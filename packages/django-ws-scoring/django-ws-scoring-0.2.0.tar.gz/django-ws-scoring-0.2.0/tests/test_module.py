from django.test import TestCase
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from ws_scoring.module_ws_scoring import ManipulateQuerySet
import uuid
import django.utils.timezone as timezone
from django_pandas.io import read_frame


class TestManipulateQuerySet(TestCase):

    def setUp(self):
        # Mock user history data
        self.user_history_data = [
            {
                'keyword_search': None,
                'location_search': None,
                'created_at': timezone.now() - timedelta(days=1),
                'kldb': '12345',
                'session_id': uuid.UUID('12345678-1234-5678-1234-567812345678')
            },
            {
                'keyword_search': None,
                'location_search': None,
                'created_at': timezone.now() - timedelta(days=1),
                'kldb': '12335',
                'session_id': uuid.UUID('12345678-1234-5678-1234-567812345678')
            },
            {
                'keyword_search': 'python developer',
                'location_search': 'New York',
                'created_at': timezone.now() - timedelta(days=3),
                'kldb': None,
                'session_id': uuid.UUID('12345678-1234-5678-1234-567812345678')
            },
            {
                'keyword_search': 'javascript developer',
                'location_search': 'San Francisco',
                'created_at': timezone.now() - timedelta(days=21),
                'kldb': None,
                'session_id': uuid.UUID('12345678-1234-5678-1234-567812345678')
            },
            {
                'keyword_search': 'data scientist',
                'location_search': 'Boston',
                'created_at': timezone.now() - timedelta(days=51),
                'kldb': None,
                'session_id': uuid.UUID('12345678-1234-5678-1234-567812345678')
            }
        ]

        self.field_weight_dict = {
            'location': 1.0,
            'keyword': 1.5,
            'kldb': 2.0
        }

        # Simulated queryset mock for JobDetail model
        self.queryset_mock = MagicMock()

        self.manipulator = ManipulateQuerySet(
            queryset=self.queryset_mock,
            user_history=self.user_history_data,  # Assuming this is acceptable by read_frame
            field_weight_dict=self.field_weight_dict
        )

    @patch('ws_scoring.module_ws_scoring.read_frame')
    def test_preprocess_user_history(self, mock_read_frame):
        # Prepare mock DataFrame from the user history data
        mock_read_frame.return_value = pd.DataFrame(self.user_history_data)

        processed_df = self.manipulator.preprocess_user_history()
        self.assertFalse(processed_df.empty)

        # Check for correct group assignment based on 'created_at'
        self.assertTrue(all(processed_df['group'].notnull()))

        # Check if 'weight_factor' is assigned correctly
        self.assertIn('weight_factor', processed_df.columns)

    @patch('ws_scoring.module_ws_scoring.read_frame')
    def test_get_scores_map(self, mock_read_frame):
        # Mock the read_frame call to return a DataFrame for the job details
        # since preprocess_user_history will process the self.user_history_data
        user_history_df = pd.DataFrame(self.user_history_data)

        jobs_df = pd.DataFrame([
            {'id': 1, 'location': 'New York', 'keyword': 'python developer', 'kldb': '12345'},  # Expected high score
            {'id': 2, 'location': 'San Francisco', 'keyword': 'javascript developer', 'kldb': '67890'},
            # Expected medium score
            {'id': 3, 'location': 'Boston', 'keyword': 'data scientist', 'kldb': '11111'},
            # Expected low score due to no kldb match
        ])

        mock_read_frame.side_effect = [user_history_df, jobs_df]

        scores_map = self.manipulator.get_scores_map()
        self.assertIsInstance(scores_map, dict)

        # Given jobs_df and how scores are calculated, check if the scoring reflects these rules
        self.assertGreater(scores_map.get(1, 0), scores_map.get(2, 0), "Job with full match should score highest")
        self.assertGreater(scores_map.get(2, 0), scores_map.get(3, 0),
                           "Job with partial match should score lower than full match but higher than no match")
        self.assertTrue(all(score > 0 for score in scores_map.values()), "All jobs should have a non-zero score")

    def test_calculate_relevancy(self):
        # Mock `get_scores_map` to return a predefined score map
        self.manipulator.get_scores_map = MagicMock(return_value={1: 10, 2: 5})  # Example IDs and scores

        annotated_qs = self.manipulator.calculate_relevancy()

        self.manipulator.queryset.annotate.assert_called()
