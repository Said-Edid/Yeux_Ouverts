from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


# WTForm rendered in contact.html
class ContactForm(FlaskForm):
    name = StringField(label="Nombre", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    phone = StringField(label="Teléfono", validators=[DataRequired()])
    message = CKEditorField("Mensaje", validators=[DataRequired()])
    submit = SubmitField("Enviar Mensaje")


# WTForm rendered in register.html
class RegisterForm(FlaskForm):
    name = StringField(label="", validators=[DataRequired()])
    email = EmailField(label="", validators=[DataRequired()])
    password = PasswordField(label="", validators=[DataRequired()])
    submit = SubmitField("Registrarme")


# WTForm rendered in login.html
class LoginForm(FlaskForm):
    email = EmailField(label="", validators=[DataRequired()])
    password = PasswordField(label="", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")


# WTForm rendered in add-product.html
class ProductForm(FlaskForm):
    description = StringField(label="Descripción del Producto", validators=[DataRequired()])
    price = StringField(label="Precio, ej. 500", validators=[DataRequired()])
    img_url_one = StringField(label="Imagen 1", validators=[DataRequired()])
    img_url_two = StringField(label="Imagen 2 (opcional)")
    img_url_three = StringField(label="Imagen 3 (opcional)")
    sizes = StringField(label="Tallas ejemplo: Ch, M, G", validators=[DataRequired()])
    materials = StringField(label="Materiales ejemplo: Algodón, Poliéster", validators=[DataRequired()])
    colors = StringField(label="Colores disponibles", validators=[DataRequired()])
    other = StringField(label="Otras características (opcional)")
    submit = SubmitField("Agregar Producto")
