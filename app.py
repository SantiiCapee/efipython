from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/db_blogcito"
db = SQLAlchemy(app)

# Migraciones
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.secret_key = os.getenv('SECRET_KEY')

from models import Usuario, Post, Comentario, Categoria

@app.context_processor
def inject_categorias():
    categorias = Categoria.query.all()
    return dict(categorias=categorias)


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not nombre or not email or not password:
            flash('Por favor complete todos los campos.', 'danger')
            return redirect(url_for('registro'))
        
        if Usuario.query.filter_by(nombre=nombre).first():
            flash('El nombre de usuario ya existe, por favor elija otro.', 'danger')
            return redirect(url_for('registro'))

        if Usuario.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'danger')
            return redirect(url_for('registro'))
        
        password_hash = generate_password_hash(password)

        usuario = Usuario(nombre=nombre, email=email, password=password_hash)
        db.session.add(usuario)
        db.session.commit()

        session["usuario_id"] = usuario.id
        session["usuario_nombre"] = usuario.nombre

        flash(f'Bienvenido, {usuario.nombre}! Tu cuenta fue creada con éxito.', 'success')
        return redirect(url_for("index"))

    return render_template("registro.html")

@app.route("/nuevo_post", methods=["GET", "POST"])
def nuevo_post():
    if "usuario_id" not in session:
        flash("Debes iniciar sesión para crear un post.", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        categoria_id = request.form["categoria_id"]

        post = Post(titulo=titulo, contenido=contenido, usuario_id=session["usuario_id"], categoria_id=categoria_id)
        db.session.add(post)
        db.session.commit()
        flash("Post creado con éxito.", "success")
        return redirect(url_for("index"))
    return render_template("nuevo_post.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            flash(f"Bienvenido {usuario.nombre}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("index"))

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def ver_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para comentar.", "danger")
            return redirect(url_for("login"))

        texto = request.form["texto"].strip()
        if not texto:
            flash("El comentario no puede estar vacío.", "danger")
            return redirect(url_for("ver_post", post_id=post_id))

        comentario = Comentario(
            texto=texto,
            usuario_id=session["usuario_id"],
            post_id=post.id
        )
        db.session.add(comentario)
        db.session.commit()

        flash("Comentario agregado con éxito.", "success")
        return redirect(url_for("ver_post", post_id=post_id))

    return render_template("post_detalle.html", post=post)