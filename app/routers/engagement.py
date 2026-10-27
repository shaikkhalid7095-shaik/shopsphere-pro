# Module 38 reviews & ratings, Module 39 product Q&A
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_customer, require_roles
from app.models import Answer, Order, OrderItem, Product, Question, Review, User
from app.roles import ADMIN, PRODUCT_MANAGER, SUPPORT_AGENT
from app.schemas.common import Page
from app.schemas.engagement import (AnswerIn, AnswerOut, ModerateIn, QAModerateIn, QuestionIn, QuestionOut,
                                    RatingSummary, ReviewIn, ReviewOut, ReviewUpdate)
from app.services.audit import log_action
from app.utils import get_or_404, paginate

router = APIRouter(tags=["38. Reviews, 39. Q&A"])
moderators = require_roles(ADMIN, SUPPORT_AGENT)

# very small bad word filter - auto hides content, staff can un-hide
BAD_WORDS = ["scam", "idiot", "stupid", "fraud"]


def looks_bad(text):
    text = (text or "").lower()
    return any(re.search(rf"\b{w}\b", text) for w in BAD_WORDS)


# ---------------- reviews ----------------
@router.post("/reviews", response_model=ReviewOut, status_code=201)
def write_review(data: ReviewIn, user: User = Depends(require_customer), db: Session = Depends(get_db)):
    get_or_404(db, Product, data.product_id, "Product")
    # verified purchase = a delivered order that contains this product
    bought = (db.query(OrderItem).join(Order)
              .filter(Order.user_id == user.id, Order.status == "delivered",
                      OrderItem.product_id == data.product_id).first())
    if not bought:
        raise HTTPException(403, "Only customers who received this product can review it")
    if db.query(Review).filter_by(product_id=data.product_id, user_id=user.id).first():
        raise HTTPException(409, "You already reviewed this product, edit your review instead")
    review = Review(product_id=data.product_id, user_id=user.id, order_id=bought.order_id, rating=data.rating,
                    title=data.title, comment=data.comment,
                    status="hidden" if looks_bad(f"{data.title} {data.comment}") else "published")
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You already reviewed this product")
    return review


@router.patch("/reviews/{review_id}", response_model=ReviewOut)
def edit_review(review_id: int, data: ReviewUpdate, user: User = Depends(require_customer),
                db: Session = Depends(get_db)):
    r = get_or_404(db, Review, review_id, "Review")
    if r.user_id != user.id:
        raise HTTPException(404, "Review not found")
    if r.status == "removed":
        raise HTTPException(400, "Removed reviews can't be edited")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    if looks_bad(f"{r.title} {r.comment}"):
        r.status = "hidden"
    db.commit()
    return r


@router.get("/products/{product_id}/reviews", response_model=Page[ReviewOut])
def product_reviews(product_id: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    q = db.query(Review).filter_by(product_id=product_id, status="published").order_by(Review.id.desc())
    return paginate(q, page, size)


@router.get("/products/{product_id}/rating", response_model=RatingSummary)
def rating_summary(product_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Product, product_id, "Product")
    rows = (db.query(Review.rating, func.count(Review.id))
            .filter_by(product_id=product_id, status="published").group_by(Review.rating).all())
    breakdown = {i: 0 for i in range(1, 6)}
    for rating, count in rows:
        breakdown[rating] = count
    total = sum(breakdown.values())
    avg = round(sum(k * v for k, v in breakdown.items()) / total, 2) if total else None
    return RatingSummary(product_id=product_id, average=avg, count=total, breakdown=breakdown)


@router.get("/reviews/moderation", response_model=Page[ReviewOut])
def moderation_queue(status: str = "hidden", page: int = 1, size: int = 20, db: Session = Depends(get_db),
                     _=Depends(moderators)):
    return paginate(db.query(Review).filter_by(status=status).order_by(Review.id.desc()), page, size)


@router.put("/reviews/{review_id}/moderate", response_model=ReviewOut)
def moderate_review(review_id: int, data: ModerateIn, db: Session = Depends(get_db), me: User = Depends(moderators)):
    r = get_or_404(db, Review, review_id, "Review")
    old = r.status
    r.status = data.status
    r.moderated_by = me.id
    log_action(db, me.id, "review.moderate", "review", r.id, {"status": old}, {"status": data.status})
    db.commit()
    return r


# ---------------- Q&A ----------------
@router.post("/questions", response_model=QuestionOut, status_code=201)
def ask_question(data: QuestionIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_or_404(db, Product, data.product_id, "Product")
    q = Question(product_id=data.product_id, user_id=user.id, text=data.text,
                 status="hidden" if looks_bad(data.text) else "open")
    db.add(q)
    db.commit()
    return q


@router.get("/products/{product_id}/questions", response_model=Page[QuestionOut])
def product_questions(product_id: int, status: Optional[str] = None, page: int = 1, size: int = 20,
                      db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.product_id == product_id)
    if status:
        q = q.filter(Question.status == status)
    else:
        q = q.filter(Question.status != "hidden")
    result = paginate(q.order_by(Question.id.desc()), page, size)
    # don't leak hidden answers to the public
    items = []
    for question in result["items"]:
        out = QuestionOut.model_validate(question)
        out.answers = [a for a in out.answers if a.status == "visible"]
        items.append(out)
    result["items"] = items
    return result


@router.post("/questions/{question_id}/answers", response_model=QuestionOut, status_code=201)
def answer_question(question_id: int, data: AnswerIn, db: Session = Depends(get_db),
                    me: User = Depends(require_roles(ADMIN, SUPPORT_AGENT, PRODUCT_MANAGER))):
    q = get_or_404(db, Question, question_id, "Question")
    if q.status == "hidden":
        raise HTTPException(400, "Question is hidden")
    q.answers.append(Answer(user_id=me.id, text=data.text))
    q.status = "answered"
    db.commit()
    db.refresh(q)
    return q


@router.put("/questions/{question_id}/moderate", response_model=QuestionOut)
def moderate_question(question_id: int, data: QAModerateIn, db: Session = Depends(get_db),
                      me: User = Depends(moderators)):
    q = get_or_404(db, Question, question_id, "Question")
    q.status = "hidden" if data.hide else ("answered" if q.answers else "open")
    db.commit()
    return q


@router.put("/answers/{answer_id}/moderate", response_model=AnswerOut)
def moderate_answer(answer_id: int, data: QAModerateIn, db: Session = Depends(get_db),
                    me: User = Depends(moderators)):
    a = get_or_404(db, Answer, answer_id, "Answer")
    a.status = "hidden" if data.hide else "visible"
    db.commit()
    return a