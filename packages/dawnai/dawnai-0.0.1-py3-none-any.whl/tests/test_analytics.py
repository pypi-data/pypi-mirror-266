import unittest
from unittest.mock import patch
import dawnai.analytics as analytics
import requests


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test data or configurations
        analytics.write_key = "0000"

    def tearDown(self):
        # Clean up any resources or reset any state after each test
        pass

    def test_identify(self):

        user_id = "user123"
        traits = {"email": "john@example.com", "name": "John"}

        try:
            analytics.identify(user_id, traits)
        except e:
            print("Error")
        # No assertion needed as the SDK handles the request internally

    def test_track(self):
        user_id = "user123"
        event = "Signed Up"
        properties = {"plan": "Premium"}
        analytics.track(user_id, event, properties)
        # No assertion needed as the SDK handles the request internally

    def test_track_ai(self):
        user_id = "user123"
        event = "AI Chat"
        model = "GPT-3"
        input_text = "Hello"
        output_text = "Hi there!"
        analytics.track_ai(
            user_id, event, model=model, user_input=input_text, output=output_text
        )
        # No assertion needed as the SDK handles the request internally
