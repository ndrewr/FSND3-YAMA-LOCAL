"""
    all test cases
"""
# from flask import Flask
import unittest
from flask.ext.testing import TestCase

import sys
import os.path
# Import from sibling directory ..\api
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from yama import app, db


class testRoutes(TestCase):

    def create_app(self):
        # app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def testHomeRoute(self):

        assert 1 == 1

    def testCourseListRoute(self):
        pass

    def testCourseDetailRoute(self):
        pass


if __name__ == '__main__':
    unittest.main()
