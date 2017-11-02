"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                    session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/display_user/<userid>")
def display_user(userid):
    """Displays info about the selected user"""

    # get user information from database by user_id (clicked on page)
    get_user = User.query.filter_by(user_id=int(userid)).first()
    user_id = int(userid)
    # Get the list of movies and scores for each rating that user rated
    movie_info = (db.session.query(User, Rating, Movie)
                 .join(Rating)
                 .join(Movie)
                 .filter_by(user_id=user_id).all())

    print movie_info

    return render_template("user_info.html", get_user=get_user)


@app.route("/register", methods=["GET"])
def user_registration():
    """Send user to registration_form"""
    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def register_process():

    email = request.form.get("frm_email")
    password = request.form.get("frm_password")

# At the registration page, check if the email and password entered,
# already exists in the database (by querying the database)
    check_email = User.query.filter_by(email=email).count()
    # import pdb; pdb.set_trace()

    if check_email == 0:
        new_user = User(email=email, password=password)
        # Adding new user to the database and commit
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    else:
        flash("You have an account. Please login")
        return redirect('/login')


@app.route('/login', methods=["GET"])
def login():
    """Go to Login page"""

    return render_template("login_page.html")


@app.route('/login', methods=["POST"])
def validate_login():
    """Validates User login information"""

    email = request.form.get("frm_email")
    password = request.form.get("frm_password")

# Could use .one() or .first().
# .one() - would give an error if email and password does not exist
#.first() - would return 'None' if the email and password does not exist
    check_user = User.query.filter_by(email=email, password=password).all()
    # user_id = str(check_user[0].user_id)

# If the password is incorrect (checking if check_user is None)
    if check_user == []:
        return redirect('/login')
    else:
        #If user exists, add user_id to the sesssion.
        flash("You were successfully logged in")
        session["user_id"] = check_user[0].user_id
        user_id = session["user_id"]
        return redirect("/display_user/"+str(user_id))


@app.route('/logout')
def logout_user():

    del session["user_id"]
    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
