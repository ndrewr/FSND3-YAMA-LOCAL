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

    login_session['prev_url'] = '/'

    return render_template('index.html', categories=categories, recent_posts=recent, state=getState())


# helper that sets session state value and returns for page render
def getState():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


# handles signin from third party
# this page should auto-redirect to the prev page user was on?
@app.route('/login')
def loginUser():
    if request.args.get('state') != login_session['state']:
        flash('Hey what state are you in? Redirected.')
        return redirect('/')
    if 'user_name' in login_session:
        flash('User is already logged in.')
        return redirect('/')
    # if no current user go ahead and kick off authorization
    return github.authorize()


# mandatory; used by Github-Flask when making requests to github
@github.access_token_getter
def gittoken():
    token = login_session.get('token')
    if token is not None:
        return token


@app.route('/authhandler')
@github.authorized_handler
def authorized(oauth_token):
    # next_url = request.args.get('next') or url_for('home')
    next_url = login_session['prev_url'] or url_for('home')
    print 'going to %s' % (next_url)
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    # add token to session required for Flask-Github token getter implmtation
    login_session['token'] = oauth_token
    gituser = github.get('user')

    user_email = gituser['email']
    user_name = gituser['name']
    user_avatar_link = gituser['avatar_url']
    login_session['user_name'] = user_name

    # check if this User is registered in the db...
    fetchedUser = User.query.filter_by(email=user_email).first()
    if fetchedUser is None:
        # create a new User in the db with these login credentials
        current_user = User(username=user_name,
                email=user_email,
                picture=user_avatar_link)
        db.session.add(current_user)
        db.session.commit()
        login_session['user_id'] = current_user.id
    else:
        # otherwise set session with this user's data
        login_session['user_id'] = fetchedUser.id

    flash("Authorized! Access granted to User %s." % (user_name))
    return redirect(next_url)


# logsout the user and redirects them to home page
@app.route('/logout/')
def logoutUser():
    # Reset the user's session data
    if 'user_name' in login_session:
        del login_session['user_name']
        del login_session['user_id']
        del login_session['token']

    flash('Logged out!')
    return redirect(login_session['prev_url'])


# convenience method to get User ID info
def getUserID():
    fetchedID = 0  # this should never show up since Add Course is login only
    if 'user_id' in login_session:
        fetchedID = login_session['user_id']
    return fetchedID


# show all courses available under one subject
# logged-in users will also see an 'add' option for new courses
# NOTE must set state here too; this route is like a second index.html,
# hit when User goes from Course-Detail view back to Course-List view
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/list/')
def showCourses(category_id):
    courses = Item.query.filter_by(category_id=category_id).all()
    categories = Category.query.all()
    recent = Item.query.order_by(Item.id.desc()).limit(5)

    login_session['prev_url'] = request.path
    return render_template('course-list-view.html', category_id=category_id,
                            categories=categories, courses=courses,
                            recent_posts=recent, state=getState())


# returns course list data in json
@app.route('/category/<int:category_id>/json')
@app.route('/category/<int:category_id>/list/json')
def showCoursesJSON(category_id):
    courses = Item.query.filter_by(category_id=category_id).all()
    return jsonify(CategoryCourses=[course.serialize for course in courses])


# show an interface to Add a course to current subject
@app.route('/category/<int:category_id>/add/', methods=['GET', 'POST'])
def addCourse(category_id):
    # check if user is logged in
    if 'user_name' not in login_session:
        flash('Hey, ya gotta log in first.')
        return redirect('/')
    # submitted course is displayed both in Course list AND Recent Posts list
    category = Category.query.filter_by(id=category_id).one()
    form = TitleDescriptionForm()
    if form.validate_on_submit():
        # if validation is passed add item to the db
        # must set user id based on currently logged-in user
        new_item = Item(name=form.name.data,
                url=form.url.data,
                description=form.description.data,
                category_id=category.id,
                user_id=getUserID())
        db.session.add(new_item)
        db.session.commit()
        flash('* New course item %s successfully added to %s.' %
            (new_item.name, category.name))
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

    login_session['prev_url'] = request.path

    return render_template('course-detail.html', category=category,
                            course=course, form=form, state=getState())


# shows an interface to edit the details of a specific course
# also has a link to delete this course from the category's course list
# NOTE using Flask-WTF forms module
@app.route('/category/<int:category_id>/<int:course_id>/edit/', methods=['GET', 'POST'])
def editCourse(category_id, course_id):
    category = Category.query.filter_by(id=category_id).one()
    course = Item.query.filter_by(id=course_id).one()
    form = TitleDescriptionForm()
    #NOTE validate_on_submit also checks if 'POST'
    if form.validate_on_submit():
        course.name = form.name.data
        course.url = form.url.data
        course.description = form.description.data
        db.session.commit()
        flash('* Course item %s edited successfully.' % (course.name))
        return redirect('/')
    elif form.errors:
        first_msg = str(form.errors[form.errors.keys()[0]][0])
        flash('! There was a problem with %s. %s' %
            (form.errors.keys()[0].upper(), first_msg))
    return render_template('course-detail.html', category=category, course=course, form=form)


# shows a confirmation view if user clicks 'delete'
@app.route('/category/<int:category_id>/<int:course_id>/delete/')
def deleteCourse(category_id, course_id):
    course = Item.query.filter_by(id=course_id).one()
    db.session.delete(course)
    # count = Item.query.count()
    db.session.commit()
    return redirect(url_for('showCourses', category_id=category_id))


# api endpoint to return details for a specific course in JSON format
@app.route('/category/<int:category_id>/<int:course_id>/JSON/')
def apiCourseJSON(course_id):
    return 'This will return all details for a specific course in JSON.'
