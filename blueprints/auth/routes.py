from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from . import auth_bp
from .forms import LoginForm, RegisterForm, ForgotPasswordForm

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    login_form = LoginForm()
    register_form = RegisterForm()

    if login_form.validate_on_submit():
        email = login_form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(login_form.password.data):
            flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "danger")
            return render_template("auth_double.html", login_form=login_form, register_form=register_form, mode="login")

        if not user.is_active:
            flash("บัญชีถูกปิดใช้งาน", "danger")
            return render_template("auth_double.html", login_form=login_form, register_form=register_form, mode="login")

        login_user(user)
        flash("เข้าสู่ระบบสำเร็จ", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("dashboard.index"))

    return render_template("auth_double.html", login_form=login_form, register_form=register_form, mode="login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and current_user.role != "admin":
        flash("คุณเข้าสู่ระบบอยู่แล้ว", "info")
        return redirect(url_for("dashboard.index"))

    login_form = LoginForm()
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("อีเมลนี้ถูกใช้งานแล้ว", "danger")
            return render_template("auth_double.html", login_form=login_form, register_form=form, mode="register")

        user = User(
            full_name=form.full_name.data.strip(),
            email=email,
            role="staff",
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth_double.html", login_form=login_form, register_form=form, mode="register")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash("ตัวอย่างระบบ: ถ้ามีบัญชี ระบบจะส่งลิงก์รีเซ็ตไปที่อีเมล", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ออกจากระบบแล้ว", "info")
    return redirect(url_for("auth.login"))
