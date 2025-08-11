from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

#Conexion a la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/db_blogcito"
db = SQLAlchemy(app)

#Migrates importacion
migrate = Migrate(app, db)

from models import Usuario, Post, Comentario, Categoria

@app.route("/")
def index():
   posts = Post.query.all()
   return render_template("index.html", posts=posts)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        usuario = Usuario(nombre=nombre, email=email, password=password)
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("registro.html")

@app.route("/nuevo_post", methods=["GET", "POST"])
def nuevo_post():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        usuario_id = request.form["usuario_id"]
        categoria_id = request.form["categoria_id"]
        post = Post(titulo=titulo, contenido=contenido, usuario_id=usuario_id, categoria_id=categoria_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("index"))
    usuarios = Usuario.query.all()
    categorias = Categoria.query.all()
    return render_template("nuevo_post.html", usuarios=usuarios, categorias=categorias)

@app.context_processor
def inject_categorias():
    return {"categorias": Categoria.query.all()}

@app.route("/login")
def login():
    return render_template("login.html")