# services/users/project/tests/test_user_model.py

import unittest

from sqlalchemy.exc import IntegrityError

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user('miniglaven', 'miniglaven@mini-super.com',
                        'miniglaven')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'miniglaven')
        self.assertEqual(user.email, 'miniglaven@mini-super.com')
        self.assertTrue(user.active)
        self.assertTrue(user.password)
        self.assertFalse(user.admin)

    def test_add_user_duplicate_username(self):
        add_user('miniglaven', 'miniglaven@mini-super.com',
                 'miniglaven')
        duplicate_user = User(
            username='miniglaven',
            email='miniglaven@mini-super.com',
            password='miniglaven'
        )
        self.assertRaises(IntegrityError, db.session.add(duplicate_user))

    def test_add_user_duplicate_email(self):
        add_user('miniglaven', 'miniglaven@mini-super.com', 'miniglaven')
        duplicate_user = User(
            username='miniglaven',
            email='miniglaven@mini-super.com',
            password='miniglaven'
        )
        self.assertRaises(IntegrityError, db.session.add(duplicate_user))

    def test_to_json(self):
        user = add_user('miniglaven', 'miniglaven@mini-super.com',
                        'miniglaven')
        self.assertTrue(isinstance(user.to_json(), dict))

    def test_passwords_are_random(self):
        user_one = add_user('miniglaven', 'miniglaven@mini-super.com',
                            'miniglaven')
        user_two = add_user('miniglaven', 'miniglaven@mini-super.com',
                            'miniglaven')
        self.assertNotEqual(user_one.password, user_two.password)

    def test_encode_auth_token(self):
        user = add_user('miniglaven', 'miniglaven@mini-super.com',
                        'miniglaven')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = add_user('miniglaven', 'miniglaven@mini-super.com',
                        'miniglaven')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertEqual(User.decode_auth_token(auth_token), user.id)


if __name__ == '__main__':
    unittest.main()
