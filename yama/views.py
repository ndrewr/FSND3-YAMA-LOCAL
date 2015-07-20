"""
    defines the app routes
"""
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response, session as login_session
from yama import app, db, github

import json, random, string
import requests

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from models import User, Category, Item
from forms import TitleDescriptionForm


# home page aka base camp. Shows course categories AND a list of most recent added courses
@app.route('/')
@app.route('/base/')
def home():
    categories = Category.query.all()

    # 5 most recently added courses
    recent = Item.query.order_by(Item.id.desc()).limit(5)

    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state

    return render_template('index.html', categories=categories, recent_posts=recent, state=state)


# shows the user login page with third party auth options
# this page should auto-redirect to the prev page user was on
@app.route('/login/')
def loginUser():
    return 'This is the login page.'


def responseMaker(msg, code):
    response = make_response(json.dumps(msg), code)
    response.headers['Content-Type'] = 'application/json'
    return response


# handles signin from third party
@app.route('/gitconnect/', methods=['GET', 'POST'])
def githubconnect():
    return github.authorize()

    if request.args.get('state') != login_session['state']:
        return responseMaker('Invalid state', 401)


    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # check if user exists in database; if not add them
    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)
    # add the now logged-in user to session
    login_session['user_id'] = user_id


@github.access_token_getter
def gittoken():
    token = login_session.get('token')
    if token is not None:
        return token


@app.route('/git-auth-handler/')
@github.authorized_handler
def authorized(oauth_token):
    print "called by github!"
    next_url = request.args.get('next') or url_for('home')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)
    
    login_session['token'] = oauth_token
    gituser = github.get('user')
    login_session['username'] = gituser.get('name')
    login_session['user'] = User.query.filter_by(git_email=gituser.email).first()
    #login_session['current_user'] = fetchedUser
    flash("Authorized! ...now what?")
    return redirect(next_url)


@app.route('/gconnect/', methods=['GET', 'POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        return responseMaker('Invalid state', 401)

    # code = request.args.get('code')
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return responseMaker('Failed to upgrade the authorization code.', 401)

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        return responseMaker(result.get('error'), 500)

    # Verify that the access token is used for the intended
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return responseMaker("Token's user ID doesn't match given user ID.", 401)

    # Verify that the access token is valid for this client
    if result['issued_to'] != CLIENT_ID:
        return responseMaker("Token's client ID does not match app.", 401)

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return responseMaker('Current user is already connected.', 200)

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # check if user exists in database; if not add them
    user_id = getUserID(login_session['email'])
    if not user_id:
        createUser(login_session)
    # add the now logged-in user to session
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'])
    return redirect('/')


# automatically logsout the user and redirects them to home page
@app.route('/logout/')
def logoutUser():
    return 'This will be the logout page.'


# show all courses available under one subject
# logged-in users will also see an 'add' option for new courses
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/list/')
def showCourses(category_id):
    courses = Item.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    recent = Item.query.order_by(Item.id.desc()).limit(5)
    return render_template('course-list-view.html', category_id=category_id, categories=categories, courses=courses, recent_posts=recent)


# returns course list data in json
@app.route('/category/<int:category_id>/json')
@app.route('/category/<int:category_id>/list/json')
def showCoursesJSON(category_id):
    courses = Item.query.filter_by(category_id=category_id).all()
    return jsonify(CategoryCourses=[course.serialize for course in courses])


# show an interface to Add a course to current subject
@app.route('/category/<int:category_id>/add/', methods=['GET', 'POST'])
def addCourse(category_id):
    # shows a form page for adding new courses under provided categories
    # when submitted, course is displayed both in Course list AND Recent Posts list
    category = Category.query.filter_by(id=category_id).one()
    form = TitleDescriptionForm()
    if form.validate_on_submit():
        # if validation is passed add item to the db
        # must set user id based on currently logged-in user
        new_item = Item(name=form.name.data,
                url=form.url.data,
                description=form.description.data,
                category_id=category.id,
                user_id=1)
        db.session.add(new_item)
        db.session.commit()
        flash('* New course item %s successfully added to %s.' % (new_item.name, category.name))
        return redirect('/')
    if form.errors:
        flash('! There was a problem...%s' % (form.errors))
    return render_template('add-course.html', category=category, form=form)


# show additional details on the selected course;
# logged-in users will also see an 'edit' option to edit course details
@app.route('/category/<int:category_id>/<int:course_id>/')
@app.route('/category/<int:category_id>/<int:course_id>/details/')
@app.route('/details/<int:course_id>/')
def showCourse(category_id=1, course_id=1):
    course = Item.query.filter_by(id=course_id).one()
    category = Category.query.filter_by(id=course.category_id).one()
    form = TitleDescriptionForm(obj=course)
    return render_template('course-detail.html', category=category, course=course, form=form)
    # return 'This will show more details on a specific course.'


# shows an interface to edit the details of a specific course
# also has a link to delete this course from the category's course list
@app.route('/category/<int:category_id>/<int:course_id>/edit/', methods=['GET', 'POST'])
def editCourse(category_id, course_id):
    category = Category.query.filter_by(id=category_id).one()
    course = Item.query.filter_by(id=course_id).one()
    form = TitleDescriptionForm()
    if form.validate_on_submit():
        course.name = form.name.data
        course.url = form.url.data
        course.description = form.description.data
        db.session.commit()
        flash('* Course item %s edited successfully.' % (course.name))
        return redirect('/')
    elif form.errors:
        first_msg = str(form.errors[form.errors.keys()[0]][0])
        flash('! There was a problem with %s. %s' % (form.errors.keys()[0].upper(), first_msg))
    return render_template('course-detail.html', category=category, course=course, form=form)
    # return 'This will be a UX allowing users to edit OR DELETE course details'


# shows a confirmation view if user clicks 'delete'
@app.route('/category/<int:category_id>/<int:course_id>/delete/')
def deleteCourse(category_id, course_id):
    course = Item.query.filter_by(id=course_id).one()
    count = Item.query.count()
    print count
    db.session.delete(course)
    count2 = Item.query.count()
    print count2
    db.session.commit()
    # return 'Will be a confirmation screen in case DELETE was accidentally clicked'
    return redirect(url_for('showCourses', category_id=category_id))


# api endpoint to return details for a specific course in JSON format
@app.route('/category/<int:category_id>/<int:course_id>/JSON/')
def apiCourseJSON(course_id):
    return 'This will return all details for a specific course in JSON.'
