SUPER_ADMIN = "super_admin"
ADMIN = "admin"
PRODUCT_MANAGER = "product_manager"
INVENTORY_MANAGER = "inventory_manager"
ORDER_MANAGER = "order_manager"
SUPPORT_AGENT = "support_agent"
CUSTOMER = "customer"
DELIVERY_MANAGER = "delivery_manager"
FINANCE_MANAGER = "finance_manager"

ALL_ROLES = [
    SUPER_ADMIN, ADMIN, PRODUCT_MANAGER, INVENTORY_MANAGER, ORDER_MANAGER,
    SUPPORT_AGENT, CUSTOMER, DELIVERY_MANAGER, FINANCE_MANAGER,
]
STAFF_ROLES = [r for r in ALL_ROLES if r != CUSTOMER]

# default permissions given to each role (seeded, can be changed by admin)
ROLE_PERMISSIONS = {
    SUPER_ADMIN: ["*"],
    ADMIN: ["users.manage", "products.manage", "orders.manage", "reports.view", "audit.view"],
    PRODUCT_MANAGER: ["products.manage", "pricing.manage", "categories.manage"],
    INVENTORY_MANAGER: ["inventory.manage", "warehouses.manage", "purchase_orders.manage"],
    ORDER_MANAGER: ["orders.manage", "returns.manage", "shipments.manage"],
    SUPPORT_AGENT: ["tickets.manage", "reviews.moderate"],
    CUSTOMER: ["shop"],
    DELIVERY_MANAGER: ["shipments.manage", "deliveries.manage"],
    FINANCE_MANAGER: ["payments.view", "refunds.manage", "invoices.manage", "reports.view"],
}