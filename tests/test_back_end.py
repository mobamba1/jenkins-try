import unittest

from flask import url_for
from flask_testing import TestCase
from flask_login import login_user, current_user, logout_user, login_required

from application import app, db, bcrypt
from application.models import Users, Posts
from application.forms import PostForm, RegistrationForm, LoginForm, UpdateAccountForm
from os import getenv

class TestBase(TestCase):

############################# pass in config for test database########################

    def create_app(self):
        config_name = 'testing'
        app.config.update(SQLALCHEMY_DATABASE_URI=getenv('TEST_DB_URI'),
                SECRET_KEY=getenv('TEST_SECRET_KEY'),
                WTF_CSRF_ENABLED=False,
                DEBUG=True
                )
        return app

############## Will be called before every test############################
   
    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()

        # create test admin user
        hashed_pw = bcrypt.generate_password_hash('admin2020')
        admin = Users(first_name="admin", last_name="admin", email="admin@admin.com", password=hashed_pw)

        # create test non-admin user
        hashed_pw_2 = bcrypt.generate_password_hash('test2020')
        employee = Users(first_name="test", last_name="user", email="test@user.com", password=hashed_pw_2)

        # save users to database
        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()


###########################Will be called after every test#####################

    def tearDown(self):
        db.session.remove()
        db.drop_all()

##########################Test that homepage is accessible without login#########################

class TestViews(TestBase):
    def test_homepage_view(self):
        response = self.client.get(url_for('home'))
        self.assertEqual(response.status_code, 200)

########Test that when I add a new post, I am redirected to the homepage with the new post visible#######

class TestPosts(TestBase):
    def test_add_new_post(self):
        with self.client:
            self.client.post(url_for('login'), data=dict(email = "admin@admin.com", password = "admin2020"),
                    follow_redirects = True)
            response = self.client.post(
                '/post',
                data=dict(
                    title="Test Title",
                    content="Test Content"),
                follow_redirects=True)
            self.assertIn(b'Test Title', response.data)

#####################################
##register account
class TestRegister(TestBase):
    def test_add_new_user(self):
        with self.client:
            response = self.client.post(
                    '/register',
                    data=dict(
                        first_name="Tobi",
                        last_name="Tobi",
                        email="tobi@tobi.com",
                        password="tobi2020",
                        confirm_password="tobi2020"),
                    follow_redirects=True)
            self.assertEqual(response.status_code, 200)

##############################################
##logout user
class TestLogout(TestBase):
    def test_logout(self):
        with self.client:
            self.client.post(url_for('login'), data=dict(email = "admin@admin.com", password = "admin2020"),
                    follow_redirects = True)
            response = self.client.post(
                    '/logout',
                    follow_redirects=True)
            self.assertEqual(response.status_code, 200)

############################################
##update account
class Testupdate(TestBase):
    def test_update_user(self):
        with self.client:
            self.client.post(url_for('login'), data=dict(email = "admin@admin.com", password = "admin2020"),
                    follow_redirects = True)
            response = self.client.post(
                    '/account',
                    data=dict(first_name="tobi", last_name="tobi", email="tobi@tobi.com"),
                    follow_redirects = True)
            self.assertEqual(response.status_code, 200)

#####################################
##delete account
