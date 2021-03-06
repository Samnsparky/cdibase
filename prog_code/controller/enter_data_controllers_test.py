"""Automated tests for entering CDI forms manually.

Copyright (C) 2014 A. Samuel Pottinger ("Sam Pottinger", gleap.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Do not type check in tests
# type: ignore

import collections
import copy
import datetime
import json
import unittest
import unittest.mock

import cdibase
from ..struct import models
from ..util import constants
from ..util import db_util
from ..util import filter_util
from ..util import math_util
from ..util import recalc_util
from ..util import user_util

TEST_EMAIL = 'test.email@example.com'
TEST_DB_ID = '1'
TEST_USER = models.User(
    TEST_DB_ID,
    TEST_EMAIL,
    None,
    True,
    False,
    False,
    False,
    False,
    False,
    False,
    False
)
MALE_TEST_PERCENTILE_NAME = 'male_test_percentiles'
FEMALE_TEST_PERCENTILE_NAME = 'female_test_percentiles'
OTHER_TEST_PERCENTILE_NAME = 'other_test_percentiles'
TEST_CDI_FORMAT_NAME = 'standard'
TEST_FORMAT = models.CDIFormat(
    'standard',
    'standard',
    'standard.yaml',
    {
        'categories': [
            {
                'words':['cat_1_word_1', 'cat_1_word_2', 'cat_1_word_3'],
                'language': 'english'
            },
            {
                'words':['cat_2_word_1', 'cat_2_word_2', 'cat_2_word_3'],
                'language': 'english'
            }
        ],
        'percentiles': {
            'male': MALE_TEST_PERCENTILE_NAME,
            'female': FEMALE_TEST_PERCENTILE_NAME,
            'other': OTHER_TEST_PERCENTILE_NAME
        },
        'options': [
            {'name': 'said', 'value': 1},
            {'name': 'not said', 'value': 0}
        ],
        'count_as_spoken': [1],
        'meta': {'cdi_type': 'standard'}
    }
)

TEST_STUDY_ID = '456'
TEST_STUDY_ID_2 = '789'
TEST_SNAPSHOT_ID = 789
TEST_ITEMS_EXCLUDED = 3
TEST_EXTRA_CATEGORIES = 4
TEST_SESSION_NUM = 4
TEST_LANGUAGES = ['english']
TEST_NUM_LANGUAGES = 1
TEST_HARD_OF_HEARING = False
TEST_STUDY = 'test study'
TEST_STUDY_2 = 'test study 2'
TEST_BIRTHDAY = '2011/09/12'
TEST_BIRTHDAY_DATE = datetime.date(2011, 9, 12)
TEST_SESSION = '2013/09/12'
TEST_TOTAL_NUM_SESSIONS = 48
TEST_AGE = 21
TEST_PERCENTILE = 50

TEST_PERCENTILE_MODEL_CLS = collections.namedtuple(
    'TestPercentileModel',
    ['details']
)
TEST_PERCENTILE_MODEL = TEST_PERCENTILE_MODEL_CLS('test details')

TEST_SUCCESSFUL_PARAMS = {
    'global_id': TEST_DB_ID,
    'study_id': TEST_STUDY_ID,
    'study': TEST_STUDY,
    'gender': constants.MALE,
    'age': TEST_AGE,
    'birthday': TEST_BIRTHDAY,
    'session_date': TEST_SESSION,
    'session_num': TEST_SESSION_NUM,
    'items_excluded': TEST_ITEMS_EXCLUDED,
    'extra_categories': TEST_EXTRA_CATEGORIES,
    'total_num_sessions': TEST_TOTAL_NUM_SESSIONS,
    'hard_of_hearing': 'off',
    'cat_1_word_1_report': '1',
    'cat_1_word_2_report': '0',
    'cat_1_word_3_report': '1',
    'cat_2_word_1_report': '0',
    'cat_2_word_2_report': '1',
    'cat_2_word_3_report': '0'
}

TEST_EXPECTED_SNAPSHOT = models.SnapshotMetadata(
    None,
    TEST_DB_ID,
    TEST_STUDY_ID,
    TEST_STUDY,
    constants.MALE,
    TEST_AGE,
    TEST_BIRTHDAY,
    TEST_SESSION,
    TEST_SESSION_NUM,
    TEST_TOTAL_NUM_SESSIONS,
    3,
    TEST_ITEMS_EXCLUDED,
    TEST_PERCENTILE,
    TEST_EXTRA_CATEGORIES,
    0,
    TEST_LANGUAGES,
    TEST_NUM_LANGUAGES,
    'standard',
    constants.EXPLICIT_FALSE,
    False
)

TEST_EXPECTED_SNAPSHOT_2 = models.SnapshotMetadata(
    None,
    TEST_DB_ID,
    TEST_STUDY_ID_2,
    TEST_STUDY_2,
    constants.MALE,
    TEST_AGE,
    TEST_BIRTHDAY,
    TEST_SESSION,
    TEST_SESSION_NUM,
    TEST_TOTAL_NUM_SESSIONS,
    3,
    TEST_ITEMS_EXCLUDED,
    TEST_PERCENTILE,
    TEST_EXTRA_CATEGORIES,
    0,
    TEST_LANGUAGES,
    TEST_NUM_LANGUAGES,
    'standard',
    constants.EXPLICIT_FALSE,
    False
)

TEST_EXPECTED_WORD_ENTRIES = {
    'cat_1_word_1': 1,
    'cat_1_word_2': 0,
    'cat_1_word_3': 1,
    'cat_2_word_1': 0,
    'cat_2_word_2': 1,
    'cat_2_word_3': 0
}


class EnterDataControllersTests(unittest.TestCase):

    def setUp(self):
        self.app = cdibase.app
        self.app.debug = True
        self.__callback_called = False

    def __run_with_mocks(self, on_start, body, on_end):
        with unittest.mock.patch('prog_code.util.user_util.get_user') as mock_get_user:
            with unittest.mock.patch('prog_code.util.db_util.load_cdi_model') as mock_load_cdi_model:
                with unittest.mock.patch('prog_code.util.db_util.insert_snapshot') as mock_insert_snapshot:
                    with unittest.mock.patch('prog_code.util.db_util.report_usage') as mock_report_usage:
                        with unittest.mock.patch('prog_code.util.db_util.load_percentile_model') as mock_load_percentile_model:
                            with unittest.mock.patch('prog_code.util.math_util.find_percentile') as mock_find_percentile:
                                with unittest.mock.patch('prog_code.util.filter_util.run_search_query') as mock_run_search_query:
                                    with unittest.mock.patch('prog_code.util.db_util.lookup_global_participant_id') as mock_lookup_global_participant_id:
                                        with unittest.mock.patch('prog_code.util.db_util.update_participant_metadata') as mock_update_participant_metadata:
                                            with unittest.mock.patch('prog_code.util.recalc_util.recalculate_ages_and_percentiles') as mock_recalculate_ages_and_percentiles:
                                                with unittest.mock.patch('prog_code.util.db_util.load_cdi_model_listing') as mock_load_cdi_model_listing:
                                                    mocks = {
                                                        'get_user': mock_get_user,
                                                        'load_cdi_model': mock_load_cdi_model,
                                                        'insert_snapshot': mock_insert_snapshot,
                                                        'report_usage': mock_report_usage,
                                                        'load_percentile_model': mock_load_percentile_model,
                                                        'find_percentile': mock_find_percentile,
                                                        'run_search_query': mock_run_search_query,
                                                        'lookup_global_participant_id': mock_lookup_global_participant_id,
                                                        'update_participant_metadata': mock_update_participant_metadata,
                                                        'recalculate_ages_and_percentiles': mock_recalculate_ages_and_percentiles,
                                                        'load_cdi_model_listing': mock_load_cdi_model_listing
                                                    }

                                                    on_start(mocks)
                                                    body()
                                                    on_end(mocks)

                                                    self.__callback_called = True

    def __default_on_start(self, mocks):
        mocks['get_user'].return_value = TEST_USER
        mocks['load_cdi_model'].return_value = TEST_FORMAT

    def __default_on_end(self, mocks):
        mocks['get_user'].assert_called_with(TEST_EMAIL)
        mocks['load_cdi_model'].assert_called_with(TEST_CDI_FORMAT_NAME)

    def __run_with_default_mocks(self, body):
        self.__run_with_mocks(
            lambda mocks: self.__default_on_start(mocks),
            body,
            lambda mocks: self.__default_on_end(mocks),
        )

    def __assert_callback(self):
        self.assertTrue(self.__callback_called)

    def check_lookup_studies_metadata(self, returned_metadata):
        """Run assertions that the provided metadata matches the test snapshot.

        @param returned_metadata: The metadata to check.
        @type returned_metadata: dict
        """
        self.assertEqual(
            returned_metadata['gender'],
            TEST_EXPECTED_SNAPSHOT.gender
        )

        self.assertEqual(
            returned_metadata['birthday'],
            TEST_EXPECTED_SNAPSHOT.birthday
        )

        self.assertEqual(
            returned_metadata['hard_of_hearing'],
            TEST_EXPECTED_SNAPSHOT.hard_of_hearing
        )

        self.assertEqual(
            returned_metadata['languages'],
            TEST_EXPECTED_SNAPSHOT.languages
        )

    def test_format_for_enter_data(self):
        def body():
            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                url = '/base/enter_data/%s' % TEST_CDI_FORMAT_NAME
                client.get(url)

                with client.session_transaction() as sess:
                    err = sess.get(constants.ERROR_ATTR, None)
                    self.assertEqual(err, None)

                url = '/base/enter_data/%s' % 'invalid format'
                client.get(url)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)

        def on_start(mocks):
            mocks['get_user'].return_value = TEST_USER
            mocks['load_cdi_model'].side_effect = [
                TEST_FORMAT,
                None
            ]

        def on_end(mocks):
            mocks['get_user'].assert_called_with(TEST_EMAIL)
            mocks['load_cdi_model'].assert_any_call(TEST_CDI_FORMAT_NAME)
            mocks['load_cdi_model'].assert_any_call('invalid format')

        self.__run_with_mocks(on_start, body, on_end)
        self.__assert_callback()

    def test_missing_enter_data_params(self):
        def body():
            target_url = '/base/enter_data/%s' % TEST_CDI_FORMAT_NAME

            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['study_id']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['study']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['gender']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['age']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['birthday']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['session_date']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['session_num']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['items_excluded']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['extra_categories']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                del test_params['total_num_sessions']
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

        self.__run_with_default_mocks(body)
        self.__assert_callback()

    def test_invalid_enter_data_params(self):

        def body():
            target_url = '/base/enter_data/%s' % TEST_CDI_FORMAT_NAME

            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['gender'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['age'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['birthday'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['session_date'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['session_num'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['items_excluded'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['extra_categories'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

                test_params = copy.copy(TEST_SUCCESSFUL_PARAMS)
                test_params['total_num_sessions'] = 'invalid'
                client.post(target_url, data=test_params)

                with client.session_transaction() as sess:
                    self.assertTrue(constants.ERROR_ATTR in sess)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(confirmation_attr, None)
                    del sess[constants.ERROR_ATTR]

        self.__run_with_default_mocks(body)
        self.__assert_callback()

    def test_success_enter_data(self):

        def body():
            target_url = '/base/enter_data/%s' % TEST_CDI_FORMAT_NAME

            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                client.post(target_url, data=TEST_SUCCESSFUL_PARAMS)

                with client.session_transaction() as sess:
                    error_attr = sess.get(constants.ERROR_ATTR, None)
                    confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                    self.assertEqual(error_attr, None)
                    self.assertNotEqual(confirmation_attr, None)

        def on_start(mocks):
            mocks['get_user'].return_value = TEST_USER
            mocks['load_cdi_model'].return_value = TEST_FORMAT
            mocks['load_percentile_model'].return_value = TEST_PERCENTILE_MODEL
            mocks['find_percentile'].return_value = TEST_PERCENTILE

        def on_end(mocks):
            mocks['get_user'].assert_called_with(TEST_EMAIL)
            mocks['load_cdi_model'].assert_called_with(TEST_CDI_FORMAT_NAME)
            mocks['load_percentile_model'].assert_called_with(
                MALE_TEST_PERCENTILE_NAME
            )
            mocks['find_percentile'].assert_called_with(
                'test details',
                3,
                TEST_AGE,
                6
            )
            mocks['report_usage'].assert_called_with(
                'test.email@example.com',
                'Enter Data',
                unittest.mock.ANY
            )
            mocks['insert_snapshot'].assert_called_with(
                TEST_EXPECTED_SNAPSHOT,
                TEST_EXPECTED_WORD_ENTRIES
            )

        self.__run_with_mocks(on_start, body, on_end)
        self.__assert_callback()

    def test_lookup_studies_by_global_id(self):

        def body():
            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                lookup_user_data = {
                    'method': 'by_global_id',
                    'global_id': TEST_DB_ID
                }
                result_info = client.post(
                    '/base/edit_data/lookup_user',
                    data=lookup_user_data
                )

            result = json.loads(result_info.data)
            returned_global_id = result['global_id']
            returned_studies = result['cdis']

            self.assertEqual(returned_global_id, TEST_DB_ID)

            self.assertEqual(len(returned_studies), 2)

            if returned_studies[0]['study'] == TEST_STUDY:
                self.assertEqual(returned_studies[0]['study'], TEST_STUDY)
                self.assertEqual(returned_studies[0]['study_id'], TEST_STUDY_ID)
                self.assertEqual(returned_studies[1]['study'], TEST_STUDY_2)
                self.assertEqual(returned_studies[1]['study_id'], TEST_STUDY_ID_2)
            else:
                self.assertEqual(returned_studies[0]['study'], TEST_STUDY_2)
                self.assertEqual(returned_studies[0]['study_id'], TEST_STUDY_ID_2)
                self.assertEqual(returned_studies[1]['study'], TEST_STUDY)
                self.assertEqual(returned_studies[1]['study_id'], TEST_STUDY_ID)

            self.check_lookup_studies_metadata(result['metadata'])

        def on_start(mocks):
            ret_list = [
                TEST_EXPECTED_SNAPSHOT,
                TEST_EXPECTED_SNAPSHOT_2
            ]

            mocks['get_user'].return_value = TEST_USER
            mocks['run_search_query'].return_value = ret_list

        def on_end(mocks):
            mocks['get_user'].assert_called_with(TEST_EMAIL)
            mocks['run_search_query'].assert_called_with(
                [models.Filter('child_id', 'eq', TEST_DB_ID)],
                constants.SNAPSHOTS_DB_TABLE
            )

        self.__run_with_mocks(on_start, body, on_end)
        self.__assert_callback()

    def test_lookup_studies_by_study_id(self):

        def body():
            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                lookup_user_data = {
                    'method': 'by_study_id',
                    'study': TEST_STUDY,
                    'study_id': TEST_STUDY_ID
                }
                result_info = client.post(
                    '/base/edit_data/lookup_user',
                    data=lookup_user_data
                )

            result = json.loads(result_info.data)
            returned_global_id = result['global_id']
            returned_studies = result['cdis']

            self.assertEqual(returned_global_id, TEST_DB_ID)

            self.assertEqual(len(returned_studies), 2)

            if returned_studies[0]['study'] == TEST_STUDY:
                self.assertEqual(returned_studies[0]['study'], TEST_STUDY)
                self.assertEqual(returned_studies[0]['study_id'], TEST_STUDY_ID)
                self.assertEqual(returned_studies[1]['study'], TEST_STUDY_2)
                self.assertEqual(returned_studies[1]['study_id'], TEST_STUDY_ID_2)
            else:
                self.assertEqual(returned_studies[0]['study'], TEST_STUDY_2)
                self.assertEqual(returned_studies[0]['study_id'], TEST_STUDY_ID_2)
                self.assertEqual(returned_studies[1]['study'], TEST_STUDY)
                self.assertEqual(returned_studies[1]['study_id'], TEST_STUDY_ID)

            self.check_lookup_studies_metadata(result['metadata'])

        def on_start(mocks):
            ret_list = [
                TEST_EXPECTED_SNAPSHOT,
                TEST_EXPECTED_SNAPSHOT_2
            ]

            mocks['get_user'].return_value = TEST_USER
            mocks['lookup_global_participant_id'].return_value = TEST_DB_ID
            mocks['run_search_query'].return_value = ret_list

        def on_end(mocks):
            mocks['get_user'].assert_called_with(TEST_EMAIL)
            mocks['lookup_global_participant_id'].assert_called_with(
                TEST_STUDY,
                TEST_STUDY_ID
            )
            mocks['run_search_query'].assert_called_with(
                [models.Filter('child_id', 'eq', TEST_DB_ID)],
                constants.SNAPSHOTS_DB_TABLE
            )

        self.__run_with_mocks(on_start, body, on_end)
        self.__assert_callback()

    def test_edit_metadata(self):
        self.__new_birthday = '2014/12/28'
        self.__new_languages = ['english', 'spanish']
        self.__ret_list = [
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2,
        ]

        def body():
            with self.app.test_client() as client:

                with client.session_transaction() as sess:
                    sess['email'] = TEST_EMAIL

                new_metadata = {
                    'global_id': TEST_DB_ID,
                    'gender': constants.FEMALE,
                    'birthday': self.__new_birthday,
                    'hard_of_hearing': constants.EXPLICIT_TRUE,
                    'languages': ','.join(self.__new_languages),
                    'snapshot_ids': json.dumps([
                        {'study': TEST_STUDY, 'id': '1'},
                        {'study': TEST_STUDY_2, 'id': '2'}
                    ])
                }

                client.post(
                    '/base/edit_data',
                    data=new_metadata
                )

        def on_start(mocks):
            mocks['get_user'].return_value = TEST_USER
            mocks['run_search_query'].return_value = self.__ret_list

        def on_end(mocks):
            mocks['get_user'].assert_called_with(
                TEST_EMAIL
            )
            mocks['report_usage'].assert_called_with(
                'test.email@example.com',
                'Update Metadata',
                '{"global_id": "1"}'
            )
            mocks['update_participant_metadata'].assert_called_with(
                TEST_DB_ID,
                constants.FEMALE,
                self.__new_birthday,
                constants.EXPLICIT_TRUE,
                self.__new_languages,
                snapshot_ids=[
                    {'study': TEST_STUDY, 'id': '1'},
                    {'study': TEST_STUDY_2, 'id': '2'}
                ]
            )
            mocks['run_search_query'].assert_called_with(
                [models.Filter('child_id', 'eq', TEST_DB_ID)],
                constants.SNAPSHOTS_DB_TABLE
            )
            mocks['recalculate_ages_and_percentiles'].assert_called_with(
                self.__ret_list
            )

        self.__run_with_mocks(on_start, body, on_end)
        self.__assert_callback()
