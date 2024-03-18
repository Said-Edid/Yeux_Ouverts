from forms import ContactForm, RegisterForm, LoginForm, ProductForm
from flask import Flask, render_template, request, abort, redirect, url_for, flash, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import smtplib
import bleach
import os

# SMTP credentials
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("APP_PSS")

# Used for Copyright statement
current_year = datetime.now().strftime("%Y")

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)

# Flask-Login for session status management
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Create Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', 'sqlite:///yeuxouverts.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Configure Tables in Database
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)


class Product(db.Model):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[str] = mapped_column(String, nullable=False)
    img_url_one: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    img_url_two: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    img_url_three: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    sizes: Mapped[str] = mapped_column(String, nullable=False)
    materials: Mapped[str] = mapped_column(String, nullable=False)
    colors: Mapped[str] = mapped_column(String, nullable=False)
    other: Mapped[str] = mapped_column(String, nullable=True)


class Contact(db.Model):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)


with app.app_context():
    db.create_all()


# Admin only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorated_function


@app.route("/")
def get_home():
    all_products = db.session.execute(db.select(Product)).scalars()
    return render_template("index.html", year=current_year, album=all_products)


@app.route("/contact", methods=["POST", "GET"])
def get_contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        message = f"""Subject:Nuevo Mensaje de yeux-ouverts.com 👁️\n\n
        Nombre: {contact_form.name.data}\n
        Email: {contact_form.email.data}\n
        Teléfono: {contact_form.phone.data}\n
        Mensaje: {contact_form.message.data}"""
        with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465) as connection:
            # connection.starttls()
            connection.login(user=EMAIL, password=PASSWORD)
            connection.sendmail(
                from_addr=EMAIL,
                to_addrs=EMAIL,
                msg=bleach.clean(message, strip=True).encode('utf-8')
            )
        confirmation = "Mensaje enviado con éxito."
        return render_template("contact.html", confirmation=confirmation, form=contact_form)
    return render_template("contact.html", form=contact_form, year=current_year)


@app.route('/product')
def show_product():
    product_id = int(request.args.get('id'))
    product = db.session.execute(db.select(Product).where(Product.id == product_id)).scalar()
    filepaths = [product.img_url_one, product.img_url_two, product.img_url_three]
    return render_template('product.html', product=product, files=filepaths)


@app.route('/login', methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_email = login_form.email.data
        user_pss = login_form.password.data
        user = db.session.execute(db.select(User).where(User.email == user_email)).scalar()
        if not user:
            flash(f"La cuenta {user_email} no está en la base de datos, intenta de nuevo.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, user_pss):
            flash("La contraseña no es correcta.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_home'))
    return render_template('login.html', form=login_form)


@app.route('/logout', methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for('get_home'))


@app.route('/registro', methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user_email = register_form.email.data
        user = db.session.execute(db.select(User).where(User.email == user_email)).scalar()
        if user:
            flash(f"Ya te has registrado con {user_email}, por favor inicia sesión")
            return redirect(url_for('login'))
        else:
            new_user = User(
                name=register_form.name.data,
                email=user_email,
                password=generate_password_hash(register_form.password.data, "pbkdf2:sha256", 8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_home'))
    return render_template('register.html', form=register_form)


@app.route('/add-product', methods=["POST", "GET"])
@admin_only
def add_product():
    product_form = ProductForm()
    if product_form.validate_on_submit():
        new_product = Product(
            description=product_form.description.data,
            price=product_form.price.data,
            img_url_one=product_form.img_url_one.data,
            img_url_two=product_form.img_url_two.data,
            img_url_three=product_form.img_url_three.data,
            sizes=product_form.sizes.data,
            materials=product_form.materials.data,
            colors=product_form.colors.data,
            other=product_form.other.data,
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('get_home'))
    return render_template('add-product.html', form=product_form)


@app.route('/edit-product/<int:product_id>', methods=["POST", "GET"])
@admin_only
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)
    edit_form = ProductForm(
        description=product.description,
        price=product.price,
        img_url_one=product.img_url_one,
        img_url_two=product.img_url_two,
        img_url_three=product.img_url_three,
        sizes=product.sizes,
        materials=product.materials,
        colors=product.colors,
        other=product.other,
    )
    if edit_form.validate_on_submit():
        product.description = edit_form.description.data
        product.img_url_one = edit_form.img_url_one.data
        product.img_url_two = edit_form.img_url_two.data
        product.img_url_three = edit_form.img_url_three.data
        product.sizes = edit_form.sizes.data
        product.materials = edit_form.materials.data
        product.colors = edit_form.colors.data
        product.other = edit_form.other.data
        db.session.commit()
        return redirect(url_for('get_home'))
    return render_template('add-product.html', form=edit_form, is_edit=True)


@app.route('/delete/<int:product_id>', methods=["GET"])
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('get_home'))


@app.route('/policies')
def show_document():
    document = request.args.get('doc')
    if document == 'privacy':
        path = 'assets/privacidad.pdf'
        return send_from_directory('static', path)
    elif document == 'shipping':
        path = 'assets/envio.pdf'
        return send_from_directory('static', path)


if __name__ == "__main__":
    app.run(debug=False)
