from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums
class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class StockAdjustmentType(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    CORRECTION = "correction"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    full_name: str = Field(max_length=100)
    email: str = Field(max_length=255, unique=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sales: List["Sale"] = Relationship(back_populates="user")
    stock_adjustments: List["StockAdjustment"] = Relationship(back_populates="user")


class Customer(SQLModel, table=True):
    __tablename__ = "customers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    address: str = Field(max_length=500)
    ktp_number: str = Field(max_length=20, unique=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sales: List["Sale"] = Relationship(back_populates="customer")


class Warehouse(SQLModel, table=True):
    __tablename__ = "warehouses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    location: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stocks: List["Stock"] = Relationship(back_populates="warehouse")
    sale_items: List["SaleItem"] = Relationship(back_populates="warehouse")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: str = Field(max_length=50, unique=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    purchase_price: Decimal = Field(decimal_places=2, default=Decimal("0"))
    selling_price: Decimal = Field(decimal_places=2, default=Decimal("0"))
    unit: str = Field(max_length=20, default="pcs")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="products")
    stocks: List["Stock"] = Relationship(back_populates="product")
    sale_items: List["SaleItem"] = Relationship(back_populates="product")


class Stock(SQLModel, table=True):
    __tablename__ = "stocks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    warehouse_id: int = Field(foreign_key="warehouses.id")
    quantity: int = Field(default=0)
    minimum_stock: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: "Product" = Relationship(back_populates="stocks")
    warehouse: "Warehouse" = Relationship(back_populates="stocks")
    adjustments: List["StockAdjustment"] = Relationship(back_populates="stock")


class Sale(SQLModel, table=True):
    __tablename__ = "sales"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(max_length=20, unique=True)
    customer_id: int = Field(foreign_key="customers.id")
    user_id: int = Field(foreign_key="users.id")
    sale_date: datetime = Field(default_factory=datetime.utcnow)
    subtotal: Decimal = Field(decimal_places=2, default=Decimal("0"))
    discount_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))
    discount_amount: Decimal = Field(decimal_places=2, default=Decimal("0"))
    tax_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))
    tax_amount: Decimal = Field(decimal_places=2, default=Decimal("0"))
    total_amount: Decimal = Field(decimal_places=2, default=Decimal("0"))
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH)
    payment_status: str = Field(max_length=20, default="completed")
    notes: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: "Customer" = Relationship(back_populates="sales")
    user: "User" = Relationship(back_populates="sales")
    items: List["SaleItem"] = Relationship(back_populates="sale")


class SaleItem(SQLModel, table=True):
    __tablename__ = "sale_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    product_id: int = Field(foreign_key="products.id")
    warehouse_id: int = Field(foreign_key="warehouses.id")
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))
    discount_amount: Decimal = Field(decimal_places=2, default=Decimal("0"))
    total_amount: Decimal = Field(decimal_places=2, default=Decimal("0"))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sale: "Sale" = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="sale_items")
    warehouse: "Warehouse" = Relationship(back_populates="sale_items")


class StockAdjustment(SQLModel, table=True):
    __tablename__ = "stock_adjustments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stocks.id")
    user_id: int = Field(foreign_key="users.id")
    adjustment_type: StockAdjustmentType
    quantity_change: int
    previous_quantity: int
    new_quantity: int
    reason: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    adjustment_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stock: "Stock" = Relationship(back_populates="adjustments")
    user: "User" = Relationship(back_populates="stock_adjustments")


# Non-persistent schemas (for validation, forms, API requests/responses)
class CustomerCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    address: str = Field(max_length=500)
    ktp_number: str = Field(max_length=20)
    phone: Optional[str] = Field(default=None, max_length=20)


class CustomerUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=500)
    ktp_number: Optional[str] = Field(default=None, max_length=20)
    phone: Optional[str] = Field(default=None, max_length=20)


class ProductCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: str = Field(max_length=50)
    category_id: Optional[int] = Field(default=None)
    purchase_price: Decimal = Field(decimal_places=2)
    selling_price: Decimal = Field(decimal_places=2)
    unit: str = Field(max_length=20, default="pcs")


class ProductUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sku: Optional[str] = Field(default=None, max_length=50)
    category_id: Optional[int] = Field(default=None)
    purchase_price: Optional[Decimal] = Field(default=None, decimal_places=2)
    selling_price: Optional[Decimal] = Field(default=None, decimal_places=2)
    unit: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)


class WarehouseCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    location: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class WarehouseUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class StockCreate(SQLModel, table=False):
    product_id: int
    warehouse_id: int
    quantity: int = Field(default=0)
    minimum_stock: int = Field(default=0)


class StockUpdate(SQLModel, table=False):
    quantity: Optional[int] = Field(default=None)
    minimum_stock: Optional[int] = Field(default=None)


class StockAdjustmentCreate(SQLModel, table=False):
    stock_id: int
    adjustment_type: StockAdjustmentType
    quantity_change: int
    reason: str = Field(max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)


class SaleItemCreate(SQLModel, table=False):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(decimal_places=2, gt=0)
    discount_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))


class SaleCreate(SQLModel, table=False):
    customer_id: int
    items: List[SaleItemCreate]
    discount_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))
    tax_percentage: Decimal = Field(decimal_places=2, default=Decimal("0"))
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH)
    notes: Optional[str] = Field(default=None, max_length=1000)


class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    full_name: str = Field(max_length=100)
    email: str = Field(max_length=255)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    full_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = Field(default=None)


# Monthly report schemas
class MonthlySalesReport(SQLModel, table=False):
    month: int
    year: int
    total_sales: Decimal
    total_transactions: int
    top_selling_items: List[Dict[str, Any]]
    sales_by_warehouse: List[Dict[str, Any]]
    sales_by_employee: List[Dict[str, Any]]
    generated_at: datetime


class TopSellingItem(SQLModel, table=False):
    product_id: int
    product_name: str
    total_quantity: int
    total_revenue: Decimal


class SalesByWarehouse(SQLModel, table=False):
    warehouse_id: int
    warehouse_name: str
    total_sales: Decimal
    transaction_count: int


class SalesByEmployee(SQLModel, table=False):
    user_id: int
    employee_name: str
    total_sales: Decimal
    transaction_count: int
