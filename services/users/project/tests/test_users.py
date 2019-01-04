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
        add_user('miniglaven', 'miniglaven@mini-super.com', 'miniglaven')
        user = User.query.filter_by(email='miniglaven@mini-super.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'miniglaven@mini-super.com',
                    'password': 'miniglaven'
                }),
                content_type='application/json',
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jwilcox',
                    'email': 'jwilcox@mini-super.com',
                    'password': 'miniglaven'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('jwilcox@mini-super.com was added!',
                          data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        # update user
        user = User.query.filter_by(email='glaven@mini-super.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not have a username key.
        """
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        # update user
        user = User.query.filter_by(email='glaven@mini-super.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        # update user
        user = User.query.filter_by(email='glaven@mini-super.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com',
                    'password': 'miniglaven'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user('jasonwlcx', 'jasonwlcx@mini-super.com', 'miniglaven')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('jasonwlcx', data['data']['username'])
            self.assertIn('jasonwlcx@mini-super.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/senor')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user('jasonwlcx', 'jasonwlcx@mini-super.com', 'miniglaven')
        add_user('superglaven', 'superglaven@mini-super.com', 'superglaven')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('jasonwlcx', data['data']['users'][0]['username'])
            self.assertIn(
                'jasonwlcx@mini-super.com', data['data']['users'][0]['email'])
            self.assertTrue(data['data']['users'][0]['active'])  # new
            self.assertFalse(data['data']['users'][0]['admin'])  # new
            self.assertIn('superglaven', data['data']['users'][1]['username'])
            self.assertIn(
                'superglaven@mini-super.com', data['data']['users'][1]['email']
            )
            self.assertTrue(data['data']['users'][1]['active'])  # new
            self.assertFalse(data['data']['users'][1]['admin'])  # new
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Ensure the main route behaves correctly when no users have been
        added to the database."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure the main route behaves correctly when users have been
        added to the database."""
        add_user('jasonwlcx', 'jasonwlcx@mini-super.com', 'miniglaven')
        add_user('superglaven', 'superglaven@mini-super.com', 'superglaven')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'jasonwlcx', response.data)
            self.assertIn(b'superglaven', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(
                    username='jasonwlcx',
                    email='jasonwlcx@mini-super.com',
                    password='miniglaven'
                ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'jasonwlcx', response.data)

    def test_add_user_invalid_json_keys_no_password(self):
        """
        Ensure error is thrown if the JSON object
        does not have a password key.
        """
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        # update user
        user = User.query.filter_by(email='glaven@mini-super.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='jasonwlcx',
                    email='jasonwlcx@mini-super.com')),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_inactive(self):
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        # update user
        user = User.query.filter_by(email='glaven@mini-super.com').first()
        user.active = False
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'jasonwlcx',
                    'email': 'jasonwlcx@mini-super.com',
                    'password': 'miniglaven'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_add_user_not_admin(self):
        add_user('glaven', 'glaven@mini-super.com', 'glaven')
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'glaven',
                    'email': 'glaven@mini-super.com',
                    'password': 'glaven'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'You do not have permission to do that.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
