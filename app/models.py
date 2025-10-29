# app/models.py
from datetime import datetime
from flask_login import UserMixin
from passlib.hash import bcrypt_sha256
from . import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="customer", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        # use bcrypt_sha256
        self.password_hash = bcrypt_sha256.hash(password)

    def check_password(self, password: str) -> bool:
        # use bcrypt_sha256
        return bcrypt_sha256.verify(password, self.password_hash)

    def __repr__(self):
        return f"<User {self.email}>"


class ComplaintType(db.Model):
    __tablename__ = "complaint_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<ComplaintType {self.name}>"


class Area(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Area {self.name}>"


class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    complaint_type_id = db.Column(db.Integer, db.ForeignKey("complaint_types.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)
    text = db.Column(db.Text, nullable=True)                       # Description
    status = db.Column(db.String(30), default="pending", nullable=False, server_default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="complaints")
    complaint_type = db.relationship("ComplaintType", backref="complaints")
    area = db.relationship("Area", backref="complaints")

    def __repr__(self):
        return f"<Complaint {self.id} user={self.user_id} status={self.status}>"
