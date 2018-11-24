# services/users/project/tests/test_users.py


import json
import unittest

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the db"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('jasonwlcx@mini-super.com was added!',
                          data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """ Ensure error is thrown if JSON object has no username key"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'jasonwlcx@mini-super.com'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """ Ensure error if email addy already exists"""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message']
            )
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = User(username='jasonwlcx', email='jasonwlcx@mini-super.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('jasonwlcx', data['data']['username'])
            self.assertIn('jasonwlcx@mini-super.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided"""
        with self.client:
            response = self.client.get('/users/glaven')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        with self.client:
            response = self.client.get('/users/666')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly"""
        add_user('jasonwlcx', 'jasonwlcx@mini-super.com')
        add_user('glaven', 'glaven@mini-super.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('jasonwlcx', data['data']['users'][0]['username'])
            self.assertIn(
                'jasonwlcx@mini-super.com', data['data']['users'][0]['email']
            )
            self.assertIn('glaven', data['data']['users'][1]['username'])
            self.assertIn(
                'glaven@mini-super.com', data['data']['users'][1]['email']
            )
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Ensure main route behaves correctly when no users found in the db"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure the main route behaves correctly when users have been
        added to the database."""
        add_user('jasonwlcx', 'jasonwlcx@mini-super.com')
        add_user('glaven', 'glaven@mini-super.com')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'jasonwlcx', response.data)
            self.assertIn(b'glaven', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the db"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='jasonwlcx',
                          email='jasonwlcx@mini-super.com'
                          ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'jasonwlcx', response.data)


if __name__ == '__main__':
    unittest.main()
