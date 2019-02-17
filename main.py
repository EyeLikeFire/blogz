# - - - - - - - - - - [  B L O G  ] - - - - - - - - - - - - #
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'xy74-blogz' #this is for the cookie! ahhh

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
    name = db.Column(db.String(120), unique=True) #changed 'email' to 'name'
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password
# /\ - - - - C L A S S  A B O V E - - - - /\

# \/ - - F U N C T I O N S  B E L O W - - \/
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index']
    if request.endpoint not in allowed_routes and 'name' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

    
@app.route('/logout')
def logout():
    del session['name']
    return redirect('/')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data

        existing_user = User.query.filter_by(name=name).first()

        if len(name) < 4:
            return "<h2>User name invalid: must be at least 4 charactors long</h2>"
        elif len(password) < 4:
            return "<h2>Password invalid: must be at least 4 charactors long</h2>"

        if not existing_user:
            new_user = User(name, password)
            db.session.add(new_user)
            db.session.commit()
            session['name'] = name
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h2>That user name already exisits</h2>"

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()
        if user and user.password == password:
            session['name'] = name

            #Code that only flashes the first part of an email dog@woof.com = dog
            #So Welcome + email_user = "Welcome dog"
            user_name = ""
            for i in name:
                if i == "@":
                    break
                user_name += i

            flash("Welcome " + user_name + "!") #"Flash messages" store info directly in the session data. That way if you redirect you still have the info 
            print(session)
            return redirect('/') 
        else:
            flash("User & password combo is incorrect, or does not exist", 'nocombo')

    return render_template('login.html')


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        author = User.query.filter_by(name=session['name']).first()
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

        return redirect('/blog?id='+str(new_post.id))
    return render_template('new-post.html')

@app.route('/blog', methods=['POST', 'GET'])
def BlogIndex():

    blog_user = User.query.filter_by(name=session['name']).first()
    blogs = Blog.query.filter_by(deleted=False).all()
    users = User.query.all()
    blog_id = request.args.get('id')

    user_id = request.args.get('user_id')

    if request.method == "GET" and blog_id:
        blogs = Blog.query.filter_by(id=blog_id).first()
        user = User.query.filter_by(id=blogs.owner_id).first()
        return render_template( 'post.html', blogs=blogs, user=user )


    if request.method == "GET" and user_id:
        user = User.query.filter_by(id=user_id).first()
        blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template( 'user.html', user=user, blogs=blogs )

    #This is the ELSE statement:    
    return render_template('blog.html', blogs=blogs, users=users)


if __name__ == '__main__':
    app.run()

# THIS IS WHERE I LEFT OFF....

    # Make a Home Page
    # Now we can see a list of all blogs by all users on the /blog page, but what if a visitor to the site only wants to see the blogs for a particular author? To make that easy for the visitor, let's add a "Home" page that will live at the route / and will display a list of the usernames for all the authors on the site. Make a template called index.html that displays this list, and in main.py create a route handler function for it (named index so that it is included in the allowed routes we listed above).

    # Create Dynamic User Pages
    # Just as we created a page to dynamically display individual blog posts in Build-a-Blog, we'll create a page to dynamically display the posts of each individual user. We'll use a GET request on the /blog path with a query parameter of ?user=userId where "userId" is the integer matching the id of the user whose posts we want to feature. And we'll need to create a template for this page.

    # There are three ways that users can reach this page and they all require that we make some changes to our templates. We will need to display, as a link, the username of the author of each blog post in a tagline on the individual blog entry page and on the /blog page. Check out our demo app and see the line "Written by..." underneath the body of the blog posts.

    # If you fulfilled the second bonus mission in Build-a-Blog using a DateTime column, then you can utilize that field here to also note when each post was created, alongside the author.

# Remember that each Blog object has an owner associated with it (passed to it in the constructor), so you can access the properties of that owner (such as username, or id) with dot notation.

#^^^^^ Is this differnt then the method I used?

    # Then you'll have to amend the /blog route handler to render the correct template (either the one for the individual blog user page, or the one for the individual blog entry page) based on the arguments in the request (i.e., which name the query parameter has). If the query param is user, then you need to use the template for the individual user page and pass it a list of all the blogs associated with that user.

    # We also need to modify our index.html. For each author name listed, add a link to the author's individual blog user page.

    # Here are the relevant use cases:

    # User is on the / page ("Home" page) and clicks on an author's username in the list and lands on the individual blog user's page.
    # User is on the /blog page and clicks on the author's username in the tagline and lands on the individual blog user's page.

    # User is on the individual entry page (e.g., /blog?id=1) and clicks on the author's username in the tagline and lands on the individual blog user's page.


# Bonus Missions
# Before embarking on these bonus missions, make sure to commit and push your working code to GitHub!

# Add Pagination
# To limit the scrolling that users have to do if they visit a page with multiple blog posts on it, we'll implement pagination on our individual users page and our "all blogs" (/blog) page. The Flask-SQLAlchemy API makes this a fairly straightforward process. Review the documentation on pagination in the Utilities section and also the Models, which describes a paginate method that is part of the class flask.ext.sqlalchemy.BaseQuery.

# We recommend limiting posts to 5 per page.

# Add Hashing
# After completing the video lessons on hashing, come back to this assignment and refactor your code so that you utilize hashing instead of storing passwords directly.

# Submit
# To turn in your assignment and get credit, follow the submission instructions.