"""Test cases for the POST server route /respondoffer."""

import unittest
import pytest
import json
from server.server import app
from unittest.mock import patch
from .mock_firebase import MockClient, MockAuth

OK          = 200
BAD_REQUEST = 400

@patch('firebase_admin.auth', new_callable=MockAuth)
@patch('server.server.db', new_callable=MockClient)
class RespondOfferTest(unittest.TestCase):
    # Setup and helper functions

    @classmethod
    def setUpClass(cls):
        """Runs once before all test cases."""
        cls.route = '/respondoffer'
        cls.client = app.test_client()

    def post(self, data):
        """Helper function for making POST requests.

        Usage:
            Making a POST request to /respondoffer with params {param_1: 1, param_2: 2} can be done with:
            response = self.post({param_1: 1, param_2: 2})
        """
        return RespondOfferTest.client.post(RespondOfferTest.route, data=data)

    def setUp(self):
        self.params = {'game_id': None, 'user_id': None, 'response': None}
        self.mock_game = {
            'id': 'some_game',
            'creator': 'some_creator',
            'players': {'w': 'some_player_1', 'b': 'some_player_2'},
            'public': True,
            'free_slots': 2,
            'time_controls': None,
            'remaining_time': {'w': None, 'b': None},
            'resigned': {'w': False, 'b': False},
            'draw_offers': {
                'w': {'made': True, 'accepted': False},
                'b': {'made': False, 'accepted': False}
            },
            'in_progress': True,
            'result': '*',
            'game_over': {'game_over': False, 'reason': None},
            'turn': 'w',
            'ply_count': 0,
            'move_count': 1,
            'pgn': '',
            'history': [],
            'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'initial_positions': {'a1': 'a1', 'a2': 'a2', 'a7': 'a7', 'a8': 'a8', 'b1': 'b1', 'b2': 'b2', 'b7': 'b7', 'b8': 'b8', 'c1': 'c1', 'c2': 'c2', 'c7': 'c7', 'c8': 'c8', 'd1': 'd1', 'd2': 'd2', 'd7': 'd7', 'd8': 'd8', 'e1': 'e1', 'e2': 'e2', 'e7': 'e7', 'e8': 'e8', 'f1': 'f1', 'f2': 'f2', 'f7': 'f7', 'f8': 'f8', 'g1': 'g1', 'g2': 'g2', 'g7': 'g7', 'g8': 'g8', 'h1': 'h1', 'h2': 'h2', 'h7': 'h7', 'h8': 'h8'}
        }

    def fill_params(self, game_id=None, user_id=None, response=None):
        self.params['game_id'] = game_id
        self.params['user_id'] = user_id
        self.params['response'] = response

    def set_up_mock(self, mock_db, mock_auth):
        """Creates some entries in the mock database"""
        mock_auth._mock_add_user("some_creator")
        mock_auth._mock_add_user("some_player_1")
        mock_auth._mock_add_user("some_player_2")
        mock_db.collection("games").add(self.mock_game, document_id='some_game')

    # Tests

    def test_game_doesnt_exist(self, mock_db, mock_auth):
        """Respond to a draw offer on a game that doesn't exist."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='game_that_doesnt_exist', user_id='some_player_1', response=True)
        response = self.post(self.params)
        self.assertEqual(BAD_REQUEST, response.status_code)

    def test_game_exists(self, mock_db, mock_auth):
        """Respond to a draw offer on a game that exists."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='some_game', user_id='some_player_1', response=True)
        response = self.post(self.params)
        self.assertEqual(OK, response.status_code)

    def test_user_id_doesnt_exist(self, mock_db, mock_auth):
        """Respond to a draw offer with the ID of a user that doesn't exist."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='some_game', user_id='user_that_doesnt_exist', response=True)
        response = self.post(self.params)
        self.assertEqual(BAD_REQUEST, response.status_code)

    def test_user_not_in_game(self, mock_db, mock_auth):
        """Respond to a draw offer with the ID of a user that exists, but isn't a player in the game."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='some_game', user_id='some_creator', response=True)
        response = self.post(self.params)
        self.assertEqual(BAD_REQUEST, response.status_code)

    def test_offer_accepted(self, mock_db, mock_auth):
        """Check that a draw offer is actually accepted."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='some_game', user_id='some_player_2', response=True)
        response = json.loads(self.post(self.params).data)
        self.assertEqual(response['draw_offers']['w']['accepted'], True)

    def test_offer_declined(self, mock_db, mock_auth):
        """Check that a draw offer is actually declined (and the made field is reset)."""
        self.set_up_mock(mock_db, mock_auth)
        self.fill_params(game_id='some_game', user_id='some_player_2', response=False)
        response = json.loads(self.post(self.params).data)
        self.assertEqual(response['draw_offers']['w']['made'], False)
        self.assertEqual(response['draw_offers']['w']['accepted'], False)
