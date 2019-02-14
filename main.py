# - - - - - - - - - - [  B L O G  ] - - - - - - - - - - - - #
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'xy74-blog' #this is for the cookie! ahhh

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.Text)
    deleted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.deleted = False
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password
# /\ - - - - C L A S S  A B O V E - - - - /\

# \/ - - F U N C T I O N S  B E L O W - - \/
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/home')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/home')
        else:
            # TODO - user better response messaging
            return "<h2>That email already exisits</h2>"

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email

            #Code that only flashes the first part of an email dog@woof.com = dog
            #So Welcome + email_user = "Welcome dog"
            email_user = ""
            for i in email:
                if i == "@":
                    break
                email_user += i

            flash("Welcome " + email_user + "!") #"Flash messages" store info directly in the session data. That way if you redirect you still have the info 
            print(session)
            return redirect('/home') 
        else:
            flash("User & password combo is incorrect, or does not exist", 'nocombo')

    return render_template('login.html')


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        author = User.query.filter_by(email=session['email']).first()
        title = request.form['title']
        content = request.form['body']

        if request.form['title'] == "":
            if request.form['body'] == "":
                return render_template('new-post.html', error_1="Please enter a title",  error_2="This feild cannot be empty", body=content, title=title)
            return render_template('new-post.html', error_1="Please enter a title", error_2="", body=content)
        if request.form['body'] == "":
            if request.form['body'] == "":
                return render_template('new-post.html', error_1="Please enter a title",  error_2="This feild cannot be empty", body=content, title=title)
            return render_template('new-post.html', error_2="This feild cannot be empty", error_1="", title=title)

        new_post = Blog(title,content,author)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/home?id='+str(new_post.id))
    return render_template('new-post.html')

@app.route('/home', methods=['POST', 'GET'])
def BlogIndex():

    blog_user = User.query.filter_by(email=session['email']).first()
    blogs = Blog.query.filter_by(deleted=False).all()
    blog_id = request.args.get('id')

    if request.method == "GET" and blog_id:
        blogs = Blog.query.filter_by(id=blog_id).first()
        return render_template('post.html', blogs=blogs)
    return render_template('home.html', blogs=blogs)



if __name__ == '__main__':
    app.run()