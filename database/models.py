import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    DEVELOPER = "developer"

class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True) # ဖုန်းနံပါတ်သိမ်းရန်
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_banned: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

class DiamondPackage(Base):
    __tablename__ = "diamond_packages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    diamond_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    price_mmk: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="package")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    package_id: Mapped[int] = mapped_column(ForeignKey("diamond_packages.id"), nullable=False)
    
    mlbb_user_id: Mapped[str] = mapped_column(String(32), nullable=False)
    mlbb_zone_id: Mapped[str] = mapped_column(String(16), nullable=False)
    
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    slip_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, index=True)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # ဤနေရာကို nullable=True သတ်မှတ်ပေးပါ
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    package: Mapped["DiamondPackage"] = relationship("DiamondPackage", back_populates="orders")