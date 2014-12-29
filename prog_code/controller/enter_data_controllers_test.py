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

import collections
import copy
import datetime
import json

import mox

import daxlabbase
from ..struct import models
from ..util import constants
from ..util import db_util
from ..util import filter_util
from ..util import math_util
from ..util import recalc_util
from ..util import user_util

TEST_EMAIL = 'test.email@example.com'
TEST_DB_ID = 1
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
TEST_MCDI_FORMAT_NAME = 'standard'
TEST_FORMAT = models.MCDIFormat(
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
        'meta': {'mcdi_type': 'standard'}
    }
)

TEST_STUDY_ID = '456'
TEST_STUDY_ID_2 = '789'
TEST_SNAPSHOT_ID = 789
TEST_ITEMS_EXCLUDED = 3
TEST_EXTRA_CATEGORIES = 4
TEST_SESSION_NUM = 4
TEST_LANGUAGES = 'english'
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


class EnterDataControllersTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        self.app = daxlabbase.app
        self.app.debug = True

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
        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(db_util, 'load_mcdi_model')
        self.mox.StubOutWithMock(db_util, 'insert_snapshot')
        
        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        db_util.load_mcdi_model(TEST_MCDI_FORMAT_NAME).AndReturn(TEST_FORMAT)
        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)

        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        db_util.load_mcdi_model('invalid format').AndReturn(None)

        self.mox.ReplayAll()

        with self.app.test_client() as client:
            
            with client.session_transaction() as sess:
                sess['email'] = TEST_EMAIL

            url = '/base/enter_data/%s' % TEST_MCDI_FORMAT_NAME
            client.get(url)

            with client.session_transaction() as sess:
                err = sess.get(constants.ERROR_ATTR, None)
                self.assertEqual(err, None)

            url = '/base/enter_data/%s' % 'invalid format'
            client.get(url)

            with client.session_transaction() as sess:
                self.assertTrue(constants.ERROR_ATTR in sess)

    def test_missing_enter_data_params(self):
        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(db_util, 'load_mcdi_model')
        self.mox.StubOutWithMock(db_util, 'insert_snapshot')

        for i in range(0, 10):
            user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
            db_util.load_mcdi_model(TEST_MCDI_FORMAT_NAME).AndReturn(
                TEST_FORMAT)

        self.mox.ReplayAll()

        target_url = '/base/enter_data/%s' % TEST_MCDI_FORMAT_NAME

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

    def test_invalid_enter_data_params(self):
        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(db_util, 'load_mcdi_model')
        self.mox.StubOutWithMock(db_util, 'insert_snapshot')

        for i in range(0, 8):
            user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
            db_util.load_mcdi_model(TEST_MCDI_FORMAT_NAME).AndReturn(
                TEST_FORMAT)


        self.mox.ReplayAll()

        target_url = '/base/enter_data/%s' % TEST_MCDI_FORMAT_NAME

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

    def test_success_enter_data(self):
        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(db_util, 'load_mcdi_model')
        self.mox.StubOutWithMock(db_util, 'load_percentile_model')
        self.mox.StubOutWithMock(math_util, 'find_percentile')
        self.mox.StubOutWithMock(db_util, 'insert_snapshot')

        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        db_util.load_mcdi_model(TEST_MCDI_FORMAT_NAME).AndReturn(
            TEST_FORMAT)
        db_util.load_percentile_model(MALE_TEST_PERCENTILE_NAME).AndReturn(
            TEST_PERCENTILE_MODEL
        )
        math_util.find_percentile('test details', 3, TEST_AGE, 6).AndReturn(
            TEST_PERCENTILE
        )
        db_util.insert_snapshot(
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_WORD_ENTRIES
        )

        self.mox.ReplayAll()

        target_url = '/base/enter_data/%s' % TEST_MCDI_FORMAT_NAME

        with self.app.test_client() as client:
            
            with client.session_transaction() as sess:
                sess['email'] = TEST_EMAIL

            client.post(target_url, data=TEST_SUCCESSFUL_PARAMS)

            with client.session_transaction() as sess:
                error_attr = sess.get(constants.ERROR_ATTR, None)
                confirmation_attr = sess.get(constants.CONFIRMATION_ATTR, None)
                self.assertEqual(error_attr, None)
                self.assertNotEqual(confirmation_attr, None)

    def test_lookup_studies_by_global_id(self):
        ret_list = [
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2,
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2
        ]

        self.mox.StubOutWithMock(filter_util, 'run_search_query')
        self.mox.StubOutWithMock(user_util, 'get_user')

        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        filter_util.run_search_query(
            [models.Filter('child_id', 'eq', TEST_DB_ID)],
            constants.SNAPSHOTS_DB_TABLE
        ).AndReturn(ret_list)

        self.mox.ReplayAll()

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
        returned_studies = result['studies']
        
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

    def test_lookup_studies_by_study_id(self):
        ret_list = [
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2,
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2
        ]

        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(filter_util, 'run_search_query')
        self.mox.StubOutWithMock(db_util, 'lookup_global_participant_id')

        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        db_util.lookup_global_participant_id(TEST_STUDY, TEST_STUDY_ID
            ).AndReturn(TEST_DB_ID)
        filter_util.run_search_query(
            [models.Filter('child_id', 'eq', TEST_DB_ID)],
            constants.SNAPSHOTS_DB_TABLE
        ).AndReturn(ret_list)

        self.mox.ReplayAll()

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
        returned_studies = result['studies']
        
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

    def test_edit_metadata(self):
        new_birthday = '2014/12/28'
        new_languages = ['english', 'spanish']
        ret_list = [
            TEST_EXPECTED_SNAPSHOT,
            TEST_EXPECTED_SNAPSHOT_2,
        ]

        self.mox.StubOutWithMock(user_util, 'get_user')
        self.mox.StubOutWithMock(db_util, 'update_participant_metadata')
        self.mox.StubOutWithMock(filter_util, 'run_search_query')
        self.mox.StubOutWithMock(
            recalc_util,
            'recalculate_ages_and_percentiles'
        )
        
        user_util.get_user(TEST_EMAIL).AndReturn(TEST_USER)
        db_util.update_participant_metadata(
            TEST_DB_ID,
            constants.FEMALE,
            new_birthday,
            constants.EXPLICIT_TRUE,
            new_languages
        )
        filter_util.run_search_query(
            [models.Filter('child_id', 'eq', TEST_DB_ID)],
            constants.SNAPSHOTS_DB_TABLE
        ).AndReturn(ret_list)
        recalc_util.recalculate_ages_and_percentiles(ret_list)

        self.mox.ReplayAll()

        with self.app.test_client() as client:

            with client.session_transaction() as sess:
                sess['email'] = TEST_EMAIL

            new_metadata = {
                'global_id': TEST_DB_ID,
                'gender': constants.FEMALE,
                'birthday': new_birthday,
                'hard_of_hearing': constants.EXPLICIT_TRUE,
                'languages': ','.join(new_languages)
            }

            client.post(
                '/base/edit_data',
                data=new_metadata
            )
