from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("อีเมล", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired()])
    submit = SubmitField("เข้าสู่ระบบ")

class RegisterForm(FlaskForm):
    full_name = StringField("ชื่อ-สกุล", validators=[DataRequired(), Length(max=120)])
    email = StringField("อีเมล", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("รหัสผ่าน", validators=[DataRequired(), Length(min=4)])
    confirm = PasswordField("ยืนยันรหัสผ่าน", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("สมัครสมาชิก")

class ForgotPasswordForm(FlaskForm):
    email = StringField("อีเมล", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("ส่งลิงก์รีเซ็ต (ตัวอย่าง)")
