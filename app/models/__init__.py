# import every model here so Base.metadata knows about all tables (alembic needs this)
from app.models.users import (Address, DeactivationRequest, Permission, ProfileHistory, RefreshToken,
                              RevokedToken, Role, User, UserActivity, role_permissions)
from app.models.catalog import (Attribute, Brand, Category, PriceHistory, Product,
                                ProductAttributeValue, ProductFile, ProductVariant)
from app.models.inventory import (Inventory, RestockAlert, StockMovement, StockTransfer,
                                  ThresholdHistory, Warehouse)
from app.models.sales import (Cart, CartItem, Coupon, Order, OrderCancellation, OrderItem,
                              OrderStatusHistory, Promotion, ShippingMethod, TaxRate, WishlistItem)
from app.models.payments import CodCollection, CodSetting, Payment, PaymentEvent, Refund
from app.models.logistics import (DeliveryAssignment, DeliveryAttempt, ExchangeEvent, ExchangeRequest,
                                  ReturnItem, ReturnRequest, Shipment, ShippingProvider, TrackingEvent)
from app.models.engagement import (Answer, MessageProvider, Notification, OutboundMessage, Question,
                                   Review, Ticket, TicketMessage)
from app.models.suppliers import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierInvoice, SupplierProduct
from app.models.system import AuditLog, BackgroundJob, ConfigHistory