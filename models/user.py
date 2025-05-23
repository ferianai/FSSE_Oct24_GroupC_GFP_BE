from instance.database import db
from datetime import datetime
from shared import crono
from models.product import Products as Product
import enum
from decimal import Decimal


class RoleType(enum.Enum):
    customer = "customer"
    vendor = "vendor"
    admin = "admin"


class Users(db.Model):
    """User model for the application."""

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=True)
    first_name: str = db.Column(db.String(80), nullable=False)
    last_name: str = db.Column(db.String(80), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    phone: str = db.Column(db.String(20), unique=True, nullable=True)  # true
    password_hash: str = db.Column(db.String(512), nullable=False)
    date_of_birth: str = db.Column(db.String(10), nullable=True)  # true
    address: str = db.Column(db.String(255), nullable=True)  # true
    city: str = db.Column(db.String(80), nullable=False)
    state: str = db.Column(db.String(80), nullable=True)  # true
    country: str = db.Column(db.String(80), nullable=True)  # true
    zip_code: str = db.Column(db.String(20), nullable=True)  # true
    image_url: str = db.Column(db.String(255), nullable=True)  # true
    role: str = db.Column(db.Enum(RoleType), nullable=True)
    bank_account: str = db.Column(db.String(20), nullable=True)  # true
    bank_name: str = db.Column(db.String(80), nullable=True)  # true
    account_number: str = db.Column(db.String(20), nullable=True)  # true
    balance: Decimal = db.Column(
        db.Numeric(precision=10, scale=2), default=Decimal("0.00")
    )

    is_active: bool = db.Column(db.Boolean, default=True)
    created_at: datetime = db.Column(db.DateTime, default=crono.now)
    updated_at: datetime = db.Column(db.DateTime, default=crono.now, onupdate=crono.now)

    # Relationships
    products = db.relationship("Products", back_populates="vendor", lazy=True)
    categories = db.relationship("Categories", backref="owner", lazy=True)
    cart = db.relationship("Cart", uselist=False, backref="user")
    orders = db.relationship("Orders", back_populates="user", lazy=True)
    feedback = db.relationship("Feedbacks", back_populates="user", lazy=True)
    wishlist_items = db.relationship(
        "WishlistItems", backref="user", lazy=True, foreign_keys="WishlistItems.user_id"
    )

    def __repr__(self):
        return f"<User {self.username}>"
