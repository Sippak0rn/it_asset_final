from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import DataRequired


class CheckoutForm(FlaskForm):

    asset_id = SelectField(
        "ครุภัณฑ์",
        coerce=int,
        validators=[DataRequired()]
    )

    due_date = DateField(
        "กำหนดวันคืน",
        validators=[DataRequired()],
        format="%Y-%m-%d"
    )

    submit = SubmitField("ยืนยันขอเบิก")
