"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        uid1 = 1
        u1.id = uid1
        u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        uid2 = 2
        u2.id = uid2

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr display what is expected?"""

        self.assertEqual(repr(self.u1), f"<User #1: testuser1, test1@test.com>")

    def test_user_followers(self):
        """Test followers are added"""
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?
        Does is_following successfully detect when user1 is not following user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?
        Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u1))

    def test_signup(self):
        """Does User.create successfully create a new user given valid credentials?
        Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
        Does User.authenticate successfully return a user when given a valid username and password?
        """
        new_user = User.signup(
            "lalala",
            "lalala@testemail.com",
            "12234",
            "https://library.kissclipart.com/20180903/hfq/kissclipart-outline-of-a-person-clipart-clip-art-074a7906dd67089a.jpg",
        )
        id = 22
        new_user.id = id
        db.session.commit()
        new_user_test = User.query.get(id)
        self.assertTrue(new_user_test.username == "lalala")
        self.assertTrue(new_user_test.email == "lalala@testemail.com")
        self.assertTrue(new_user_test.password.index("$2b$") != -1)

    def test_authenticate(self):
        """Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?"""
        self.assertTrue(User.authenticate("testuser1", "HASHED_PASSWORD1"))
        self.assertFalse(User.authenticate("testuser2", "wrongpassword"))
        self.assertFalse(User.authenticate("beepbeep", "HASHED_PASSWORD1"))
