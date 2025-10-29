# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required
from passlib.hash import bcrypt
import os
import csv

bp = Blueprint("auth", __name__)

# ---------------------------
# CSV Setup for Users
# ---------------------------
LOCAL_DATA_DIR = r"D:\Project\complaint-analyzer\data"
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
USERS_CSV_PATH = os.path.join(LOCAL_DATA_DIR, "users.csv")

def save_all_users_to_csv():
    users = User.query.order_by(User.id).all()
    fieldnames = ["id", "username", "email", "phone", "role", "created_at"]
    with open(USERS_CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in users:
            writer.writerow({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "phone": u.phone,
                "role": u.role,
                "created_at": u.created_at
            })

# ---------------------------
# Register Route
# ---------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")  # default: customer

        # Prevent duplicate email
        if User.query.filter_by(email=email).first():
            flash("⚠️ Email already registered!", "error")
            return redirect(url_for("auth.register"))

        try:
            user = User(username=username, email=email, phone=phone, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # --- Save all users to CSV ---
            save_all_users_to_csv()

            flash("✅ Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Registration failed: {e}", "error")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


# ---------------------------
# Login Route
# ---------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("❌ Email not found. Please register first.", "error")
            return redirect(url_for("auth.login"))

        if not user.check_password(password):
            flash("⚠️ Invalid password. Try again.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(f"👋 Welcome {user.username}!", "success")

        # Redirect based on role
        if user.role == "admin":
            return redirect(url_for("complaints.dashboard"))
        else:
            return redirect(url_for("complaints.submit"))

    return render_template("login.html")


# ---------------------------
# Logout Route
# ---------------------------
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("👋 Logged out successfully.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------
# Index Route
# ---------------------------
@bp.route("/")
def index():
    return render_template("index.html")
