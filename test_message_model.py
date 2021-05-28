"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app


class MessageModelTestCase(TestCase):
    """Test messages"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.client = app.test_client()
        self.u1 = User.signup("testuser1", "test1@test.com", "HASHED_PASSWORD1", None)
        self.uid1 = 1
        self.u1.id = self.uid1
        self.u2 = User.signup("testuser2", "test2@test.com", "HASHED_PASSWORD", None)
        self.uid2 = 2
        self.u2.id = self.uid2
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(text="Hey everyone", user_id=self.uid1)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "Hey everyone")

    def test_message_likes(self):
        "Can a user like another user's post?"
        m1 = Message(text="hdshdjhfhjx hdjsddj?", user_id=self.uid1)

        m2 = Message(text="I can't think of something funny", user_id=self.uid1)
        db.session.add_all(
            [
                m1,
                m2,
            ]
        )
        db.session.commit()

        self.u1.likes.append(m1)

        db.session.commit()

        user1_likes = Likes.query.filter(Likes.user_id == self.uid1).all()
        self.assertEqual(len(user1_likes), 1)
