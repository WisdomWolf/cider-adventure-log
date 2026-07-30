from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    display_name: Mapped[Optional[str]]
    password_hash: Mapped[Optional[str]]
    authentik_sub: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    ratings: Mapped[list["Rating"]] = db.relationship(back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)


class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str]
    flavor: Mapped[str]
    description: Mapped[Optional[str]]
    image = mapped_column(db.LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    ratings: Mapped[list["Rating"]] = db.relationship(back_populates='product')
    barcodes: Mapped[list["Barcode"]] = db.relationship(
        back_populates='product',
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def average_rating(self) -> float:
        if self.ratings:
            return sum(r.score for r in self.ratings) / len(self.ratings)
        else:
            return None


class Barcode(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey('product.id'),
        nullable=False
    )
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    product: Mapped["Product"] = db.relationship(back_populates="barcodes")


class Rating(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey('product.id'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey('user.id'),
        nullable=False
    )
    score: Mapped[int]
    comment: Mapped[Optional[str]]
    purchase_location: Mapped[Optional[str]]
    consumption_location: Mapped[Optional[str]]
    consumption_method: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    product: Mapped["Product"] = db.relationship(back_populates="ratings")
    user: Mapped["User"] = db.relationship(back_populates="ratings")
