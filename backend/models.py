from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Flavor(Base):
    __tablename__ = "flavors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_flavors_price_positive"),
        CheckConstraint(
            "length(btrim(name)) BETWEEN 1 AND 100",
            name="ck_flavors_name_length",
        ),
        CheckConstraint(
            "length(btrim(description)) BETWEEN 1 AND 1000",
            name="ck_flavors_description_length",
        ),
        Index("uq_flavors_name_lower", func.lower(name), unique=True),
    )

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="customer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'admin')",
            name="ck_users_role_valid",
        ),
        Index("uq_users_email_lower", func.lower(email), unique=True),
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    flavor_id: Mapped[int] = mapped_column(ForeignKey("flavors.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flavor = relationship("Flavor")

    __table_args__ = (
        CheckConstraint("quantity >= 1"),
        CheckConstraint(
            "quantity <= 100",
            name="ck_cart_items_quantity_max",
        ),
        UniqueConstraint("user_id", "flavor_id", name="uq_cart_item_user_flavor"),
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    items = relationship(
        "OrderItem",
        order_by="OrderItem.id",
    )

    __table_args__ = (
        CheckConstraint(
            "total_price > 0",
            name="ck_orders_total_price_positive",
        ),
        Index(
            "ix_orders_user_created_at_id",
            "user_id",
            "created_at",
            "id"
        ),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    flavor_id: Mapped[int] = mapped_column(ForeignKey("flavors.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        CheckConstraint("quantity >= 1"),
        CheckConstraint(
            "quantity <= 100",
            name="ck_order_items_quantity_max",
        ),
        CheckConstraint(
            "price_at_purchase > 0",
            name="ck_order_items_price_positive",
        ),
        Index(
            "ix_order_items_order_id",
            "order_id",
        ),
    )
