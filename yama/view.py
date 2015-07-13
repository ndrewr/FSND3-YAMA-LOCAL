"""
    defines the app routes
"""

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response
from yama import app

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import json
import requests


# home page aka base camp. Shows course categories AND a list of most recent added courses
@app.route('/')
@app.route('/base/')
def home():
    return 'Hello, this is the home page.'


# shows the user login page with third party auth options
# this page should auto-redirect to the prev page user was on
@app.route('/login/')
def loginUser():
    return 'This is the login page.'


# automatically logsout the user and redirects them to home page
@app.route('/logout/')
def logoutUser():
    return 'This will be the logout page.'


# show all courses available under one subject
# logged-in users will also see an 'add' option for new courses
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/list/')
def showCourses(category_id):
    return 'This will show all courses under one category.'


# show an interface to Add a course to current subject
@app.route('/category/<int:category_id>/add/')
def addCourse(category_id):
    return 'This will be a UI for adding new courses under an offered subject.'


# show additional details on the selected course;
# logged-in users will also see an 'edit' option to edit course details
@app.route('/category/<int:category_id>/<int:course_id>/')
@app.route('/category/<int:category_id>/<int:course_id>/details/')
def showCourse(category_id, course_id):
    return 'This will show more details on a specific course.'


# shows an interface to edit the details of a specific course
# also has a link to delete this course from the category's course list
@app.route('/category/<int:category_id>/<int:course_id>/edit/')
def editCourse(category_id, course_id):
    return 'This will be a UX allowing users to edit OR DELETE course details'


# shows a confirmation view if user clicks 'delete'
@app.route('/category/<int:category_id>/<int:course_id>/delete/')
def deleteCourse(category_id, course_id):
    return 'Will be a confirmation screen in case DELETE was accidentally clicked'


# api endpoint to return all courses under a category in JSON format
@app.route('/category/<int:category_id>/JSON/')
def apiCategoryJSON(category_id):
    return 'This will return a list of all courses under given category subject'


# api endpoint to return details for a specific course in JSON format
@app.route('/category/<int:category_id>/<int:course_id>/JSON/')
def apiCourseJSON(course_id):
    return 'This will return all details for a specific course in JSON.'
