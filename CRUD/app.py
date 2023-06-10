import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["UPLOAD_FOLDER"] = "static/images/"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
db = SQLAlchemy(app)


class MyPost(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String, nullable=False)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/")
def sayHello():
    return render_template("/main.html")


@app.route("/addpost", methods=["GET", "POST"])
def addPost():
    if request.method == "POST":
        post_title = request.form["title"]
        post_body = request.form["body"]
        post_image = None
        
        if "image" in request.files and allowed_file(request.files["image"].filename):
            image_file = request.files["image"]
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            post_image = filename
        
        setPost = MyPost(title=post_title, body=post_body, image=post_image)
        db.session.add(setPost)
        db.session.commit()
        return redirect(url_for("listPost"))
    
    return render_template("posts/add.html")


@app.route("/listpost")
def listPost():
    postDetails = MyPost.query.all()
    return render_template("posts/all.html", posts=postDetails)


@app.route("/listpost/<int:id>")
def displayPost(id):
    getPost = MyPost.query.get_or_404(id)
    return render_template("posts/view.html", myPost=getPost)


@app.route("/listpost/update/<int:id>", methods=["GET", "POST"])
def updatePost(id):
    getPost = MyPost.query.get_or_404(id)
    
    if request.method == "POST":
        getPost.title = request.form["title"]
        getPost.body = request.form["body"]
        
        if "image" in request.files and allowed_file(request.files["image"].filename):
            image_file = request.files["image"]
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            getPost.image = filename
        
        db.session.commit()
        return redirect(url_for("listPost"))
    
    return render_template("posts/update.html", setPost=getPost)


@app.route("/listpost/deletepost/<int:id>")
def deletePost(id):
    getPost = MyPost.query.get_or_404(id)
    db.session.delete(getPost)
    db.session.commit()
    return redirect(url_for("listPost"))


@app.errorhandler(404)
def pageNotFound(error):
    return "<h1> page not found </h1>"


if __name__ == "__main__":
    app.run(debug=True)