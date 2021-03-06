"""Test cases for the POST server route /controllerregister."""

import time
import unittest
from unittest.mock import patch
from server.server import app
from server.schemas.controller import CONTROLLER_COLLECTION, TIMEOUT
from .mock_firebase import MockClient

OK = 200
BAD_REQUEST = 400

class ControllerRegisterTest(unittest.TestCase):
    # Setup and helper functions

    @classmethod
    def setUpClass(cls):
        """Runs once before all test cases."""
        cls.route = '/controllerregister'
        cls.client = app.test_client()

    def post(self, data):
        """Helper function for making POST requests.

        Usage:
            # POST /controllerregister -F "param_1=1&param_2=2"
            response = self.post({param_1: 1, param_2: 2})
        """
        return self.client.post(self.route, data=data)

    @patch('server.server.db', new_callable=MockClient)
    def test_new_controller_can_register(self, mock_db):
        "Tests that a controller can register if not seen before"
        controller_id = "kevin"
        params = {"board_id": controller_id,
                  "board_version": "0.0.1"}
        response = self.post(params)
        self.assertEqual(OK, response.status_code)
        # assert that controller is in database
        self.assertTrue(mock_db.collection(CONTROLLER_COLLECTION).document(controller_id).exists)

    @patch('server.server.db', new_callable=MockClient)
    def test_controller_cant_register_twice(self, mock_db):
        "Tests that a controller can't register within the time-out window"
        params = {"board_id": "kevin",
                  "board_version": "0.0.1"}
        response = self.post(params)
        self.assertEqual(OK, response.status_code)
        response = self.post(params)
        self.assertEqual(BAD_REQUEST, response.status_code)

    @patch('server.server.db', new_callable=MockClient)
    def test_controller_can_re_register_after_time_out(self, mock_db):
        "Test controller can re-register after time-out"
        controller_id = "kevin"
        params = {"board_id": controller_id,
                  "board_version": "0.0.1"}
        response = self.post(params)
        self.assertEqual(OK, response.status_code)
        # make sure at least TIMEOUT seconds have "passed"
        mock_db.collection(CONTROLLER_COLLECTION).document(controller_id).data["last_seen"] -= 2*TIMEOUT
        response = self.post(params)
        self.assertEqual(OK, response.status_code)

    @patch('server.server.db', new_callable=MockClient)
    def test_controller_register_with_no_game(self, mock_db):
        "When a controller registers it should not have a game assigned"
        controller_id = "kevin"
        params = {"board_id": controller_id,
                  "board_version": "0.0.1"}
        response = self.post(params)
        self.assertEqual(OK, response.status_code)
        self.assertIsNone(mock_db.collection(CONTROLLER_COLLECTION).document(controller_id).data["game_id"])

    @patch('server.server.db', new_callable=MockClient)
    def test_register_does_not_overwrite_game_id(self, mock_db):
        "Regression for a bug where registering overwrote existing game_id"
        controller_id = "kevin"
        game_id = "some_id"
        params = {"board_id": controller_id,
                  "board_version": "0.0.1"}
        c_w_game_id = {"board_id": controller_id, "board_version": "0.0.1",
                       "game_id": game_id, "last_seen": time.time() - 6000} # 6000 >> TIMEOUT

        mock_db.collection(CONTROLLER_COLLECTION).document(controller_id).set(c_w_game_id)
        response = self.post(params)
        self.assertEqual(OK, response.status_code)
        self.assertEqual(game_id, mock_db.collection(
            CONTROLLER_COLLECTION).document(controller_id).data['game_id'])
