"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        self.u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        self.uid1 = 1
        self.u1.id = self.uid1
        self.u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        self.uid2 = 2
        self.u2.id = self.uid2
        db.session.commit()
        # self.u1 = u1
        # self.uid1 = uid1

        # self.u2 = u2
        # self.uid2 = uid2

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("testuser2", str(resp.data))

    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))

    def test_user_show(self):
        """Does user page show up?"""
        with self.client as c:
            resp = c.get(f"/users/{self.uid1}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser1", str(resp.data))

    def test_show_following(self):
        """can a non logged in user see following page? does it work if logged in?"""
        self.u1.following.append(self.u2)
        db.session.commit()

        resp = self.client.get(f"/users/{self.uid1}/following", follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.get(f"/users/{self.uid1}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser2", html)

    def test_remove_followers(self):
        """can a logged in user add and remove followers?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1

            resp = c.post("/users/follow/2", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("@testuser2", html)

            resp = c.post("/users/stop-following/2", follow_redirects=True)
            html = resp.get_data(as_text=True)
            html = resp.get_data(as_text=True)
            self.assertNotIn("@testuser2", html)
