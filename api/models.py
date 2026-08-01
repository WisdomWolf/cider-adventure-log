import base64
from datetime import datetime
from typing import Any, Optional

from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

JSON_VARIANT = JSONB().with_variant(sqlite.JSON(), 'sqlite')


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


class Beverage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    brand: Mapped[str]
    name: Mapped[str]
    description: Mapped[Optional[str]]
    image = mapped_column(db.LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    ratings: Mapped[list["Rating"]] = db.relationship(back_populates='beverage')
    barcodes: Mapped[list["Barcode"]] = db.relationship(
        back_populates='beverage',
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "beverage",
    }

    @hybrid_property
    def average_rating(self) -> float:
        if self.ratings:
            return sum(r.score for r in self.ratings) / len(self.ratings)
        else:
            return None

    def type_details(self) -> dict:
        """Overridden by each subclass to return its own type-specific fields."""
        return {}

    def to_summary_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "brand": self.brand,
            "name": self.name,
            "barcodes": [
                {"id": barcode.id, "code": barcode.code}
                for barcode in self.barcodes
            ],
            "average_rating": self.average_rating,
        }

    def to_detail_dict(self) -> dict:
        image_base64 = None
        if self.image:
            image_base64 = base64.b64encode(self.image).decode('utf-8')

        data = self.to_summary_dict()
        data.update({
            "description": self.description,
            "image": image_base64,
            "ratings": [
                {
                    "id": r.id,
                    "score": r.score,
                    "comment": r.comment,
                    "attributes": r.attributes,
                }
                for r in self.ratings
            ],
            "details": self.type_details(),
        })
        return data


class CiderDetails(Beverage):
    id: Mapped[int] = mapped_column(db.ForeignKey('beverage.id'), primary_key=True)
    abv: Mapped[Optional[float]]
    style: Mapped[Optional[str]]

    __mapper_args__ = {"polymorphic_identity": "cider"}

    def type_details(self) -> dict:
        return {"abv": self.abv, "style": self.style}


class WhiskeyDetails(Beverage):
    id: Mapped[int] = mapped_column(db.ForeignKey('beverage.id'), primary_key=True)
    abv: Mapped[Optional[float]]
    style: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    batch_number: Mapped[Optional[str]]

    __mapper_args__ = {"polymorphic_identity": "whiskey"}

    def type_details(self) -> dict:
        return {
            "abv": self.abv,
            "style": self.style,
            "year": self.year,
            "batch_number": self.batch_number,
        }


class CoffeeDetails(Beverage):
    id: Mapped[int] = mapped_column(db.ForeignKey('beverage.id'), primary_key=True)
    origin: Mapped[Optional[str]]
    roast_level: Mapped[Optional[str]]
    process: Mapped[Optional[str]]
    varietal: Mapped[Optional[str]]

    __mapper_args__ = {"polymorphic_identity": "coffee"}

    def type_details(self) -> dict:
        return {
            "origin": self.origin,
            "roast_level": self.roast_level,
            "process": self.process,
            "varietal": self.varietal,
        }


BEVERAGE_TYPES = {
    "cider": CiderDetails,
    "whiskey": WhiskeyDetails,
    "coffee": CoffeeDetails,
}


class Barcode(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    beverage_id: Mapped[int] = mapped_column(
        db.ForeignKey('beverage.id'),
        nullable=False
    )
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    beverage: Mapped["Beverage"] = db.relationship(back_populates="barcodes")


class Rating(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    beverage_id: Mapped[int] = mapped_column(
        db.ForeignKey('beverage.id'),
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
    attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON_VARIANT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        nullable=True
    )

    beverage: Mapped["Beverage"] = db.relationship(back_populates="ratings")
    user: Mapped["User"] = db.relationship(back_populates="ratings")
