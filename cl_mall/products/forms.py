from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators, DecimalField


def validate_images_only(Form, field):
    if field.data:
        if not field.data.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            raise validators.ValidationError('Only image files are allowed.')


class Addproducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    price = DecimalField('Price', [validators.DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('Stock', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    colors = TextAreaField('colors', [validators.DataRequired()])
    
    image_1 = FileField('Image_1', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), validate_images_only])
    image_2 = FileField('Image_2', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), validate_images_only])
    image_3 = FileField('Image_3', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg']), validate_images_only])
