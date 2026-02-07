from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class TicketForm(FlaskForm):
    asset_id = SelectField("ครุภัณฑ์", coerce=int, validators=[DataRequired()])
    description = TextAreaField("อาการเสีย", validators=[DataRequired()])
    submit = SubmitField("ยืนยันแจ้งซ่อม")
