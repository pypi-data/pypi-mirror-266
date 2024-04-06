'''
Performs unit tests on the Pioneer REST Client and API.

Usage:
  api_tests.py [--authlegacy=<bool>] [--user=<str>] [--pass=<str>] [--appkey=<str>] [--wksp=<str>]
  api_tests.py (-h | --help)

Examples:
  api_tests.py --user=username --pass=secret
  api_tests.py --user=username --appkey=op_guid --wksp=sqa

Options:
  -h, --help
  -a, --authlegacy=<bool>  true for legacy username password method [default: False]
  -u, --user=<str>         API user [default:]
  -p, --pass=<str>         API password [default:]
  -k, --appkey=<str>       non expiring auth key [default:]
  -w, --wksp=<str>         wksp to use [default: Studio]
'''

import api
import time
import unittest
from collections import OrderedDict
from contextlib import redirect_stderr, redirect_stdout
from dateutil.parser import parse
from datetime import datetime, timedelta, timezone
from difflib import Differ
from docopt import docopt
from io import StringIO
from json import dump, dumps, loads
from numbers import Number
from os import listdir, path
from random import randint
from re import compile, fullmatch, match
from sys import platform
from threading import Thread
from typing import Any, Dict, Final, List, Literal, Tuple, TypedDict, Optional
from uuid import uuid4


class Templates(TypedDict):
    '''Typing database templates data structure.'''

    baseId: int
    baselineSchemaVersion: str
    id: float
    isDefault: bool
    longDescription: str
    media: list
    name: str
    pgTemplateName: str
    schema: str
    schemaReleaseStatus: str
    shortDescription: str
    tags: list
    templateType: str
    templateVersion: str


class TestApi(unittest.TestCase):
    '''A series of Pioneer REST API unit tests.

    OVERRIDE
    docopt configuration passed into the module will override the default static members

    STATIC MEMBERS
    USERNAME    required to be issued api key
    USERPASS    required to be issued api key
    WKSP        file storage to use for IO operations
    APPKEY      non expiring authentication key
    AUTH_LEGACY true for legacy username password authentication method
    '''

    USERNAME: Optional[str] = None
    USERPASS: Optional[str] = None
    WKSP: str = 'Studio'
    APPKEY: Optional[str] = None
    AUTH_LEGACY: bool = False
    TEST_SYSTEM: bool = False

    ANURA_STATUS: Tuple[str, ...] = (
        'current',
        'deprecated',
        'legacy',
        'preview',
        'release candidate',
        'retired',
        'stable',
    )

    DB_ARCHIVE_STATES: Tuple[str, ...] = (
        'archive-restore-error',
        'archive-restoring',
        'archived',
    )

    @classmethod
    def setUpClass(cls) -> None:
        '''Execute before test methods are ran.
        Ensure cache directories and test data inputs are available in target wksp.
        '''

        cls.API = api.Api(
            auth_legacy=cls.AUTH_LEGACY,
            appkey=cls.APPKEY,
            un=cls.USERNAME,
            pw=cls.USERPASS,
            test_system=cls.TEST_SYSTEM,
        )
        print(cls.API._domain)
        cls.__jobkey_quick: str = ''
        cls.API._log_active = True

        # directory references
        cls.dir_local_current: str = path.dirname(__file__)
        cls.dir_testdata_local: str = path.join(cls.dir_local_current, 'quick_tests')
        assert path.exists(cls.dir_testdata_local)
        assert len(listdir(cls.dir_testdata_local)) >= 1
        cls.dir_testdata_remote: str = 'quick_tests'
        cls.files_testdata_local: list[str] = []
        cls.files_testdata_remote: list[str] = []
        cls.py_sleep: str = ''
        cls.py_bash: str = ''
        cls.py_quick: str = ''
        cls.py_sidecar: str = ''
        cls.py_job_aware: str = ''

        # get all directories from wksp
        resp = cls.API.wksp_files(cls.WKSP, '/quick_tests/')
        files_remote: list[str] = [f['filePath'] for f in resp['files']]

        # comb over local test data and map to destination file structure
        for f in listdir(cls.dir_testdata_local):
            local: str = path.join(cls.dir_testdata_local, f)
            if path.isfile(local) is False:
                continue
            elif path.getsize(local) == 0:
                continue
            dest: str = path.join(cls.dir_testdata_remote, f)
            cls.files_testdata_local.append(local)
            cls.files_testdata_remote.append(dest)
            if dest.endswith('sleep.py'):
                cls.py_sleep = dest
            elif dest.endswith('quick.py'):
                cls.py_quick = dest
            elif dest.endswith('bash.py'):
                cls.py_bash = dest
            elif dest.endswith('sidecar.py'):
                cls.py_sidecar = dest
            elif dest.endswith('job_key_self_aware.py'):
                cls.py_job_aware = dest

            # upload local test data to destination
            for idx, local in enumerate(cls.files_testdata_local):
                dest = cls.files_testdata_remote[idx]
            res: list[str] = [f for f in files_remote if dest in f]
            if len(res) == 0:
                print(f'uploading {dest}')
                resp = cls.API.wksp_file_upload(
                    cls.WKSP, file_path_dest=dest, file_path_local=local
                )

    @classmethod
    def tearDownClass(cls) -> None:
        '''Execute after all tests have ran and clean up.'''

        # remove test databases
        dbs: List[Dict[str, Any]] = cls.API._database_by_name(r'unittest.+\d{13}', wildcard=True)
        for d in dbs:
            print(f"Deleting database dust bunny {d['name']}")
            cls.API.database_delete(d['name'])

        # remove test db archives
        archived_dbs: Dict[str, Any] = cls.API.database_archived()
        archived_ids: List[str] = [
            d['id'] for d in archived_dbs['storages'] if d['name'].startswith('unittest_archive_')
        ]
        for id in archived_ids:
            cls.API.database_delete(id)

        # remove test cache entries
        cache_store = cls.API._cache_store()
        keys_to_delete: list[str] = [key for key in cache_store.keys() if 'cache_' in key]
        for key in keys_to_delete:
            cls.API._cache_entry_delete(key)

        # remove test secrets
        cls.API.secrets.cache_clear()
        secrets: List[Dict[str, Any]] = cls.API._secret_select_all(desc='unittest')
        for s in secrets:
            cls.API.secret_delete(s['name'])

    def _compare_list_of_dict_keys(self, items) -> None:
        '''What is the commonality and difference between a list of dictionaries.'''

        unique_sets: List[set] = []
        keys_unique = set()
        for i in items:
            s = set(i)
            if s not in unique_sets:
                unique_sets.append(s)
                for k in s:
                    keys_unique.add(k)

        keys_common_missing = set()
        for u in unique_sets:
            diff = u ^ keys_unique
            keys_common_missing = keys_common_missing | diff

        keys_common = keys_unique ^ keys_common_missing

        print(f'{len(items)} total dicts')
        print(f'{len(unique_sets)} unique dict sets:')
        print(f'{len(keys_unique)} unique keys: {sorted(keys_unique)}')
        print(f'{len(keys_common)} common keys: {sorted(keys_common)}')
        print(f'{len(keys_common_missing)} vanishing keys: {sorted(keys_common_missing)}')

    def _compare_words(self, str1: str, str2: str, echo: bool = False) -> List[str]:
        '''Identify any word differences between two strings.

        :param str1: The first string for comparison.
        :param str2: The second string for comparison.
        :param echo: True to print diffs to stdout.
        '''

        if not isinstance(str1, str):
            raise TypeError(f'str1 must be a string, but got {type(str1)}')
        if not isinstance(str2, str):
            raise TypeError(f'str2 must be a string, but got {type(str2)}')

        # Split the input strings by spaces to compare words
        words1: List[str] = str1.split()
        words2: List[str] = str2.split()

        # Compare the words
        differ = Differ()
        diff = list(differ.compare(words1, words2))
        diffs: List[str] = []
        char_position: int = 0

        for i, line in enumerate(diff):
            if line.startswith(('+', '-')):
                # Extract the plus and minus symbol from the word
                symbol, word = line[:1], line[2:]

                # Minus is unique to sequence 1, plus is unique to sequence 2
                word_list = words1 if symbol == '-' else words2

                # TODO OE-9034 index will return first match found
                word_index = word_list.index(word) if word in word_list else None
                if word_index is None:
                    continue

                # Get two words before and after the difference
                start_idx = max(0, word_index - 2)
                end_idx = min(len(word_list), word_index + 3)
                context_words = word_list[start_idx:end_idx]
                context = ' '.join(context_words)
                char_position = ' '.join(word_list).find(context)
                diffs.append(f'{symbol}{context} (position: {char_position})')
                if echo:
                    print(f'{symbol}{context} (position: {char_position})')

        return diffs

    def _database_ensure_exist(self, name: str = 'pg_unittest') -> None:
        '''Database must exist for db unit tests.'''

        # cache is for 10 seconds
        exists: bool = self.API.storagename_database_exists(name)
        if exists:
            resp: Dict[str, Any] = self.API.storage(name)
            assert resp.get('crash') is None
        else:
            self.API.database_create(name, desc='common db for unit tests', backups=False)

    def _databases_utilized_by_unittest(self, all: bool = False) -> List[Dict[str, Any]]:
        '''Which databases are used by unit tests.

        :param all: bool, False returns only temporary unittest databases
        '''

        dbs: List[Dict[str, Any]] = []
        if all is False:
            dbs = self.API._database_by_name(r'unittest.+\d{13}', wildcard=True)
        else:
            dbs = self.API._database_by_name('unittest', wildcard=True)
        return dbs

    def _date_iso_today(self, date_str) -> bool:
        '''Verify date string is ISO format and occurred today.'''

        today: bool = True

        if self._date_isoformat(date_str) is False:
            return False

        dt: datetime = parse(date_str)
        now: datetime = datetime.utcnow()

        if (
            dt.tzname() != 'UTC'
            or dt.year != now.year
            or dt.month != now.month
            or dt.day != now.day
        ):
            today = False

        return today

    def _date_isoformat(self, date_str: str) -> bool:
        '''Verify date/datetime string is iso format.

        2020-01-20T00:39:12.361762 - absence of trailing Z indicates local time.
        2020-01-20T00:39:12.361762Z - Zulu/UTC timezone was included.'''

        dt: datetime
        try:
            if date_str.endswith('Z'):
                dt = datetime.fromisoformat(date_str[:-1])
            else:
                dt = datetime.fromisoformat(date_str)
            return isinstance(dt, datetime)
        except ValueError:
            return False

    def _deserialize_pip_output(self, std_out: str) -> List[Dict[str, Any]]:
        '''Deserialization of `pip list --format json` from standard output.'''

        if isinstance(std_out, str) is False:
            raise TypeError(f'std_out must be a string, but got {type(std_out)}')
        if len(std_out) < 58:
            raise ValueError(f'len of std_out is {std_out}, too short')

        # remove cli earmarking from std_out
        m = match(r"(.|\n)+format\sjson'\}\n", std_out)
        if m is None:
            raise ValueError('could not match std_out')

        return loads(std_out.lstrip(m.group()))

    def _json_from_file(self, file_path: str = 'output.json'):
        '''Convert file to json.'''

        cwd: str = path.dirname(__file__)
        fp: str = path.join(cwd, file_path)

        with open(fp, 'r') as f:
            return loads(f.read())

    def _json_to_file(self, json: Dict[str, Any], file_path: str = 'output.json') -> None:
        '''Convert a dict to json file.'''

        cwd: str = path.dirname(__file__)
        fp: str = path.join(cwd, file_path)

        with open(fp, 'w') as f:
            dump(json, f, indent=2, sort_keys=True)

    def _job_keys(self, d: Dict[str, Any]) -> None:
        '''The essential keys on the job record.'''

        self.assertTrue(bool(fullmatch(self.API.re_uuid4, d['jobKey'], flags=2)))
        self.assertIn(d['status'], self.API.JOBSTATES)
        self.assertIsInstance(d['phase'], str)

        self.assertIsInstance(d['submittedDatetime'], str)
        self.assertTrue(self._date_isoformat(d['submittedDatetime']))

        if d.get('startDatetime'):
            self.assertIsInstance(d['startDatetime'], str)
            self.assertTrue(self._date_isoformat(d['startDatetime']))

        if d['status'] in ('running', 'canceling'):
            self.assertIn(d['phase'], ('initializing', 'executing', 'finalizing', 'out-of-memory'))

        if d.get('endDatetime'):
            self.assertIsInstance(d['endDatetime'], str)
            self.assertTrue(self._date_isoformat(d['endDatetime']))
            self.assertIsInstance(d['runTime'], str)
            self.assertIn(d['status'], self.API.JOBSTATES_TERMINAL_RUNTIME)

        if d['phase'] == 'out-of-memory':
            self.assertIn(d['status'], ('running', 'canceling', 'error'))

        # jobs dashboard
        if d.get('billedTime'):
            self.assertIsInstance(d['billedTime'], str)
        if d.get('runRate'):
            self.assertIsInstance(d['runRate'], Number)

        # job info details vary
        if d.get('jobInfo') and len(d) > 0:
            self.assertIsInstance(d['jobInfo'], dict)
            self.assertIsInstance(d['jobInfo']['command'], str)
            self.assertIn(
                d['jobInfo']['command'], ('run', 'run_model', 'tadpole', 'presolve', 'utility')
            )
            self.assertIsInstance(d['jobInfo']['directoryPath'], str)
            self.assertIsInstance(d['jobInfo']['filename'], str)

            if d['jobInfo'].get('commandArgs'):
                self.assertIsInstance(d['jobInfo']['commandArgs'], str)
            if d['jobInfo'].get('errorFile'):
                self.assertIsInstance(d['jobInfo']['errorFile'], bool)
            if d['jobInfo'].get('resultFile'):
                self.assertIsInstance(d['jobInfo']['resultFile'], bool)

            self.assertIsInstance(d['jobInfo']['resourceConfig'], dict)
            self.assertIsInstance(d['jobInfo']['resourceConfig']['cpu'], str)
            self.assertIsInstance(d['jobInfo']['resourceConfig']['name'], str)
            self.assertIsInstance(d['jobInfo']['resourceConfig']['ram'], str)
            self.assertIsInstance(d['jobInfo']['resourceConfig']['run_rate'], Number)

            if d['jobInfo']['resourceConfig'].get('cpu_limit'):
                self.assertIsInstance(d['jobInfo']['resourceConfig']['cpu_limit'], str)
            if d['jobInfo']['resourceConfig'].get('cpu_request'):
                self.assertIsInstance(d['jobInfo']['resourceConfig']['cpu_request'], str)
            if d['jobInfo']['resourceConfig'].get('memory_limit'):
                self.assertIsInstance(d['jobInfo']['resourceConfig']['memory_limit'], str)
            if d['jobInfo']['resourceConfig'].get('memory_request'):
                self.assertIsInstance(d['jobInfo']['resourceConfig']['memory_request'], str)

            self.assertIsInstance(d['jobInfo']['tags'], str)
            self.assertIsInstance(d['jobInfo']['timeout'], int)
            self.assertIsInstance(d['jobInfo']['workspace'], str)

    def _job_prereq(self) -> None:
        '''For running test methods in isolation.'''

        resp = self.API.wksp_job_start(
            self.WKSP, self.py_quick, tags='unittest_prereq', resourceConfig='mini'
        )
        self.assertEqual(resp['result'], 'success')
        self.__jobkey_quick = resp['jobKey']
        # BUG ledger and metrics should be immediately available when job is running
        res: bool = self.API.util_job_monitor(self.WKSP, resp['jobKey'], stop_when='done')
        self.assertTrue(res)

    def _storage_common(self, d: Dict[str, Any]) -> None:
        '''Device attributes expected across afs, wksp, onedrive, and postgres storage devices.'''

        self.assertIsInstance(d['annotations'], dict)
        self.assertIsInstance(d['bytesUsed'], int)
        self.assertGreater(d['bytesUsed'], -1)
        self.assertIsInstance(d['created'], int)
        self.assertTrue(d['description'] is None or isinstance(d['description'], str))
        self.assertIsInstance(d['id'], str)
        self.assertIsInstance(d['labels'], dict)
        self.assertTrue(d['lockoutReason'] is None or isinstance(d['lockoutReason'], str))
        self.assertIsInstance(d['name'], str)
        self.assertIsInstance(d['notes'], str)
        self.assertIsInstance(d['shortcuts'], list)
        if len(d['shortcuts']) >= 1:
            for s in d['shortcuts']:
                self.assertIsInstance(s['driveId'], str)
                self.assertIsInstance(s['driveName'], str)
                self.assertIsInstance(s['id'], str)
                self.assertIsInstance(s['name'], str)
                self.assertIsInstance(s['path'], str)
                self.assertIsInstance(s['type'], str)
        self.assertIsInstance(d['tags'], str)
        self.assertIsInstance(d['type'], str)
        self.assertIsInstance(d['updated'], int)

    def _storage_azure_afs(self, d: Dict[str, Any]) -> None:
        '''SSD device attributes for get device and devices.'''

        self._storage_common(d)
        self.assertIsInstance(d['capacity'], int)
        self.assertEqual(d['capacity'], 100)
        self.assertIsInstance(d['internal'], bool)
        self.assertTrue(d['internal'])
        self.assertIsInstance(d['tier'], str)
        self.assertEqual(d['tier'], 'Premium')

    def _storage_azure_workspace(self, d: Dict[str, Any]) -> None:
        '''Workspace device attributes for get device and devices.'''

        self._storage_common(d)
        self.assertIsInstance(d['capacity'], int)
        self.assertTrue(4 <= d['capacity'] <= 512)  # default is 4 but some are custom
        self.assertIsInstance(d['internal'], bool)
        self.assertIsInstance(d['tier'], str)
        self.assertEqual(d['tier'], 'TransactionOptimized')
        self.assertIsInstance(d['workspaceKey'], str)
        self.assertEqual(len(d['workspaceKey']), 25)
        self.assertTrue(d['workspaceKey'].startswith('workspace'))

    def _storage_database(self, d: Dict[str, Any]) -> None:
        '''Database attributes for get device and devices.'''

        self._storage_common(d)
        self.assertIsInstance(d['bytesUsedLastUpdated'], int)
        self.assertIsInstance(d['dbname'], str)
        self.assertIsInstance(d['defaultSchema'], str)
        self.assertIsInstance(d['host'], str)
        self.assertIsInstance(d['port'], int)
        self.assertIsInstance(d['schemaStatus'], str)
        with self.subTest():
            self.assertTrue(d['schemaStatus'] in ('error', 'invalid', 'valid'))  # BUG OE-8954
        self.assertIsInstance(d['schemaStatusLastUpdated'], Number)
        self.assertIsInstance(d['schemaVersion'], str)
        self.assertIsInstance(d['user'], str)

        # empty pg database vs anura schema
        if d['defaultSchema'].startswith('anura_2_'):
            self.assertRegex(d['schemaVersion'], r'2\.[4-9]\.\d+')
            self.assertIsInstance(d['schemaReleaseStatus'], str)
            release_status: bool = True if d['schemaReleaseStatus'] in self.ANURA_STATUS else False
            self.assertTrue(release_status)
            self.assertIsInstance(d['schemaStatusLastValidated'], Number)
        else:
            self.assertIn(d['defaultSchema'], ('"$user"', 'public'))
            self.assertTrue(len(d['schemaVersion']) == 0)

    def _storage_onedrive(self, d: dict) -> None:
        '''Onedrive storage attributes for get device and devices.'''

        self._storage_common(d)

        self.assertIsInstance(d['authenticated'], int)
        dt: datetime = datetime.fromtimestamp(d['authenticated'] / 1000)
        self.assertGreaterEqual(dt.year, 2020)

        # connect is not in get devices call due to real time performance
        # self.assertIsInstance(d['connected'], bool)
        self.assertIsInstance(d['capacity'], int)

        self.assertIsInstance(d['homeAccountId'], str)
        self.assertIsInstance(d['internal'], bool)

        self.assertIsInstance(d['username'], str)

    def test_000_init_api_version_bad(self) -> None:
        '''Recover from a bad api version provided.'''

        bad_version: int = 99

        with redirect_stderr(StringIO()) as err:
            a = api.Api(auth_legacy=self.AUTH_LEGACY, version=bad_version, ut=True)
            output: str = err.getvalue().strip()

        self.assertGreater(output.find(f'API version {bad_version} not supported'), -1)
        self.assertRegex(a.api_version, r'app/v0/')

    def test_000_init_password_missing(self) -> None:
        '''Get password uses a secret stream and input will not echo.'''

        if platform != 'linux':
            self.skipTest('only linux has timed inputs')

        with redirect_stdout(StringIO()) as out:
            try:
                api.Api(auth_legacy=True, un=self.USERNAME, ut=True)
            except (EOFError, TimeoutError):
                pass
            output: str = out.getvalue().strip()

        self.assertEqual(output.find('REQUIRED API User Password'), -1)

    def test_000_prereq(self) -> None:
        '''Ensure job data is available to test against.'''

        resp: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP, self.py_quick, tags='unittest_preseed', resourceConfig='mini'
        )
        self.assertEqual(resp['result'], 'success')
        self.__jobkey_quick = resp['jobKey']
        stime: float = time.time()
        print('Pre-seeding by running a new job')
        res: bool = self.API.util_job_monitor(
            self.WKSP, resp['jobKey'], stop_when='done', secs_max=300
        )
        delta: float = time.time() - stime
        print(f'Job completed {res}, time spent {delta}')
        self.assertLessEqual(delta, 240.0)

    def test_auth_apikey(self) -> None:
        '''Api key is required for all api calls with legacy authentication.'''

        self.assertIsNotNone(
            self.API.auth_apikey
        ) if self.API.auth_method_legacy else self.assertIsNone(self.API.auth_apikey)

    def test_auth_apikey_expiration(self) -> None:
        '''Ensure api key is refreshed and not expired.'''

        if self.API.auth_method_legacy:
            self.assertGreater(self.API.auth_apikey_expiry, datetime.now().timestamp())
        else:
            self.assertEqual(self.API.auth_apikey_expiry, 0)

    def test_auth_header(self) -> None:
        '''Request header must have valid apikey or appkey.'''

        if self.API.auth_method_legacy:
            self.assertEqual(self.API.auth_req_header['x-api-key'], self.API.auth_apikey)
        else:
            self.assertEqual(self.API.auth_req_header['x-app-key'], self.API.auth_appkey)

    def test_account_info(self) -> None:
        '''Account properties.'''

        resp = self.API.account_info()
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 10)

        self.assertIsInstance(resp['created'], int)
        dt: datetime = datetime.fromtimestamp(resp['created'] / 1000)
        self.assertGreaterEqual(dt.year, 2019)
        now: datetime = datetime.utcnow()
        self.assertLessEqual(dt.year, now.year)

        self.assertIsInstance(resp['email'], str)

        self.assertIsInstance(resp['id'], str)
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['id'], flags=2)))

        self.assertIsInstance(resp['name'], str)
        self.assertGreaterEqual(len(resp['name']), 3)

        self.assertIsInstance(resp['subscriptionName'], str)
        self.assertIn(
            resp['subscriptionName'], ('Standard', 'Professional', 'empcustom', 'Free')
        )  # OE-9002

        self.assertIsInstance(resp['limits'], dict)
        self.assertEqual(len(resp['limits']), 3)
        self.assertIsInstance(resp['limits']['concurrentJobs'], int)
        self.assertIsInstance(resp['limits']['databaseCount'], int)
        self.assertIsInstance(resp['limits']['fileStorageGb'], int)
        self.assertEqual(resp['limits']['fileStorageGb'], 500)  # max possible

        self.assertIsInstance(resp['roles'], dict)
        self.assertEqual(len(resp['roles']), 1)
        self.assertIsInstance(resp['roles']['api'], list)
        roles = (
            'api-access',
            'api-beast',
            'api-internal',
            'api-proxy',
            'api-share',
            'pioneer-team',
            'preview-schema',
            'reveal-admin',
            'user-initiated-db-upgrade',
        )
        for r in resp['roles']['api']:
            self.assertIsInstance(r, str)
            self.assertIn(r, roles)

        self.assertIsInstance(resp['usage'], dict)
        self.assertEqual(len(resp['usage']), 5)
        self.assertIsInstance(resp['usage']['databaseCount'], int)
        self.assertIsInstance(resp['usage']['databaseStorageBytes'], int)
        dbs_total_bytes: int = resp['usage']['databaseStorageBytes']
        self.assertIsInstance(resp['usage']['fileStorageCount'], int)
        self.assertIsInstance(resp['usage']['fileStorageGb'], int)
        self.assertIsInstance(resp['usage']['workspaceCount'], int)
        self.assertGreaterEqual(resp['usage']['databaseCount'], 0)
        self.assertLessEqual(resp['usage']['databaseCount'], resp['limits']['databaseCount'])
        self.assertTrue(0 < resp['usage']['fileStorageCount'] < 10)
        self.assertTrue(0 < resp['usage']['workspaceCount'] < 10)
        self.assertLessEqual(
            resp['usage']['fileStorageGb'],
            resp['limits']['fileStorageGb'] * resp['usage']['fileStorageCount'],
        )

        self.assertIsInstance(resp['username'], str)
        if self.API.auth_username:
            self.assertEqual(resp['username'], self.API.auth_username)

        dbs: List[Dict[str, Any]] = self.API.databases()
        total: int = 0
        for db in dbs:
            total += db['bytesUsed']

        self.assertEqual(dbs_total_bytes, total)

        # limits per rate plan
        if resp['subscriptionName'] == 'Standard':
            self.assertEqual(resp['limits']['concurrentJobs'], 3)
            self.assertEqual(resp['limits']['databaseCount'], 25)
        elif resp['subscriptionName'] == 'Professional':
            self.assertEqual(resp['limits']['concurrentJobs'], 10)
            self.assertEqual(resp['limits']['databaseCount'], 100)
        elif resp['subscriptionName'] == 'empcustom':
            self.assertEqual(resp['limits']['concurrentJobs'], 50)
            self.assertEqual(resp['limits']['databaseCount'], 100)
            self.assertGreater(resp['email'].find('@optilogic.com'), -1)

    def test_account_jobs(self) -> None:
        '''User jobs from any workspace.'''

        job_count: int = 50
        resp: Dict[str, Any] = self.API._account_jobs(max_jobs=job_count)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 4)

        self.assertIsInstance(resp['subsetCount'], int)
        self.assertEqual(resp['subsetCount'], job_count)
        self.assertIsInstance(resp['totalCount'], int)

        self.assertIsInstance(resp['jobs'], list)
        for job in resp['jobs']:
            self._job_keys(job)

            self.assertIsInstance(job['cancelable'], bool)
            self.assertIsInstance(job['canHaveResult'], bool)
            self.assertIsInstance(job['submittedTimeStamp'], int)

            if job['status'] in self.API.JOBSTATES_TERMINAL_RUNTIME:
                self.assertTrue(job['canHaveResult'])
                self.assertIsInstance(job['billedTime'], str)
                self.assertIsInstance(job['billedTimeMs'], Number)
                self.assertIsInstance(job['endDatetime'], str)
                self.assertIsInstance(job['endTimeStamp'], int)
                self.assertIsInstance(job['runTime'], str)
                self.assertIsInstance(job['runTimeMs'], int)
                self.assertIsInstance(job['startDatetime'], str)
                self.assertIsInstance(job['startTimeStamp'], int)
            elif job['status'] in 'submitted':
                self.assertIsNone(job['startDatetime'])
            elif job['status'] in self.API.JOBSTATES_ACTIVE:
                self.assertIsNone(job['endDatetime'])

            # self.assertFalse(job['canHaveResult'])  # BUG 6710

    def test_account_jobs_active(self) -> None:
        '''Compare active account jobs count to all active wksp jobs.'''

        # TODO OE-9033
        start_new_job: bool = bool(randint(0, 1))
        if start_new_job:
            self.API.wksp_job_start(
                self.WKSP, self.py_sleep, tags='unittest_jobs_active', resourceConfig='mini'
            )

        active_account: int = 0
        resp: Dict[str, Any] = self.API._account_jobs(max_jobs=200)
        for job in resp['jobs']:
            if job['status'] in self.API.JOBSTATES_ACTIVE:
                active_account += 1

        active_wksp: int = self.API._jobs_active
        self.assertEqual(active_account, active_wksp)
        if start_new_job:
            self.assertGreater(active_account, 0)
            self.assertGreater(active_wksp, 0)

    def test_account_storage_devices(self) -> None:
        '''Get a list of available storage devices in an account.'''

        resp = self.API.account_storage_devices()
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertGreaterEqual(resp['count'], 1)
        self.assertIsInstance(resp['storages'], list)
        with self.subTest():
            for device in resp['storages']:
                d = OrderedDict(sorted(device.items()))
                if d['type'] == 'azure_afs':
                    self.assertEqual(len(d), 16)
                    self._storage_azure_afs(d)
                if d['type'] == 'azure_workspace':
                    self.assertEqual(len(d), 17)
                    self._storage_azure_workspace(d)
                elif d['type'] == 'onedrive':
                    self.assertEqual(len(d), 18)
                    self._storage_onedrive(d)
                elif d['type'] == 'postgres_db':
                    self.assertEqual(len(d), 24)
                    self._storage_database(d)

    def test_account_usage(self) -> None:
        '''Atlas and andromeda information.'''

        resp = self.API._account_usage()
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['andromeda'], dict)
        self.assertIsInstance(resp['atlas'], dict)
        self.assertEqual(len(resp), 3)

        self.assertIsInstance(resp['andromeda']['jobsLastThirty'], int)
        self.assertIsInstance(resp['andromeda']['jobsMostRecent'], int)
        self.assertIsInstance(resp['andromeda']['jobsTimeLastThirty'], Number)
        self.assertIsInstance(resp['andromeda']['jobsTimeTotal'], float)
        self.assertIsInstance(resp['andromeda']['jobsTotal'], int)
        self.assertIsInstance(resp['andromeda']['periodHours'], Number)
        self.assertEqual(len(resp['andromeda']), 6)
        self.assertEqual(len(str(resp['andromeda']['jobsMostRecent'])), 13)
        dt: datetime = datetime.fromtimestamp(
            resp['andromeda']['jobsMostRecent'] / 1000, timezone.utc
        )
        now: datetime = datetime.now(timezone.utc)
        self.assertEqual(dt.year, now.year)
        self.assertEqual(dt.month, now.month)

        self.assertIsInstance(resp['atlas'], dict)
        if (
            self.API._domain != 'https://api.optilogic.app'
            and resp['atlas'].get('lastLogin') is None
        ):
            self.assertEqual(len(resp['atlas']), 3)
        else:
            self.assertEqual(len(resp['atlas']), 4)
            self.assertIsInstance(resp['atlas']['lastLogin'], int)
            self.assertEqual(len(str(resp['atlas']['lastLogin'])), 13)
            dt: datetime = datetime.fromtimestamp(resp['atlas']['lastLogin'] / 1000)
            self.assertIsInstance(dt, datetime)
        self.assertIsInstance(resp['atlas']['periodHours'], Number)
        self.assertIsInstance(resp['atlas']['task'], dict)
        self.assertIsInstance(resp['atlas']['workspaceCount'], int)
        self.assertIsInstance(resp['atlas']['task'], dict)
        self.assertIsInstance(resp['atlas']['task']['durationCurrentWeek'], Number)
        self.assertIsInstance(resp['atlas']['task']['durationLastThirty'], Number)
        self.assertIsInstance(resp['atlas']['task']['durationTotal'], float)
        self.assertIsInstance(resp['atlas']['task']['lastDuration'], float)
        self.assertIsInstance(resp['atlas']['task']['lastRunStart'], int)
        self.assertIsInstance(resp['atlas']['task']['runCurrentWeek'], int)
        self.assertIsInstance(resp['atlas']['task']['runlastThirty'], int)
        self.assertIsInstance(resp['atlas']['task']['runTotal'], int)
        self.assertEqual(len(resp['atlas']['task']), 8)
        self.assertEqual(len(str(resp['atlas']['task']['lastRunStart'])), 13)
        dt: datetime = datetime.fromtimestamp(resp['atlas']['task']['lastRunStart'] / 1000)
        self.assertIsInstance(dt, datetime)

    def test_account_workspaces(self) -> None:
        '''Check all workspaces properties.'''

        resp = self.API.account_workspaces()
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)

        wksp_exists: bool = False
        for wksp in resp['workspaces']:
            self.assertRegex(wksp['name'], '^[\\w-]+$')
            self.assertEqual(len(wksp['key']), 25)
            self.assertIn(wksp['stack'], ['Optilogic', 'Gurobi'])
            self.assertIn(wksp['status'], ['STARTING', 'RUNNING', 'STOPPING', 'STOPPED'])
            self.assertRegex(wksp['status'], '\\w{3,}')

            # https://en.wikipedia.org/wiki/ISO_8601
            dt_wksp_creation: datetime = parse(wksp['createdon'])
            self.assertGreaterEqual(dt_wksp_creation.year, 2020)

            if wksp['name'] == self.WKSP:
                wksp_exists = True

        self.assertTrue(wksp_exists)

    def test_account_workspace_count(self) -> None:
        '''Account info and workspaces both return wksp count.'''

        resp = self.API.account_info()
        ws_count: int = self.API.account_workspace_count
        self.assertEqual(resp['usage']['workspaceCount'], ws_count)

    @unittest.skip('cant delete a wksp atm')
    def test_account_workspace_create(self) -> None:
        '''Creating a new workspace.'''

        resp = self.API.account_workspace_create('delete_me')
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['name'], 'delete_me')
        self.assertEqual(resp['stack'], 'Gurobi')

    def test_account_workspace_create_crash(self) -> None:
        '''Expected to not create the same workspace twice.'''

        resp = self.API.account_workspace_create('Studio')
        self.assertEqual(resp['crash'], True)
        self.assertEqual(resp['exception'].response.status_code, 400)

    def test_account_workspace_delete(self) -> None:
        '''Deleting a newly created workspace.'''

        with self.assertRaises(NotImplementedError):
            self.API.account_workspace_delete('delete_me')

    def test_andromeda_configs(self) -> None:
        '''Memory and CPU configurations for Andromeda.'''

        NAMES = (
            'mini',
            '4XS',
            '3XS',
            '2XS',
            'XS',
            'S',
            'M',
            'L',
            'XL',
            '2XL',
            '3XL',
            '4XL',
            'overkill',
        )
        resp: Dict[str, Any] = self.API.andromeda_machine_configs()
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 4)
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['defaultConfigName'], str)
        self.assertIsInstance(resp['resourceConfigs'], list)

        self.assertEqual(resp['count'], 13)
        self.assertEqual(resp['defaultConfigName'], '3XS')
        self.assertEqual(len(resp['resourceConfigs']), 13)

        for rc in resp['resourceConfigs']:
            self.assertIsInstance(rc, dict)
            self.assertEqual(len(rc.keys()), 5)
            self.assertTrue(rc.get('name'))
            self.assertTrue(rc.get('description'))
            self.assertTrue(rc.get('cpu'))
            self.assertTrue(rc.get('ram'))
            self.assertTrue(rc.get('runRate'))

            self.assertIsInstance(rc['name'], str)
            self.assertIsInstance(rc['description'], str)
            self.assertIsInstance(rc['cpu'], Number)
            self.assertIsInstance(rc['ram'], Number)
            self.assertIsInstance(rc['runRate'], Number)

            self.assertIn(rc['name'], NAMES)
            self.assertRegex((rc['description']), r'(\d{1,2}\sCPU).+(\d{1,3}[GM]b RAM)')

    def test_andromeda_utilities(self) -> None:
        '''Get a list of all CLI utilities that can run in Andromeda.'''

        resp: Dict[str, Any] = self.API._andromeda_utilities()
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        # TODO OE-8726 specific utilities are to be added
        self.assertGreater(resp['count'], 0)
        self.assertIsInstance(resp['utilities'], list)
        for d in resp['utilities']:
            self.assertIsInstance(d, dict)
            self.assertEqual(len(d.keys()), 5)
            self.assertIsInstance(d['name'], str)
            self.assertIsInstance(d['description'], str)
            self.assertIsInstance(d['version'], str)
            self.assertIsInstance(d['stable'], bool)
            self.assertIsInstance(d['hasParameters'], bool)

    def test_andromeda_utility(self) -> None:
        '''Get details of a CLI utility.'''

        utils: Dict[str, Any] = self.API._andromeda_utilities()
        item: int = randint(0, len(utils['utilities']) - 1)
        util_name: str = utils['utilities'][item]['name']
        util_preview: bool = True if utils['utilities'][item]['stable'] is False else False

        # TODO OE-8726 test a specific utility
        resp: Dict[str, Any] = self.API._andromeda_utility(util_name, util_preview)
        self.assertIsInstance(resp, dict)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 6)
        self.assertIsInstance(resp['name'], str)
        self.assertIsInstance(resp['description'], str)
        self.assertIsInstance(resp['version'], str)
        self.assertIsInstance(resp['stable'], bool)
        self.assertIsInstance(resp['parameters'], list)
        for d in resp['parameters']:
            # TODO OE-8726 a specific utility will have specific parameters
            self.assertIsInstance(d, dict)
            self.assertTrue(all(isinstance(k, str) for k in d.keys()))

    def test_andromeda_utility_run(self) -> None:
        '''Run a named CLI utility in Andromeda.'''

        utils: Dict[str, Any] = self.API._andromeda_utilities()
        item: int = randint(0, len(utils['utilities']) - 1)
        util_name: str = utils['utilities'][item]['name']
        util_preview: bool = True if utils['utilities'][item]['stable'] is False else False
        cmd = 'utility'
        tag = 'unittest_utility'
        size = '3xs'
        secs = 60

        # TODO OE-8726 commandArgs is CLI mechanism for input parameters to py module
        resp: Dict[str, Any] = self.API.wksp_job_start(
            wksp=self.WKSP,
            command=cmd,
            utility_name=util_name,
            utility_preview_version=util_preview,
            tags='unittest_utility',
            resourceConfig=size,  # TODO OE-8732 casing is inconsistent
            timeout=secs,
        )

        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'Job submitted')
        self.assertIsInstance(resp['jobKey'], str)
        self.assertIsInstance(resp['jobInfo'], dict)
        self.assertEqual(resp['jobInfo']['command'], cmd)
        self.assertTrue(tag in resp['jobInfo']['tags'])
        self.assertEqual(resp['jobInfo']['resourceConfig']['name'].lower(), size)
        self.assertEqual(resp['jobInfo']['timeout'], secs)

    def test_andromeda_utility_run_bad_utility_name(self) -> None:
        '''Attempt to run a CLI utility that does not exist in Andromeda.'''

        resp: Dict[str, Any] = self.API.wksp_job_start(
            wksp=self.WKSP,
            command='utility',
            utility_name='does_not_exist',
        )
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['crash'], True)
        self.assertEqual(resp['resp'].status_code, 404)
        self.assertEqual(resp['exception'].response.reason, 'Not Found')
        err: Dict[str, str] = loads(resp['response_body'])
        self.assertEqual(err['error'], 'Utility name and/or version not found')

    def test_andromeda_utility_run_cant_finish(self) -> None:
        '''Run a CLI utility that is intentionally cut short.'''

        utils: Dict[str, Any] = self.API._andromeda_utilities()
        item: int = randint(0, len(utils['utilities']) - 1)
        util_name: str = utils['utilities'][item]['name']
        util_preview: bool = True if utils['utilities'][item]['stable'] is False else False
        cmd = 'utility'
        tag = 'unittest_utility'
        size = 'mini'
        secs = 1

        resp: Dict[str, Any] = self.API.wksp_job_start(
            wksp=self.WKSP,
            command=cmd,
            utility_name=util_name,
            utility_preview_version=util_preview,
            tags=tag,
            resourceConfig=size,
            timeout=secs,
        )

        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'Job submitted')
        self.assertIsInstance(resp['jobKey'], str)
        self.assertIsInstance(resp['jobInfo'], dict)
        self.assertEqual(resp['jobInfo']['command'], cmd)
        self.assertTrue(tag in resp['jobInfo']['tags'])
        self.assertEqual(resp['jobInfo']['resourceConfig']['name'], size)

        # add cache entry to be verified run results later
        k = 'utility_run_incomplete'
        added: bool = self.API._cache_entry_upsert(k, resp['jobKey'])
        self.assertTrue(added)

    def test_andromeda_utility_verify_cant_finish(self) -> None:
        '''Utility run was intentionally cut short or may not have enough memory.'''

        k = 'utility_run_incomplete'
        timestamp: float = self.API._cache_entry_get_updated(k)
        now: float = time.time()
        if now - timestamp > 300.0:
            self.skipTest('utility has not been run in the last 60 seconds')

        # TODO OE-8726 verify utility run was cut short
        # timeout cut it short or ran out of memory

    def test_api_server_online(self) -> None:
        '''Check if api service is up and running.'''

        self.assertTrue(self.API.api_server_online)

    def test_api_version(self) -> None:
        '''Only version zero is supported.'''

        self.assertTrue(self.API.api_version.endswith('v0/'))

    def test_cache_store_add(self) -> None:
        '''Add a cache entry to cache store.'''

        ns: int = time.perf_counter_ns()
        k = f'cache_{ns}'

        # assert cache entry does not exist
        timestamp: float = self.API._cache_entry_get_updated(k)
        self.assertIsInstance(timestamp, float)
        self.assertEqual(timestamp, -1.0)

        # add cache entry
        added: bool = self.API._cache_entry_upsert(k, ns)
        self.assertTrue(added)

        # assert key type is correct
        val = self.API._cache_entry_get_value(k)
        self.assertIsInstance(val, int)
        self.assertEqual(val, ns)

        # clean up and remove unit tests cache entries!
        self.API._cache_entry_delete(k)

    def test_cache_store_update(self) -> None:
        '''Update a cache entry in cache store.'''

        ns: int = time.perf_counter_ns()
        k = f'cache_{ns}'
        v = True

        # add cache entry
        added_time: float = time.time()
        added: bool = self.API._cache_entry_upsert(k, v)
        self.assertTrue(added)

        timestamp_add: float = self.API._cache_entry_get_updated(k)
        self.assertIsInstance(timestamp_add, float)
        self.assertGreater(timestamp_add, added_time)

        val = self.API._cache_entry_get_value(k)
        self.assertIsInstance(val, bool)
        self.assertEqual(val, v)

        # update cache entry
        updated_time: float = time.time()
        updated: bool = self.API._cache_entry_upsert(k, False)
        self.assertTrue(updated)
        timestamp_update: float = self.API._cache_entry_get_updated(k)
        self.assertGreater(timestamp_update, updated_time)
        self.assertGreater(updated_time, added_time)
        diff: float = timestamp_update - timestamp_add
        self.assertLess(diff, 1.0)

        # clean up and remove unit tests cache entries!
        self.API._cache_entry_delete(k)

    def test_cache_store_update_bad_type(self) -> None:
        '''Try to update a cache entry where its value type is not supported.'''

        ns: int = time.perf_counter_ns()
        k = f'cache_{ns}'

        updated: bool = self.API._cache_entry_upsert(k, time)  # type: ignore
        self.assertFalse(updated)
        timestamp: float = self.API._cache_entry_get_updated(k)
        self.assertIsInstance(timestamp, float)
        self.assertEqual(timestamp, -1.0)

    def test_cache_store_delete(self) -> None:
        '''Delete a cache entry from cache store.'''

        ns: int = time.perf_counter_ns()
        k = f'cache_{ns}'

        added: bool = self.API._cache_entry_upsert(k, ns)
        self.assertTrue(added)
        deleted: bool = self.API._cache_entry_delete(k)
        self.assertTrue(deleted)

    def test_cache_store_get_nonexistent(self) -> None:
        '''Try to get a non-existent cache entry.'''

        ns: int = time.perf_counter_ns()
        k = f'cache_{ns}'

        timestamp: float = self.API._cache_entry_get_updated(k)
        self.assertIsInstance(timestamp, float)
        self.assertEqual(timestamp, -1.0)

    def test_database_archive(self) -> None:
        '''Archive a postgres database.'''

        ns: int = time.perf_counter_ns()
        name: str = f'unittest_archive_{ns}'
        self._database_ensure_exist(name)
        db: Dict[str, Any] = self.API.database(name)

        # assert db is available before archiving
        self.API.account_storage_devices.cache_clear()
        dbs: List[Dict[str, Any]] = self.API.databases()
        self.assertTrue(any([d for d in dbs if d['id'] == db['id']]))

        # archive db
        now: float = time.time()
        resp: Dict[str, Any] = self.API.database_archive(name)
        self.assertEqual(resp['result'], 'success')

        # diff attributes between archived db and original db
        db_latest: Dict[str, Any] = self.API.database(name)
        self.assertEqual(db_latest['archiveCategory'], 'archived')
        with self.subTest():
            self.assertEqual(db['tags'], db_latest['tags'])  # BUG OE-9598
        diff: set[str] = set(db) ^ set(db_latest)
        self.assertNotIn('schemaStatusLastValidated', diff)

        # time diff to archive db
        self.assertIsInstance(db_latest['userArchiveLastUpdated'], int)
        archive_delta: float = now - db_latest['userArchiveLastUpdated'] / 1000
        self.assertLessEqual(archive_delta, 60)

        # assert list of databases no longer contains archived db
        self.API.account_storage_devices.cache_clear()
        dbs: List[Dict[str, Any]] = self.API.databases()
        self.assertFalse(any([d for d in dbs if d['id'] == db['id']]))

    def test_database_archive_complete(self) -> None:
        '''Archiving a postgres database is complete.'''

        resp: Dict[str, Any] = self.API.database_archived()
        self.assertEqual(resp['result'], 'success')
        for d in resp['storages']:
            self._storage_database(d)
            self.assertEqual(d['archiveCategory'], 'archived')

    def test_database_archive_delete(self) -> None:
        '''Delete a database archive.'''

        # create a db to archive
        ns: int = time.perf_counter_ns()
        name: str = f'unittest_archive_delete_{ns}'
        self._database_ensure_exist(name)

        # archive db
        resp: Dict[str, Any] = self.API.database_archive(name)
        self.assertEqual(resp['result'], 'success')

        # delete archived db
        resp = self.API.database_archive_delete(name)
        self.assertEqual(resp['result'], 'success')

    def test_database_archive_restore(self) -> None:
        '''Restore an archived postgres database.'''

        archived: Dict[str, Any] = self.API.database_archived()
        if archived['count'] == 0:
            self.skipTest('no archived databases')

        archived_ids: List[str] = [
            d['id'] for d in archived['storages'] if d['name'].startswith('unittest_archive_')
        ]

        resp: Dict[str, Any] = self.API.database_archive_restore(archived_ids[0])
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['jobKey'], str)
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['jobKey'], flags=2)))
        self.assertEqual(len(resp.keys()), 2)

        # TODO OE-9229

    def test_database_archived(self) -> None:
        '''Get a list of archived databases.'''

        resp: Dict[str, Any] = self.API.database_archived()
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['storages'], list)
        self.assertEqual(len(resp.keys()), 3)
        self.assertEqual(len(resp['storages']), resp['count'])
        for d in resp['storages']:
            self._storage_database(d)
            self.assertIn(d['archiveCategory'], self.DB_ARCHIVE_STATES)
            self.assertIsInstance(d['userArchiveLastUpdated'], int)

    def test_database_clone(self) -> None:
        '''Duplicate a postgres database.'''

        self._database_ensure_exist()
        name_new: str = f'pg_unittest_{time.perf_counter_ns()}'
        name: str = 'pg_unittest'
        resp: Dict[str, str] = self.API.database_clone(name, name_new)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 3)
        self.assertIsInstance(resp['jobKey'], str)
        self.assertIsInstance(resp['storageId'], str)
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['jobKey'], flags=2)))
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['storageId'], flags=2)))

        # TODO OE-9036 explicit database created verification via system jobs
        # 1) db_clone
        # 2) db_analyze

        # 1-2) implicit wait for db_clone, and db_analyze to complete
        db_src: Dict[str, Any] = self.API.database(name)
        db_clone: Dict[str, Any] = {}
        ready: bool = False
        while ready is False:
            db_clone = self.API.database(name_new)
            if db_clone.get('lockoutReason') is None:
                ready = True
                break
            time.sleep(10)

        # 3) db now exists
        # self.assertEqual(db_clone['annotations']['sharedByUserName'], self.API.auth_username)
        self.assertEqual(db_clone['description'], 'Duplicated via OptiPy')
        self.assertIsNone(db_clone['annotations'].get('shared'))
        dbc = OrderedDict(sorted(db_clone.items()))
        self._storage_database(dbc)

        bytes_diff: int = abs(db_src['bytesUsed'] - db_clone['bytesUsed'])
        bytes_diff_percent: float = bytes_diff / db_src['bytesUsed']
        self.assertLess(bytes_diff_percent, 1.0)

        self.assertEqual(db_src['defaultSchema'], db_clone['defaultSchema'])
        self.assertEqual(db_src['notes'], db_clone['notes'])
        self.assertEqual(db_src['schemaReleaseStatus'], db_clone['schemaReleaseStatus'])
        self.assertEqual(db_src['schemaStatus'], db_clone['schemaStatus'])
        self.assertEqual(db_src['schemaVersion'], db_clone['schemaVersion'])

        src_schema_update: datetime = datetime.fromtimestamp(
            db_src['schemaStatusLastUpdated'] / 1000
        )
        clone_schema_update: datetime = datetime.fromtimestamp(
            db_clone['schemaStatusLastUpdated'] / 1000
        )
        schema_update_diff: timedelta = clone_schema_update - src_schema_update
        self.assertLessEqual(schema_update_diff.seconds, 3600)

        src_schema_valid: datetime = datetime.fromtimestamp(
            db_src['schemaStatusLastValidated'] / 1000
        )
        clone_schema_valid: datetime = datetime.fromtimestamp(
            db_clone['schemaStatusLastValidated'] / 1000
        )
        schema_valid_diff: timedelta = src_schema_valid - clone_schema_valid
        self.assertLessEqual(schema_valid_diff.seconds, 0)

        self.assertEqual(db_src['tags'], db_clone['tags'])
        self.assertEqual(db_src['type'], db_clone['type'])

    def test_database_connections(self) -> None:
        '''Get a list of active database connections.'''

        nano_secs: str = str(time.perf_counter_ns())
        thread = Thread(
            target=lambda: self.API.sql_query('pg_unittest', f'/*{nano_secs}*/ SELECT pg_sleep(30)')
        )
        thread.start()  # fire and forget
        now: datetime = datetime.now(timezone.utc)
        time.sleep(2)

        resp: Dict[str, Any] = self.API.database_connections('pg_unittest')
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['rowCount'], int)
        self.assertGreaterEqual(resp['rowCount'], 1)
        self.assertIsInstance(resp['queryResults'], list)
        self.assertEqual(len(resp['queryResults']), resp['rowCount'])

        KEYS: Tuple[str, ...] = (
            'application',
            'Query Start',
            'query',
            'State Change',
            'state',
            'Transaction Start',
        )
        query_found: bool = False
        for row in resp['queryResults']:
            self.assertIsInstance(row, dict)
            self.assertEqual(len(row.keys()), 8)
            for k in KEYS:
                self.assertIn(k, row.keys())
            self.assertIsInstance(row['application'], str)
            self.assertIsInstance(row['Query Start'], str)
            self.assertIsInstance(row['query'], str)
            self.assertIsInstance(row['State Change'], str)
            self.assertIsInstance(row['state'], str)
            self.assertTrue(
                row['Transaction Start'] is None or isinstance(row['Transaction Start'], str)
            )
            self.assertTrue(row['Wait Event'] is None or isinstance(row['Wait Event'], str))
            self.assertTrue(row['Wait Type'] is None or isinstance(row['Wait Type'], str))

            if row['query'].find('SELECT pg_sleep(') > -1:
                query_found = True
                self.assertGreater(row['query'].find('OptiPy'), -1)
                self.assertEqual(row['Wait Event'], 'PgSleep')
                self.assertEqual(row['Wait Type'], 'Timeout')

                dt: datetime = parse(row['Query Start'])
                self.assertTrue(dt.tzname(), 'UTC')
                self.assertEqual(dt.year, now.year)
                self.assertEqual(dt.month, now.month)
                self.assertEqual(dt.day, now.day)

        self.assertTrue(query_found)

    def test_database_connections_terminate(self) -> None:
        '''Terminate a database connection.'''

        resp: Dict[str, Any] = self.API.database_connections_terminate('pg_unittest')
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['rowCount'], int)
        self.assertIsInstance(resp['queryResults'], list)
        self.assertEqual(resp['rowCount'], 0)
        self.assertEqual(len(resp['queryResults']), 0)

    def test_database_create_delete(self) -> None:
        '''Create a postgres database then delete.'''

        bots: List[float] = self.API._database_templates_by_name('Global', wildcard=True)
        self.assertGreaterEqual(len(bots), 1)
        db_name: str = f'pg_unittest_{time.perf_counter_ns()}'

        # create database
        label: dict[str, bool] = {'no-backup': True}
        resp: dict = self.API.database_create(
            db_name,
            desc=f'unittest {db_name}',
            template_id=bots[0],
            backups=False,
            labels=label,
        )
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['storageId'], str)
        self.assertEqual(len(resp['storageId']), 36)

        # verify database was created
        db: Dict[str, Any] = self.API.database(db_name)
        self._storage_database(db)
        self.assertGreater(db['tags'].find('no-backup'), -1)
        self.assertDictEqual(db['labels'], {'no-backup': True})

        # delete database
        resp = self.API.storage_delete(db_name)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')

    def test_database_create_delete_all(self) -> None:
        '''For each database template create a database, verify then delete it.'''

        k = 'db_create_delete_all'

        timestamp: float = self.API._cache_entry_get_updated(k)
        now: float = time.time()
        delta = timedelta(seconds=now - timestamp)
        if delta.total_seconds() < 604_800:  # skip if ran in last 7 days
            self.skipTest(f'test ran {str(delta)} ago, skipping less than 7 days')

        self.API._cache_entry_upsert(k, True)
        resp_templates: Dict[str, Any] = self.API.database_templates()

        for t in resp_templates['templates']:
            # create database
            db_name: str = (
                f'pg_unittest_all_templates_{t["id"]}-{t["name"]}_{time.perf_counter_ns()}'
            )
            db_desc: str = f'unittest {db_name}'
            resp: dict = self.API.database_create(
                db_name, desc=db_desc, template=t['name'], backups=False, labels={'no-backup': True}
            )
            self.assertIsInstance(resp['result'], str)
            self.assertEqual(resp['result'], 'success')
            self.assertIsInstance(resp['storageId'], str)
            self.assertEqual(len(resp['storageId']), 36)

            # verify
            db: Dict[str, Any] = self.API.database(db_name)
            self._storage_database(db)
            self.assertEqual(db['id'], resp['storageId'])
            self.assertEqual(db['name'], db_name)
            self.assertEqual(db['description'], db_desc)
            self.assertEqual(db['schemaStatus'], 'valid')

            print(f'\n\n{t["id"]}, {t["name"]}')
            print(f"  tags: {len(db['tags'])},\n  {db['labels']}\n  {db['annotations']}")
            self.assertGreater(db['tags'].find('no-backup'), -1)
            self.assertDictEqual(db['labels'], {'no-backup': True})

            if db['annotations'].get('sourceBaseTemplateId'):
                # 2023-10-30 anura_2_7_11_clean shows this still exists
                self.assertIsInstance(db['annotations']['sourceBaseTemplateId'], Number)
                # self.assertEqual(db['annotations']['sourceBaseTemplateName'], template_name)  # OE-9071
            if db['annotations'].get('sourceTemplateSetId'):
                self.assertIsInstance(db['annotations']['sourceTemplateSetId'], Number)
                # self.assertEqual(db['annotations']['sourceTemplateSetName'], template_name)  # OE-9071

            # delete database
            resp = self.API.storage_delete(db_name)
            self.assertIsInstance(resp['result'], str)
            self.assertEqual(resp['result'], 'success')

    def test_database_create_id_wrong(self) -> None:
        '''Create a postgres database with a template name instead of id.'''

        template_name: str = 'China Exit Risk Strategy'
        db_name: str = f'pg_unittest_{time.perf_counter_ns()}'

        # get template id
        ids: List[float] = self.API._database_templates_by_name(template_name)
        self.assertEqual(len(ids), 1)

        # create database with template id derived from the template name
        resp: Dict[str, Any] = self.API.database_create(
            db_name, desc=f'unittest {db_name} {template_name}', template_id=ids[0], backups=False
        )
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['storageId'], str)
        self.assertEqual(len(resp['storageId']), 36)

        # verify database creation
        db: Dict[str, Any] = self.API.database(db_name)
        self.assertEqual(db['result'], 'success')
        self.assertEqual(db['name'], db_name)
        self.assertEqual(db['type'], 'postgres_db')
        self.assertEqual(db['id'], resp['storageId'])
        self.assertGreater(db['description'].find(template_name), -1)
        self.assertGreater(db['tags'].find('no-backup'), -1)

    def test_database_create_failure_already_exists(self) -> None:
        '''Attempt creating a postgres database but cannot db name is already used.'''

        db_name: str = 'cant'

        if self.API.storagename_database_exists(db_name) is False:
            resp: Dict[str, Any] = self.API.database_create(db_name)
            self.assertEqual(resp['result'], 'success')

        with self.assertRaises(AssertionError):
            self.API.database_create(db_name)

    def test_database_create_failure_template_bad(self) -> None:
        '''Attempt creating a postgres database with bad template id that does not exist.'''

        db_name: str = f'pg_unittest_{time.perf_counter_ns()}'
        resp = self.API.database_create(name=db_name, template='does_not_exist')

        self.assertEqual(resp['crash'], True)
        self.assertEqual(resp['exception'].response.status_code, 400)

    def test_database_customization(self) -> None:
        '''Perform customizations on a database and verify.'''

        CUSTOM: str = '''
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'analytics'
                AND column_name = 'custom'
            ) THEN
                ALTER TABLE analytics ADD COLUMN custom TEXT;
            END IF;

            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'dirt_bikes'
            ) THEN
            CREATE TABLE dirt_bikes (
                manf TEXT,
                year INT,
                model TEXT,
                price INT,
                freight INT
            );
            INSERT INTO dirt_bikes (manf, year, model, price, freight)
            VALUES
                ('GasGas', 2023, 'MC 50', 4599, 410),
                ('KTM', 2023, '50sx', 4699, 385),
                ('Husqvarna', 2023, 'TC 50', 4799, 385);
            END IF;
        END $$;

        '''

        # apply customizations
        self.API.sql_query('pg_unittest', CUSTOM)

        # verify customizations
        resp: Dict[str, Any] = self.API.database_customizations('pg_unittest')
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 2)
        self.assertIsInstance(resp['schemas'], list)
        self.assertGreaterEqual(len(resp['schemas']), 1)
        for s in resp['schemas']:
            self.assertIsInstance(s['name'], str)
            self.assertIsInstance(s['tables'], list)
            self.assertIsInstance(s['views'], list)
            for t in s['tables']:
                self.assertIsInstance(t['name'], str)
                self.assertIsInstance(t['columns'], list)
                self.assertIsInstance(t['isCustom'], bool)
                # TODO if custom table, assert table is truly from anura schema
                for c in t['columns']:
                    self.assertIsInstance(c['name'], str)
                    self.assertIsInstance(c['dataType'], str)
            for v in s['views']:
                self.assertIsInstance(v['name'], str)
                self.assertIsInstance(v['columns'], list)
                self.assertIsInstance(v['isCustom'], bool)
                for c in v['columns']:
                    self.assertIsInstance(c['name'], str)
                    self.assertIsInstance(c['dataType'], str)

        # clean up
        DELETE_CUSTOMIZATIONS = '''
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'analytics'
                AND column_name = 'custom'
                ) THEN
                    ALTER TABLE analytics DROP COLUMN custom;
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'dirt_bikes'
                ) THEN
                    DROP TABLE dirt_bikes;
            END IF;
        END $$;
        '''
        self.API.sql_query('pg_unittest', DELETE_CUSTOMIZATIONS)

    def test_database_customization_none(self) -> None:
        '''Database has no customizations.'''

        CUSTOM_COLUMN = '''
        SELECT
        EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'analytics'
            AND column_name = 'custom'
        );
        '''
        resp = self.API.sql_query('pg_unittest', CUSTOM_COLUMN)
        self.assertFalse(resp['queryResults'][0]['exists'])

        CUSTOM_TABLE = '''
        SELECT
        EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'dirt_bikes'
        );
        '''
        resp = self.API.sql_query('pg_unittest', CUSTOM_TABLE)
        self.assertFalse(resp['queryResults'][0]['exists'])

        resp: Dict[str, Any] = self.API.database_customizations('pg_unittest')
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 2)
        self.assertIsInstance(resp['schemas'], list)
        self.assertEqual(len(resp['schemas']), 0)

    def test_database_export(self) -> None:
        '''Initiate job to export database named empty table, nonEmptyTables, and custom sql query.'''

        DB: Final[str] = 'pg_unittest'
        G: Final[str] = 'nonEmptyTables'
        Q: Final[str] = 'SELECT datname FROM pg_database'
        TBL: Final[List[str]] = ['advancedqueueingdetails']

        with self.assertRaises(ValueError):
            self.API.database_export(DB, named=[])

        with self.assertRaises(ValueError):
            self.API.database_export(DB, group='does_not_exist')  # type: ignore

        with self.assertRaises(AssertionError):
            self.API.database_export(DB, query='ha')

        # xls format mirrors csv and includes two extra files: .xls, readme.txt
        resp: Dict[str, Any] = self.API.database_export(
            DB, named=TBL, group=G, query=Q, format='xls'
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 10)
        self.assertIsInstance(resp['format'], str)
        self.assertIsInstance(resp['jobKey'], str)
        self.assertIsInstance(resp['message'], str)
        self.assertIsInstance(resp['sourceGroup'], str)
        self.assertIsInstance(resp['sourceList'], list)
        self.assertIsInstance(resp['sourceQuery'], str)
        self.assertIsInstance(resp['sourceSchema'], str)
        self.assertIsInstance(resp['storageId'], str)
        self.assertIsInstance(resp['storageName'], str)
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['jobKey'])))
        self.assertEqual(
            resp['message'], 'DB Data Export job submitted. Poll job info for current job status.'
        )
        self.assertIsNone(resp.get('multipleFiles'))
        self.assertEqual(resp['sourceGroup'], G)
        self.assertEqual(resp['sourceList'], TBL)
        self.assertEqual(resp['sourceQuery'], Q)
        self.assertTrue(bool(fullmatch(self.API.re_uuid4, resp['storageId'])))
        self.assertEqual(resp['storageName'], DB)

        # TODO OE-8120
        # 1) poll job key status
        # 2) download zip
        # 3) unpack zip
        # 4) verify csv output folder: csv, source_query, metadata
        # 5) if xls format, verify xls output file and readme.txt

    def test_database_no_backups(self) -> None:
        '''Unittest databases should not be eligible for system backups.'''

        dbs: List[Dict[str, Any]] = self._databases_utilized_by_unittest(all=True)
        for db in dbs:
            with self.subTest():
                self.assertGreater(db['tags'].find('no-backup'), -1)  # BUG OE-9598

    def test_database_objects(self) -> None:
        '''Tables and views with stats.'''

        self._database_ensure_exist()
        resp: Dict[str, Any] = self.API.database_objects('pg_unittest')
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['schemas'], list)
        for schema in resp['schemas']:
            self.assertEqual(len(schema.keys()), 6)
            self.assertIsInstance(schema['isDefault'], bool)
            self.assertIsInstance(schema['name'], str)
            self.assertIsInstance(schema['tableCount'], int)
            self.assertIsInstance(schema['tables'], list)
            self.assertIsInstance(schema['viewCount'], int)
            self.assertIsInstance(schema['views'], list)
            self.assertEqual(len(schema['tables']), schema['tableCount'])
            self.assertEqual(len(schema['views']), schema['viewCount'])
            for t in schema['tables']:
                self.assertIsInstance(t['name'], str)
                self.assertIsInstance(t['rows'], int)
                self.assertGreaterEqual(len(t['name']), 1)
                self.assertGreaterEqual(t['rows'], 0)

        # tables only
        resp: Dict[str, Any] = self.API.database_objects('pg_unittest', views=False)
        self.assertEqual(resp['result'], 'success')
        for schema in resp['schemas']:
            self.assertIsNone(schema.get('views'))

        # views only
        resp: Dict[str, Any] = self.API.database_objects('pg_unittest', tables=False)
        self.assertEqual(resp['result'], 'success')
        for schema in resp['schemas']:
            self.assertIsNone(schema.get('tables'))

    def test_database_schemas(self) -> None:
        '''Currently only anura schemas.'''

        resp = self.API.database_schemas_anura()
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['schemas'], dict)
        self.assertEqual(len(resp), 2)
        self.assertEqual(len(resp['schemas']), 1)
        self.assertTrue(resp['schemas'].get('anura', False))
        for schema_type in resp['schemas'].keys():
            for v in resp['schemas'][schema_type]:
                self.assertEqual(len(v), 10)
                self.assertIsInstance(v['generalAvailabilityDate'], str)
                self.assertIsInstance(v['description'], str)
                self.assertIsInstance(v['notes'], str)
                self.assertIsInstance(v['schemaName'], str)
                self.assertRegex(v['schemaName'], r'anura_2_[4-9]')
                self.assertIsInstance(v['schemaVersion'], str)
                self.assertRegex(v['schemaVersion'], r'2\.[4-9]\.\d+')
                self.assertIsInstance(v['status'], str)
                self.assertIn(v['status'], self.ANURA_STATUS)
                self.assertTrue(self._date_isoformat(v['generalAvailabilityDate']))
                if v.get('defaultMigrationDate'):
                    self.assertIsInstance(v['defaultMigrationDate'], str)
                    self.assertTrue(self._date_isoformat(v['defaultMigrationDate']))
                if v.get('endOfLifeDate'):
                    self.assertIsInstance(v['endOfLifeDate'], str)
                    self.assertTrue(self._date_isoformat(v['endOfLifeDate']))
                if v.get('limitedAvailabilityDate'):
                    self.assertIsInstance(v['limitedAvailabilityDate'], str)
                    self.assertTrue(self._date_isoformat(v['limitedAvailabilityDate']))
                if v.get('techPreviewDate'):
                    self.assertIsInstance(v['techPreviewDate'], str)
                    self.assertTrue(self._date_isoformat(v['techPreviewDate']))

    def test_database_tables(self) -> None:
        '''List of schemas and tables.'''

        self._database_ensure_exist()
        db = self.API.account_storage_device(type='postgres_db')
        resp = self.API.database_tables(db['name'])
        self.assertIsInstance(resp['result'], str)
        for schema in resp['schemas']:
            self.assertIsInstance(schema['name'], str)
            self.assertIsInstance(schema['tables'], int)
            self.assertIsInstance(schema['is_default_schema'], bool)
        self.assertIsInstance(resp['tables'], list)

        if len(resp['tables']) >= 1:
            self.assertIsInstance(resp['tables'][0]['name'], str)
            self.assertIsInstance(resp['tables'][0]['rows'], int)
            self.assertIsInstance(resp['tables'][0]['schema'], str)

    def test_database_tables_empty(self) -> None:
        '''Clear the data in specified tables.'''

        db: str = 'pg_unittest_empty_bom_table'
        tbl: str = 'billsofmaterials'
        anura_versions: list[str] = sorted(
            {t for t in self.API.DATABASE_TEMPLATES if t.find('anura') > -1}, reverse=True
        )
        tid: str = anura_versions[0]
        schema: str = tid[0:9]

        # assert db exists
        exists: bool = self.API.storagename_database_exists(db)
        if exists:
            resp: Dict[str, Any] = self.API.storage(db)
            schema = resp['defaultSchema']
        else:
            self.API.database_create(name=db, template=tid, backups=False)

        # assert db has data
        QUERY_ROWS: str = f'SELECT COUNT(*) FROM {schema}.{tbl}'
        resp = self.API.sql_query(db, QUERY_ROWS)
        rows: int = int(resp['queryResults'][0]['count'])
        if rows == 0:
            query_insert = f'INSERT INTO {schema}.{tbl}\n'
            query_insert += (
                '(bomname, productname, producttype, quantity, quantityuom, status, notes)\n'
            )
            query_insert += f"VALUES\n('Unittest', 'RM1', 'Component', '1', 'EA', 'Exclude', 'unittest{time.time()}')"
            self.API.sql_query(db, query_insert)
            rows = 1

        # remove table data dry run
        resp = self.API.database_tables_empty(db, tables=[tbl], dry_run=True)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 4)
        self.assertTrue(resp['dryRun'])
        self.assertIsInstance(resp['emptied'], list)
        self.assertEqual(len(resp['emptied']), 1)
        self.assertEqual(resp['emptied'][0], f'{schema}.{tbl}')
        self.assertIsInstance(resp['failed'], list)
        self.assertEqual(len(resp['failed']), 0)
        resp = self.API.sql_query(db, QUERY_ROWS)
        rows_dry_run: int = int(resp['queryResults'][0]['count'])
        self.assertEqual(rows, rows_dry_run)

        # remove table data
        resp = self.API.database_tables_empty(db, tables=[tbl])
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 4)
        self.assertFalse(resp['dryRun'])
        self.assertIsInstance(resp['emptied'], list)
        self.assertEqual(len(resp['emptied']), 1)
        self.assertEqual(resp['emptied'][0], f'{schema}.{tbl}')
        self.assertIsInstance(resp['failed'], list)
        self.assertEqual(len(resp['failed']), 0)
        resp = self.API.sql_query(db, QUERY_ROWS)
        rows_cleared: int = int(resp['queryResults'][0]['count'])
        self.assertEqual(rows_cleared, 0)

    def test_database_template_sets(self) -> None:
        '''Distinct categories of database templates.'''

        resp: Dict[str, Any] = self.API.database_template_sets()
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['schemas'], list)
        self.assertEqual(len(resp.keys()), 3)
        self.assertEqual(len(resp['schemas']), resp['count'])
        self.assertIsInstance(resp['schemas'][0]['name'], str)
        self.assertIsInstance(resp['schemas'][0]['templateSets'], list)

        STATUS = ('stable', 'legacy')
        for t in resp['schemas'][0]['templateSets']:
            self.assertEqual(len(t.keys()), 7)
            self.assertIsInstance(t['id'], int)
            self.assertIsInstance(t['name'], str)
            self.assertIsInstance(t['shortDescription'], str)
            self.assertIsInstance(t['longDescription'], str)
            self.assertIsInstance(t['availableReleaseStatuses'], list)
            self.assertGreaterEqual(len(t['availableReleaseStatuses']), 1)
            self.assertTrue(any([True for s in STATUS if s in t['availableReleaseStatuses']]))
            self.assertIsInstance(t['tags'], list)
            self.assertTrue(
                all([True if isinstance(tag, str) and len(tag) > 0 else False for tag in t['tags']])
            )
            self.assertIsInstance(t['media'], list)
            pat = compile(r'(https):\/\/(youtu.be)\/([\w-]+)$')
            if len(t['media']) > 0:
                self.assertIsInstance(t['media'][0], dict)
                self.assertIsInstance(t['media'][0]['type'], str)
                self.assertEqual(t['media'][0]['type'], 'yt')
                self.assertIsInstance(t['media'][0]['url'], str)
                m = pat.fullmatch(t['media'][0]['url'])
                self.assertIsNotNone(m)

    def test_database_templates(self) -> None:
        '''Empty db or anura schemas.'''

        known_templates: List[Dict[str, Any]] = self._json_from_file(
            'quick_tests/database_templates.json'
        )
        templates: Dict[Number, Dict[str, Any]] = {t['id']: t for t in known_templates}

        resp: Dict[str, Any] = self.API.database_templates()
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 3)
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['templates'], list)

        for t in resp['templates']:
            self.assertIsInstance(t, dict)
            self.assertTrue(issubclass(type(templates[t['id']]['baseId']), type(t['baseId'])))
            self.assertTrue(
                issubclass(
                    type(templates[t['id']]['baselineSchemaVersion']),
                    type(t['baselineSchemaVersion']),
                )
            )
            self.assertTrue(issubclass(type(templates[t['id']]['id']), type(t['id'])))
            self.assertTrue(issubclass(type(templates[t['id']]['isDefault']), type(t['isDefault'])))
            self.assertTrue(
                issubclass(type(templates[t['id']]['longDescription']), type(t['longDescription']))
            )
            self.assertTrue(issubclass(type(templates[t['id']]['media']), type(t['media'])))
            self.assertTrue(issubclass(type(templates[t['id']]['name']), type(t['name'])))
            self.assertTrue(
                issubclass(type(templates[t['id']]['pgTemplateName']), type(t['pgTemplateName']))
            )
            self.assertTrue(issubclass(type(templates[t['id']]['schema']), type(t['schema'])))
            self.assertTrue(
                issubclass(
                    type(templates[t['id']]['shortDescription']), type(t['shortDescription'])
                )
            )
            self.assertTrue(issubclass(type(templates[t['id']]['tags']), type(t['tags'])))
            self.assertTrue(
                issubclass(type(templates[t['id']]['templateType']), type(t['templateType']))
            )
            self.assertTrue(issubclass(type(templates[t['id']]['baseId']), type(t['baseId'])))
            self.assertEqual(templates[t['id']]['baseId'], t['baseId'])
            self.assertEqual(
                templates[t['id']]['baselineSchemaVersion'], t['baselineSchemaVersion']
            )
            self.assertEqual(templates[t['id']]['id'], t['id'])
            self.assertEqual(templates[t['id']]['isDefault'], t['isDefault'])
            if templates[t['id']]['longDescription'] != t['longDescription']:
                diff: List[str] = self._compare_words(
                    t['longDescription'], templates[t['id']]['longDescription']
                )
                formatted_diff: str = '\n'.join(diff)
                self.fail(f"{t['name']} longDescription mismatch: \n{formatted_diff}")

            self.assertEqual(templates[t['id']]['longDescription'], t['longDescription'])
            self.assertEqual(templates[t['id']]['media'], t['media'])
            self.assertEqual(templates[t['id']]['name'], t['name'])
            self.assertEqual(templates[t['id']]['pgTemplateName'], t['pgTemplateName'])
            self.assertEqual(templates[t['id']]['schema'], t['schema'])
            self.assertEqual(templates[t['id']]['shortDescription'], t['shortDescription'])
            self.assertEqual(templates[t['id']]['tags'], t['tags'])
            self.assertEqual(templates[t['id']]['templateType'], t['templateType'])
            self.assertEqual(templates[t['id']]['baseId'], t['baseId'])

    def test_database_templates_by_name(self) -> None:
        '''Look up the database template id by case-insensitive template name.'''

        template_names: List[str] = [t['name'] for t in self.API.DATABASE_TEMPLATES_NEW]

        for name in template_names:
            ids: List[float] = self.API._database_templates_by_name(name)
            self.assertEqual(len(ids), 1)
            ids = self.API._database_templates_by_name(name[5:], wildcard=True)
            self.assertGreaterEqual(len(ids), 1)

    def test_database_templates_legacy(self) -> None:
        '''Legacy empty db or anura schemas.'''

        resp: Dict[str, Any] = self.API._database_templates_legacy()
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['templates'], list)

        TEMPLATE_KEYS: Tuple[str, ...] = ('id', 'is_default', 'name', 'role', 'schema')
        for t in resp['templates']:
            self.assertIsInstance(t, dict)
            for k in t.keys():
                self.assertIsInstance(k, str)
                self.assertIn(t['id'], self.API.DATABASE_TEMPLATES)
                self.assertIn(k, TEMPLATE_KEYS)

    def test_database_templates_legacy_by_name(self) -> None:
        '''Look up the database template id by case-insensitive template name.'''

        template_names: List[str] = [k for k in self.API.DATABASE_TEMPLATES_NAMEID.keys()]

        for name in template_names:
            ids: List[str] = self.API._database_templates_legacy_by_name(name)
            self.assertEqual(len(ids), 1)
            self.assertEqual(ids[0], self.API.DATABASE_TEMPLATES_NAMEID[name])
            ids = self.API._database_templates_legacy_by_name(name[5:], wildcard=True)
            if name == 'Anura New Model v2.6':
                self.assertEqual(len(ids), 2)
            else:
                self.assertGreaterEqual(len(ids), 1)

    def test_database_templates_names_legacy_diff_modern(self) -> None:
        '''Diff Legacy Templates call to Modern.'''

        # TODO future state will be to remove legacy template calls in which this would go away

        legacy: Dict[str, Any] = self.API._database_templates_legacy()
        modern: Dict[str, Any] = self.API.database_templates()

        # Old call id attribute used to be friendly name with underscores, then changed to guids
        old = {t['id'] for t in legacy['templates']}

        # New call pgTemplateName maps to old id attribute
        new = {t['pgTemplateName'] for t in modern['templates']}
        diff = old ^ new

        # Canary warning if templates are added or removed but legacy call does not mirror changes
        self.assertEqual(len(diff), 0)

        # Canary warning if the known list of legacy template ids diffs from legacy api call
        static_ids = {t for t in self.API.DATABASE_TEMPLATES_NAMEID.values()}
        diff = static_ids ^ old
        if len(diff) > 0:
            print(f'\nLegacy template vs static known ids diff: {diff}')

            static_not_in_legacy = static_ids - old
            print('\nStatic known ids not in legacy api call', static_not_in_legacy)
            for i in static_not_in_legacy:
                for name, id in self.API.DATABASE_TEMPLATES_NAMEID.items():
                    if i == id:
                        print(name, id)
                        break

            old_not_in_static = old - static_ids
            print('\nLegacy api template ids not in static known ids', old_not_in_static)
            for i in old_not_in_static:
                for t in legacy['templates']:
                    if i == t['id']:
                        print(t['name'], t['id'])
                        break

        if len(diff) > 0:
            self._json_to_file(legacy['templates'], '.database_templates_legacy.json')
            self._json_to_file(modern['templates'], '.database_templates_modern.json')
            self.fail('Legacy template ids do not match static known ids')

    def test_ip_address_allow(self) -> None:
        '''Whitelist ip address.'''

        self._database_ensure_exist()
        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        resp: Dict[str, str] = self.API.ip_address_allow(database_name=db['name'], ip='127.0.0.0')

        self.assertIsInstance(resp['ip'], str)
        self.assertIsInstance(resp['message'], str)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['ip'], '127.0.0.0')
        self.assertEqual(resp['result'], 'accepted')
        self.assertIn('five-minute delay', resp['message'])

    def test_ip_address_allow_invalid(self) -> None:
        '''Unable to whitelist, ip address is invalid.'''

        self._database_ensure_exist()
        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        with self.assertRaises(ValueError):
            self.API.ip_address_allow(database_name=db['name'], ip='alpha.0.0.0')

    def test_ip_address_allowed(self) -> None:
        '''Ip address is whitelisted.'''

        self._database_ensure_exist()
        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        resp: Dict[str, Any] = self.API.ip_address_allowed(database_name=db['name'], ip='127.0.0.0')
        self.assertIsInstance(resp['allowed'], bool)
        self.assertIsInstance(resp['ip'], str)
        self.assertIsInstance(resp['message'], str)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['allowed'], True)
        self.assertEqual(resp['ip'], '127.0.0.0')
        self.assertEqual(resp['result'], 'success')
        self.assertIn('is in the firewall', resp['message'])

    def test_ip_address_allowed_invalid(self) -> None:
        '''Ip address is invalid.'''

        self._database_ensure_exist()
        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        with self.assertRaises(ValueError):
            self.API.ip_address_allowed(database_name=db['name'], ip='alpha.0.0.0')

    def test_ip_address_invalid_ip4(self) -> None:
        '''Invalid IP4 address.'''

        ips: set[str] = {
            '300.0.0.1',
            '172.16.0.0/12',
            '0e48:e218:a693:e3ef:5863:dd98:f2e2:3019',
        }

        for ip in ips:
            self.assertFalse(self.API._ip_address_valid_ip4(ip))

    def test_ip_address_invalid_ip6(self) -> None:
        '''Invalid IP6 address.'''

        ips: set[str] = {
            '192.168.0.1',
            '185.81.104.218',
            '10.0.0.0/8',
            '0e48:e218:a693:e3ef:5863:dd98:f2e2:',
        }

        for ip in ips:
            self.assertFalse(self.API._ip_address_valid_ip6(ip))

    def test_ip_address_remove(self) -> None:
        '''Remove ip address from whitelist.'''

        ip = '127.0.0.0'
        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        resp: Dict[str, str] = self.API.ip_address_remove(db['name'], ip)
        self.assertEqual(len(resp.keys()), 3)
        self.assertIsInstance(resp['result'], str)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['ip'], str)
        self.assertIsInstance(resp['message'], str)
        self.assertIn(f'ip address {ip} is removed', resp['message'])

    def test_ip_address_remove_bad(self) -> None:
        '''Remove ip address from whitelist.'''

        db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
        with self.assertRaises(ValueError):
            self.API.ip_address_remove(database_name=db['name'], ip='')
            self.API.ip_address_remove(database_name=db['name'], ip='bad_ip_address')
            self.API.ip_address_remove(database_name=db['name'], ip='0.0.0.0')

    def test_ip_address_valid_ip4(self) -> None:
        '''Validate IP4 address.'''

        ips: set[str] = {
            '192.168.0.1',
            '185.81.104.218',
            '45.5.235.54',
            '240.143.250.50',
            '81.179.2.59',
            '27.243.41.247',
        }

        for ip in ips:
            self.assertTrue(self.API._ip_address_valid_ip4(ip))

    def test_ip_address_valid_ip4_cidr(self) -> None:
        '''Validate IP4 CIDR address range.'''

        ips: set[str] = {
            '10.0.0.0/8',
            '100.64.0.0/10',
            '172.16.0.0/12',
            '172.31.0.0/14',
            '192.168.0.0/16',
        }

        for ip in ips:
            self.assertTrue(self.API._ip_address_valid_ip4_cidr(ip))

    def test_ip_address_valid_ip6(self) -> None:
        '''Validate IP6 address.'''

        ips: set[str] = {
            '::1',
            '0e48:e218:a693:e3ef:5863:dd98:f2e2:3019',
            '2e23:164f:29a6:7e77:ab8a:4d5e:1b83:54d6',
            '406d:c023:1f83:fdb9:9685:8b8e:24f4:ee33',
            '4a20:1727:f9ea:b31c:48fc:954d:caf2:f2ae',
            '4bbb:024a:b3e8:cfb8:9164:f79d:0064:5c5b',
        }

        for ip in ips:
            self.assertTrue(self.API._ip_address_valid_ip6(ip))

    def test_ip_address_valid_ip6_cidr(self) -> None:
        '''Validate IP6 address range.'''

        ips: set[str] = {
            '2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b/48',
            '2001:db8::/32',
            '2001:db8:3c4d:15::/64',
            '2345:425:2CA1:0000:0000:567:5673:23b5/64',
        }

        for ip in ips:
            self.assertTrue(self.API._ip_address_valid_ip6_cidr(ip))

    def test_ip_addresses(self) -> None:
        '''Get list of whitelisted ip addresses for all databases.'''

        KNOWN_IPS = ('127.0.0.0', '174.52.145.72', '204.225.31.199')
        dbs: List[Dict[str, Any]] = self.API.databases()
        for db in dbs:
            db: Dict[str, Any] = self.API.account_storage_device(type='postgres_db')
            resp: Dict[str, Any] = self.API.ip_addresses(db['name'])
            self.assertIsInstance(resp['result'], str)
            self.assertEqual(resp['result'], 'success')
            self.assertIsInstance(resp['count'], int)
            self.assertIsInstance(resp['ips'], list)
            for ip in resp['ips']:
                self.assertIsInstance(ip, str)
                self.assertTrue(self.API._ip_address_valid(ip))
                self.assertIn(ip, KNOWN_IPS)

    def test_resource_library(self) -> None:
        '''Databases, Python modules, and Reference Data Resources.'''

        resp: List[Dict[str, Any]] = self.API._resource_library()
        self.assertIsInstance(resp, list)
        self.assertGreaterEqual(len(resp), 173)

        # check for drift
        # self._compare_list_of_dict_keys(resp)

        RTYPES: List[str] = self.API._resource_library_file_types()
        COMMON_KEYS: Tuple[str, ...] = (
            'category',
            'createdDate',
            'files',
            'id',
            'longDescription',
            'shortDescription',
            'tags',
            'title',
            'type',
            'updateDate',
        )

        for r in resp:
            self.assertGreaterEqual(len(r.keys()), len(COMMON_KEYS))
            self.assertTrue(all([True if k in r.keys() else False for k in COMMON_KEYS]))
            self.assertIsInstance(r, dict)
            self.assertIsInstance(r['category'], str)
            self.assertIsInstance(r['createdDate'], str)
            self.assertIsInstance(r['files'], dict)
            self.assertIsInstance(r['id'], str)
            self.assertIsInstance(r['longDescription'], str)
            self.assertIsInstance(r['shortDescription'], str)
            self.assertIsInstance(r['tags'], list)
            if len(r['tags']) > 0:
                for t in r['tags']:
                    self.assertIsInstance(t, str)

            # database
            if r.get('templateId'):
                self.assertIsInstance(r['templateId'], str)
                self.assertEqual(len(r.keys()), 11)
            else:
                self.assertGreaterEqual(len(r.keys()), 10)
                # self.assertLessEqual(len(r.keys()), 11)
            self.assertIsInstance(r['title'], str)
            self.assertIsInstance(r['type'], str)
            self.assertIn(
                r['type'],
                (
                    'reference_data',
                    'resource_items',
                    'sdk',
                    'cosmic_frog_model',
                    'simulation',
                    'mip',
                ),
            )
            self.assertIsInstance(r['updateDate'], str)

            if len(r['files'].keys()) > 0:
                self.assertIsInstance(r['files']['basePath'], str)
                self.assertIsInstance(r['files']['baseUrl'], str)
                self.assertIsInstance(r['files']['files'], list)
                for f in r['files']['files']:
                    self.assertIsInstance(f['name'], str)
                    self.assertIsInstance(f['path'], str)
                    self.assertIsInstance(f['type'], str)
                    if len(f['type']) > 0:
                        self.assertIn(f['type'], RTYPES)

    def test_onedrive_push(self) -> None:
        '''Push optilogic files to onedrive.'''

        with self.assertRaises(NotImplementedError):
            self.API.onedrive_push('fakeFilePath')

        return  # OE-7039 API: OneDrive Push Broke

        # does account even have onedrive storage?
        if self.API.storagetype_onedrive_exists is False:
            self.skipTest('OneDrive device not available')

        # storage device info cached, grab the first onedrive device name
        all_storage_devices: Dict[str, Any] = self.API.account_storage_devices()
        onedrive_devices = [d for d in all_storage_devices['storages'] if d['type'] == 'onedrive']

        # upload a file to onedrive device
        file_contents: str = f'{datetime.now()} unittest test_onedrive_push {time.time()}'
        file_path: str = f"/{onedrive_devices[0]['name']}/unittest.txt"
        self.API.wksp_file_upload('Studio', file_path, overwrite=True, filestr=file_contents)

        # initiate push to onedrive
        resp = self.API.onedrive_push(file_path)
        self.assertEqual(resp['result'], 'success')
        self.assertGreaterEqual(resp['count'], 1)
        self.assertIsInstance(resp['storageId'], str)
        self.assertIsInstance(resp['storageName'], str)
        self.assertTrue(resp['storageId'], onedrive_devices[0]['id'])
        self.assertTrue(resp['storageName'], onedrive_devices[0]['name'])

    def test_secret_add(self) -> None:
        '''Create a new secret.'''

        nano_secs: str = str(time.perf_counter_ns())
        cat: str = 'geocode'
        desc: str = f'unittest {nano_secs}'
        for provider in self.API.GEO_PROVIDERS:
            meta_dict: dict = {'isDefault': False, 'provider': provider}
            meta_str: str = dumps(meta_dict)
            name: str = f'ut_{provider}_{nano_secs}'
            value: str = str(uuid4())

            resp: Dict[str, str] = self.API.secret_add(name, value, cat, desc, meta=meta_str)
            self.assertIsInstance(resp['created'], str)
            self.assertIsInstance(resp['description'], str)
            self.assertIsInstance(resp['id'], str)
            self.assertIsInstance(resp['meta'], str)
            self.assertIsInstance(resp['name'], str)
            self.assertIsInstance(resp['result'], str)
            self.assertIsInstance(resp['type'], str)
            self.assertIsInstance(resp['value'], str)
            self.assertEqual(resp['description'], desc)
            self.assertEqual(resp['meta'], meta_str)
            self.assertEqual(resp['name'], name)
            self.assertEqual(resp['result'], 'success')
            self.assertEqual(resp['type'], cat)
            self.assertEqual(resp['value'], value)
            self.assertTrue(resp['created'].endswith('Z'))
            dt: datetime = parse(resp['created'])
            self.assertTrue(dt.tzname(), 'UTC')
            now: datetime = datetime.now(timezone.utc)
            self.assertEqual(dt.year, now.year)
            self.assertEqual(dt.month, now.month)
            self.assertEqual(dt.day, now.day)

    def test_secret_alter(self) -> None:
        '''Modify a secret.'''

        # find the unit test bing w/ timestamp secret to alter
        secrets = self.API._secret_select_all(desc='unittest')  # no values returned, too sensitive
        if len(secrets) == 0:
            self.API.secrets.cache_clear()
            self.test_secret_add()
            secrets = self.API._secret_select_all(desc='unittest')

        sec: dict = {}
        name: str = ''
        for secret in secrets:
            if secret['name'].find('ut_bing') > -1:
                sec = secret
                name = secret['name']
                break

        self.assertGreater(len(name), 0)

        # change the secret name
        new_name: str = 'ut_altered'
        resp = self.API.secret_update(name, new_name)
        if resp.get('crash'):
            self.fail(resp['response_body'])
        self.assertEqual(resp['created'], sec['created'])
        self.assertEqual(resp['id'], sec['id'])
        self.assertEqual(resp['description'], sec['description'])
        self.assertEqual(resp['meta'], sec['meta'])
        self.assertEqual(resp['name'], new_name)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['type'], sec['type'])

        # assert old secret no longer exists
        old: Dict[str, str] = self.API.secret(name)
        self.assertTrue(old['crash'])
        d: dict = loads(old['response_body'])
        self.assertIsInstance(d, dict)
        self.assertEqual(d['result'], 'error')
        self.assertEqual(d['message'], f"no secret found named '{name}'")

        # verify modified secret
        new: Dict[str, str] = self.API.secret('ut_altered')
        self.assertEqual(resp['id'], new['id'])
        self.assertEqual(resp['name'], new_name)

        # invalidate cache
        self.API.secrets.cache_clear()

    def test_secrets(self) -> None:
        '''Check all secrets.'''

        resp = self.API.secrets()
        if resp['count'] == 0:
            self.API.secrets.cache_clear()
            self.test_secret_add()
            resp = self.API.secrets()

        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertGreaterEqual(resp['count'], 1)
        self.assertIsInstance(resp['secrets'], list)
        self.assertGreaterEqual(len(resp['secrets']), 1)

        for s in resp['secrets']:
            self.assertIsInstance(s['created'], str)
            self.assertEqual(len(s['created']), 24)
            self.assertIsInstance(s['id'], str)
            self.assertEqual(len(s['id']), 36)
            self.assertTrue(bool(fullmatch(self.API.re_uuid4, s['id'], flags=2)))
            self.assertIsInstance(s['name'], str)
            self.assertGreater(len(s['name']), 0)

            if s.get('description'):
                self.assertIsInstance(s['description'], str)
            if s.get('meta'):
                self.assertIsInstance(s['meta'], str)
            if s.get('type'):
                self.assertIsInstance(s['type'], str)

            dt: datetime = parse(s['created'])
            self.assertTrue(dt.tzname(), 'UTC')

    def test_secrets_exist(self) -> None:
        '''Check newly created unittest secrets.'''

        nil = 'does_not_exist'
        ut = 'unittest'
        geo = 'geocode'

        secrets: List[Dict[str, Any]] = self.API._secret_select_all(category=geo, desc=ut)
        if len(secrets) == 0:
            self.API.secrets.cache_clear()
            self.test_secret_add()
            secrets = self.API._secret_select_all(category=geo, desc=ut)

        self.assertGreaterEqual(len(secrets), 4)
        for s in secrets:
            d: Dict[str, Any] = loads(s['meta'])
            self.assertIsInstance(d, dict)
            self.assertEqual(len(d.keys()), 2)
            self.assertIsInstance(d['isDefault'], bool)
            self.assertFalse(d['isDefault'])
            self.assertIsInstance(d['provider'], str)
            self.assertIn(d['provider'], self.API.GEO_PROVIDERS)

            dt: datetime = parse(s['created'])
            self.assertLess(time.time() - dt.timestamp(), 3600)

            self.assertGreater(s['name'].find('ut'), -1)
            self.assertGreater(s['description'].find(ut), -1)

        self.assertFalse(self.API._secret_exist(name=nil, category=geo, desc=ut))
        self.assertFalse(self.API._secret_exist(name=nil, category=geo))
        self.assertFalse(self.API._secret_exist(name=nil, desc=ut))
        self.assertFalse(self.API._secret_exist(name=nil))
        self.assertFalse(self.API._secret_exist(category=nil))
        self.assertFalse(self.API._secret_exist(desc=nil))

        self.assertTrue(self.API._secret_exist(category=geo, desc=ut))
        self.assertTrue(self.API._secret_exist(category=geo))
        self.assertTrue(self.API._secret_exist(desc=ut))

    def test_secrets_remove(self) -> None:
        '''Remove all unittest secrets.'''

        secrets: List[Dict[str, Any]] = self.API._secret_select_all(desc='unittest')
        if len(secrets) == 0:
            self.API.secrets.cache_clear()
            self.test_secret_add()
            secrets = self.API._secret_select_all(desc='unittest')

        for s in secrets:
            resp: Dict[str, str] = self.API.secret_delete(s['name'])
            if resp.get('crash'):
                self.fail(resp['response_body'])
            self.assertEqual(resp['result'], 'success')
            self.assertEqual(resp['id'], s['id'])
            self.assertEqual(resp['name'], s['name'])

    def test_sql_connect_info(self) -> None:
        '''Get the connection information for a sql storage item.'''

        self._database_ensure_exist()
        pg = self.API.account_storage_device('postgres_db')
        resp = self.API.sql_connection_info(pg['name'])
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp['raw']), 6)
        self.assertIsInstance(resp['raw']['host'], str)
        self.assertTrue(
            resp['raw']['host'].endswith('postgres.database.azure.com')
            or resp['raw']['host'].endswith('database.optilogic.app')
        )
        self.assertIsInstance(resp['raw']['dbname'], str)
        self.assertIsInstance(resp['raw']['password'], str)
        self.assertIsInstance(resp['raw']['port'], int)
        self.assertIsInstance(resp['raw']['sslmode'], str)
        self.assertIsInstance(resp['raw']['user'], str)
        self.assertIsInstance(resp['connectionStrings'], dict)
        self.assertEqual(len(resp['connectionStrings']), 5)
        self.assertTrue(resp['connectionStrings']['jdbc'].startswith('jdbc:postgresql://'))
        self.assertTrue(resp['connectionStrings']['libpq'].startswith('host='))
        self.assertTrue(resp['connectionStrings']['net'].startswith('Server='))
        self.assertTrue(resp['connectionStrings']['psql'].startswith('psql \'host='))
        self.assertTrue(resp['connectionStrings']['url'].startswith('postgresql://'))

    def test_storage(self) -> None:
        '''Perform storage device info on every device from storage device list.'''

        devices = self.API.account_storage_devices()
        self.assertEqual(devices['result'], 'success')
        with self.subTest():
            for device in devices['storages']:
                resp: Dict[str, Any] = self.API.storage(device['name'])
                d = OrderedDict(sorted(resp.items()))
                self.assertEqual(d['result'], 'success')
                if d['type'] == 'azure_afs':
                    self.assertEqual(len(d), 17)
                    self._storage_azure_afs(d)
                if d['type'] == 'azure_workspace':
                    self.assertEqual(len(d), 18)
                    self._storage_azure_workspace(d)
                elif d['type'] == 'onedrive':
                    self.assertEqual(len(d), 20)
                    self._storage_onedrive(d)
                    self.assertIsInstance(d['connected'], bool)
                elif d['type'] == 'postgres_db':
                    # storage item contains an additional result key
                    self.assertEqual(len(d), 25)
                    self._storage_database(d)

    def test_storage_attr(self) -> None:
        '''Device attributes: annotations, label, and tag.'''

        attrs: Tuple[Literal['annotations'], Literal['labels'], Literal['tags']] = (
            'annotations',
            'labels',
            'tags',
        )
        devices: Dict[str, Any] = self.API.account_storage_devices()
        self.assertEqual(devices['result'], 'success')
        with self.subTest():
            for d in devices['storages']:
                for a in attrs:
                    resp: Dict[str, Any] = self.API._storage_attr(d['name'], a)
                    self.assertEqual(resp['result'], 'success')
                    self.assertEqual(len(resp.keys()), 2)
                    self.assertTrue(a in resp.keys())
                    if a == 'tags':
                        self.assertIsInstance(resp[a], str)
                    else:
                        self.assertIsInstance(resp[a], dict)

    @unittest.skip('api has not implemented')
    def test_storage_disk_create(self):
        '''Create a new file storage device.'''

        raise NotImplementedError

    @unittest.skip('api is incomplete')
    def test_storage_delete(self):
        '''Delete storage device.'''

        raise NotImplementedError

    def test_sql_query(self) -> None:
        '''Test sql statement execution.'''

        self._database_ensure_exist()
        pg = self.API.account_storage_device(type='postgres_db')
        resp = self.API.sql_query(
            database_name=pg['name'], query='SELECT datname FROM pg_database;'
        )
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['rowCount'], int)
        self.assertGreaterEqual(resp['rowCount'], 1)
        self.assertIsInstance(resp['queryResults'], list)
        self.assertGreaterEqual(len(resp['queryResults']), 1)

    def test_util_env(self) -> None:
        '''Atlas and andromeda common environment variables.'''

        keys: Tuple[str, ...] = (
            'job_cmd',
            'job_dir',
            'job_key',
            'job_api',
            'job_img',
            'pip_ver',
            'py_ver',
        )
        d = self.API.util_environment()
        for k in d.keys():
            self.assertTrue(k in keys)
            self.assertIsInstance(d[k], str)

    def test_util_job_monitor(self) -> None:
        '''Start a new job and monitor job state.'''

        resp: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP, self.py_sleep, tags='monitor', resourceConfig='mini'
        )

        # measure the job monitor time to for job state to be running
        start: float = time.time()
        success: bool = self.API.util_job_monitor(self.WKSP, resp['jobKey'])
        self.assertTrue(success)
        delta: float = time.time() - start

        # verify job state is running
        job: Dict[str, Any] = self.API.wksp_job_status(self.WKSP, resp['jobKey'])
        self.assertNotEqual(job['status'], 'submitted')
        valid_states: Tuple[str, ...] = (
            self.API.JOBSTATES_ACTIVE[1:] + self.API.JOBSTATES_TERMINAL_RUNTIME
        )
        self.assertIn(job['status'], valid_states)

        # monitoring time is longer due to polling delays
        sub: datetime = parse(job['submittedDatetime'])
        st: datetime = parse(job['startDatetime'])
        diff: timedelta = st - sub
        self.assertLess(diff.total_seconds(), delta)

    def test_util_job_monitor_bad(self) -> None:
        '''Job monitor check invalid job key or job state.'''

        valid_guid = '00000000-0000-0000-0000-000000000000'

        # invalid job state
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, '5633e372-337a-454c-aae4-10084ea5bac6', 'invalid')  # type: ignore

        # invalid job key
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, '')
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, 'invalid')
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, '633e372-337a-454c-aae4-10084ea5bac6')

        # invalid max seconds
        with self.assertRaises(TypeError):
            self.API.util_job_monitor(self.WKSP, valid_guid, secs_max='invalid')  # type: ignore
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, valid_guid, secs_max=-1)
        with self.assertRaises(ValueError):
            self.API.util_job_monitor(self.WKSP, valid_guid, secs_max=86401)

        # TODO force a non 404 job crash and verify job monitor emits warning

        # valid but job key does not exist
        resp: bool = self.API.util_job_monitor(self.WKSP, valid_guid)
        self.assertFalse(resp)

    def test_util_job_monitor_done(self) -> None:
        '''Jobs with unittest_prereq are ran prior and are in terminal state.'''

        # jobs found by tag in last seven days
        resp: Dict[str, Any] = self.API.wksp_jobs(self.WKSP, tags='unittest_prereq')

        jobs: int = resp.get('count', 0)
        if jobs == 0:
            self.skipTest('no jobs found with tag unittest_prereq')

        job_key: str = resp['jobs'][0]['jobKey']

        success: bool = self.API.util_job_monitor(self.WKSP, job_key)
        self.assertTrue(success)

    def test_util_job_monitor_set(self) -> None:
        '''Monitor jobs by tag.'''

        resp: Dict[str, Any] = {}
        jobs_max: int = 9
        secs: int = 10

        tag_time: float = int(time.time())
        tag: str = f'monitor_set_{tag_time}'

        for _ in range(jobs_max):
            # spin up a few jobs to create load to evaluate
            resp = self.API.wksp_job_start(
                self.WKSP, self.py_sleep, tags=tag, timeout=secs, resourceConfig='mini'
            )
            if resp.get('crash'):
                jobs_max -= 1
                continue

        success: bool = self.API.util_job_monitor_set(self.WKSP, tag)
        self.assertTrue(success)

    def test_util_job_monitor_set_done(self) -> None:
        '''Unittest_prereq tag to quickly check terminal state.'''

        # prereq job runs before any unittest and will be in done state
        success: bool = self.API.util_job_monitor_set(self.WKSP, 'unittest_prereq', 'terminal')
        self.assertTrue(success)

    def test_wksp_file_copy(self) -> None:
        '''Make a copy of a file within a workspace.'''

        src: str = self.py_sleep
        dest: str = f'{self.dir_testdata_remote}/cp_test.txt'
        resp = self.API.wksp_file_copy(
            self.WKSP, file_path_src=src, file_path_dest=dest, overwrite=True
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['copyStatus'], 'success')
        self.assertEqual(resp['message'], 'Copy complete')
        src_result: str = (
            f"{resp['sourceFileInfo']['directoryPath']}/{resp['sourceFileInfo']['filename']}"
        )
        dest_result: str = (
            f"{resp['targetFileInfo']['directoryPath']}/{resp['targetFileInfo']['filename']}"
        )
        self.assertEqual(src, src_result)
        self.assertEqual(dest, dest_result)

    def test_wksp_file_delete(self) -> None:
        '''Delete a copied file with a workspace.'''

        f: str = f'{self.dir_testdata_remote}/cp_test.txt'
        resp = self.API.wksp_file_delete(self.WKSP, file_path=f)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'File deleted')
        file_result = f"{resp['fileInfo']['directoryPath']}/{resp['fileInfo']['filename']}"
        self.assertEqual(f, file_result)

    def test_wksp_file_download(self) -> None:
        '''Download a file from a given workspace.'''

        download = self.API.wksp_file_download(self.WKSP, file_path=self.py_sleep)
        self.assertGreaterEqual(len(download), 1)
        self.assertIsInstance(download, str)

    def test_wksp_file_download_crash(self) -> None:
        '''Download a file from a given workspace.'''

        resp: str = self.API.wksp_file_download(self.WKSP, file_path='does_not_exist')
        self.assertIsInstance(resp, str)
        r: dict = loads(resp)
        self.assertEqual(r['result'], 'error')
        self.assertIsInstance(r['error'], str)
        self.assertEqual(len(r['correlationId']), 36)

    def test_wksp_file_download_meta(self) -> None:
        '''File metadata.'''

        resp = self.API.wksp_file_download_status(self.WKSP, file_path=self.py_sleep)
        self.assertEqual(resp['result'], 'success')
        keys: Tuple[str, ...] = (
            'result',
            'workspace',
            'filename',
            'directoryPath',
            'filePath',
            'lastModified',
            'contentLength',
            'date',
            'fileCreatedOn',
            'fileLastWriteOn',
            'fileChangeOn',
        )
        for key in resp.keys():
            self.assertIn(key, keys)
        self.assertEqual(resp['filePath'], self.py_sleep)
        self.assertEqual(resp['workspace'], self.WKSP)
        self.assertIsInstance(resp['contentLength'], int)
        dt: datetime = parse(resp['lastModified'])
        self.assertEqual(dt.tzname(), 'UTC')

    def test_wksp_file_upload(self) -> None:
        '''Upload a file to a workspace.'''

        dest: str = f'{self.dir_testdata_remote}/str2file.txt'
        resp = self.API.wksp_file_upload(
            self.WKSP, file_path_dest=dest, overwrite=True, filestr='test'
        )
        self.assertEqual(resp['result'], 'success')
        self.assertIn(resp['message'], ['File created', 'File replaced'])

    def test_wksp_files(self) -> None:
        '''File structure from a given workspace and must have at least one file.'''

        resp = self.API.wksp_files(self.WKSP)
        self.assertEqual(resp['result'], 'success')
        self.assertGreaterEqual(resp['count'], 1)
        self.assertIsInstance(resp['files'], list)
        self.assertGreaterEqual(len(resp['files']), 1)
        self.assertTrue(resp['files'][0].get('filename'))
        self.assertTrue(resp['files'][0].get('directoryPath'))
        self.assertTrue(resp['files'][0].get('filePath'))
        self.assertTrue(resp['files'][0].get('contentLength'))

    def test_wksp_folder_delete(self) -> None:
        '''Delete a folder from a workspace.'''

        folder: str = 'delete_me_now'
        fp: str = path.join(folder, 'delete_me.txt')
        self.API.wksp_file_upload(self.WKSP, fp, filestr='first file line')
        resp = self.API.wksp_folder_delete(self.WKSP, dir_path=folder, force=True)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'Directory and all contents deleted')
        self.assertEqual(resp['directoryPath'], folder)

    def test_wksp_info(self) -> None:
        '''Properties of a given workspace.'''

        resp = self.API.wksp_info(self.WKSP)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['name'], self.WKSP)
        self.assertEqual(len(resp['key']), 25)
        self.assertRegex(resp['key'], '^workspace')
        self.assertIn(resp['stack'], ['Optilogic', 'Simulation', 'Gurobi'])
        self.assertTrue(resp['status'].isupper())

    def test_wksp_job_back2back(self) -> None:
        '''One job to run many python modules in a row.'''

        item_one: dict = {
            'pyModulePath': '/projects/quick_tests/sleep.py',
            'commandArgs': 'not_used',
            'timeout': 90,
        }
        item_two: dict = {
            'pyModulePath': '/projects/quick_tests/airline_hub_location_cbc.py',
            'timeout': 30,
        }
        batch = {'batchItems': [item_one, item_two]}

        tag: str = 'unittest_batch_back2back'
        resp = self.API.wksp_job_back2back(self.WKSP, batch=batch, verboseOutput=True, tags=tag)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 5)
        self.assertEqual(resp['message'], 'Job submitted')
        self.assertIsInstance(resp['jobKey'], str)
        self.assertEqual(len(resp['jobKey']), 36)
        self.assertIsInstance(resp['batch'], dict)
        self.assertEqual(len(resp['batch']), 1)

        # batchItems
        self.assertIsInstance(batch['batchItems'], list)
        self.assertEqual(len(batch['batchItems']), 2)
        # item_one
        self.assertIsInstance(resp['batch']['batchItems'][0], list)
        self.assertEqual(len(resp['batch']['batchItems'][0]), 3)
        self.assertEqual(resp['batch']['batchItems'][0][0], item_one['pyModulePath'])
        self.assertEqual(resp['batch']['batchItems'][0][1], item_one['commandArgs'])
        self.assertEqual(resp['batch']['batchItems'][0][2], item_one['timeout'])
        # item_two
        self.assertIsInstance(resp['batch']['batchItems'][1], list)
        self.assertEqual(len(resp['batch']['batchItems'][1]), 3)
        self.assertEqual(resp['batch']['batchItems'][1][0], item_two['pyModulePath'])
        self.assertIsNone(resp['batch']['batchItems'][1][1])
        self.assertEqual(resp['batch']['batchItems'][1][2], item_two['timeout'])

        # jobInfo
        andromeda_configs: Dict[str, Any] = self.API.andromeda_machine_configs()
        cfg_name: str = andromeda_configs['defaultConfigName']
        cfg_run_rate: Number = next(
            cfg['runRate']
            for cfg in andromeda_configs['resourceConfigs']
            if cfg['name'] == cfg_name
        )

        self.assertIsInstance(resp['jobInfo'], dict)
        self.assertEqual(len(resp['jobInfo']), 4)
        self.assertEqual(resp['jobInfo']['workspace'], self.WKSP)
        self.assertEqual(resp['jobInfo']['tags'], tag)
        self.assertEqual(resp['jobInfo']['timeout'], -1)
        self.assertIsInstance(resp['jobInfo']['resourceConfig'], dict)
        self.assertEqual(len(resp['jobInfo']['resourceConfig']), 4)
        self.assertEqual(resp['jobInfo']['resourceConfig']['cpu'], '1vCore')
        self.assertEqual(resp['jobInfo']['resourceConfig']['name'], cfg_name)
        self.assertEqual(resp['jobInfo']['resourceConfig']['ram'], '2Gb')
        self.assertEqual(resp['jobInfo']['resourceConfig']['run_rate'], cfg_run_rate)

        # verify new batch job
        job = self.API.wksp_job_status(self.WKSP, resp['jobKey'])
        self.assertEqual(job['jobInfo']['workspace'], self.WKSP)
        self.assertEqual(job['jobInfo']['directoryPath'], '/usr/bin')
        self.assertEqual(job['jobInfo']['filename'], 'batch_run.py')
        self.assertEqual(job['jobInfo']['command'], 'run')
        self.assertIsInstance(job['jobInfo']['commandArgs'], str)
        args: dict = loads(job['jobInfo']['commandArgs'][1:-1])
        self.assertIsInstance(args, dict)
        self.assertIsInstance(args['batchItems'], list)
        self.assertEqual(args['batchItems'][0][0], item_one['pyModulePath'])
        self.assertEqual(args['batchItems'][0][1], item_one['commandArgs'])
        self.assertEqual(args['batchItems'][0][2], item_one['timeout'])
        self.assertEqual(args['batchItems'][1][0], item_two['pyModulePath'])
        self.assertEqual(args['batchItems'][1][1], item_two.get('commandArgs'))
        self.assertEqual(args['batchItems'][1][2], item_two['timeout'])
        self.assertEqual(job['jobInfo']['resourceConfig']['cpu'], '1vCore')
        self.assertEqual(job['jobInfo']['resourceConfig']['name'], cfg_name)
        self.assertEqual(job['jobInfo']['resourceConfig']['ram'], '2Gb')
        self.assertEqual(job['jobInfo']['resourceConfig']['run_rate'], cfg_run_rate)

    def test_wksp_job_back2back_findnrun(self) -> None:
        '''Search file paths yields one job to run many python modules in a row.'''

        item_one: dict = {
            'pySearchTerm': '/projects/quick_tests/sleep.py',
            'commandArgs': 'not_used',
            'timeout': 90,
        }
        item_two: dict = {
            'pySearchTerm': '/projects/quick_tests/airline_hub_location_cbc.py',
            'timeout': 30,
        }
        batch = {'batchItems': [item_one, item_two]}

        tag: str = 'unittest_batch_back2back_find'
        resp = self.API.wksp_job_back2back_findnrun(
            self.WKSP, batch=batch, verboseOutput=True, tags=tag
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp), 5)
        self.assertEqual(resp['message'], 'Job submitted')
        self.assertIsInstance(resp['jobKey'], str)
        self.assertEqual(len(resp['jobKey']), 36)
        self.assertIsInstance(resp['batch'], dict)
        self.assertEqual(len(resp['batch']), 2)
        self.assertTrue(resp['batch']['search'])

        # batchItems
        self.assertIsInstance(batch['batchItems'], list)
        self.assertEqual(len(batch['batchItems']), 2)
        # item_one
        self.assertIsInstance(resp['batch']['batchItems'][0], list)
        self.assertEqual(len(resp['batch']['batchItems'][0]), 3)
        self.assertEqual(resp['batch']['batchItems'][0][0], item_one['pySearchTerm'])
        self.assertEqual(resp['batch']['batchItems'][0][1], item_one['commandArgs'])
        self.assertEqual(resp['batch']['batchItems'][0][2], item_one['timeout'])
        # item_two
        self.assertIsInstance(resp['batch']['batchItems'][1], list)
        self.assertEqual(len(resp['batch']['batchItems'][1]), 3)
        self.assertEqual(resp['batch']['batchItems'][1][0], item_two['pySearchTerm'])
        self.assertIsNone(resp['batch']['batchItems'][1][1])
        self.assertEqual(resp['batch']['batchItems'][1][2], item_two['timeout'])

        # jobInfo
        andromeda_configs: Dict[str, Any] = self.API.andromeda_machine_configs()
        cfg_name: str = andromeda_configs['defaultConfigName']
        cfg_run_rate: Number = next(
            cfg['runRate']
            for cfg in andromeda_configs['resourceConfigs']
            if cfg['name'] == cfg_name
        )

        self.assertIsInstance(resp['jobInfo'], dict)
        self.assertEqual(len(resp['jobInfo']), 4)
        self.assertEqual(resp['jobInfo']['workspace'], self.WKSP)
        self.assertEqual(resp['jobInfo']['tags'], tag)
        self.assertEqual(resp['jobInfo']['timeout'], -1)
        self.assertIsInstance(resp['jobInfo']['resourceConfig'], dict)
        self.assertEqual(len(resp['jobInfo']['resourceConfig']), 4)
        self.assertEqual(resp['jobInfo']['resourceConfig']['cpu'], '1vCore')
        self.assertEqual(resp['jobInfo']['resourceConfig']['name'], cfg_name)
        self.assertEqual(resp['jobInfo']['resourceConfig']['ram'], '2Gb')
        self.assertEqual(resp['jobInfo']['resourceConfig']['run_rate'], cfg_run_rate)

        # verify new batch job
        job = self.API.wksp_job_status(self.WKSP, resp['jobKey'])
        self.assertEqual(job['jobInfo']['workspace'], self.WKSP)
        self.assertEqual(job['jobInfo']['directoryPath'], '/usr/bin')
        self.assertEqual(job['jobInfo']['filename'], 'batch_search_n_run.py')
        self.assertEqual(job['jobInfo']['command'], 'run')
        self.assertIsInstance(job['jobInfo']['commandArgs'], str)
        args: dict = loads(job['jobInfo']['commandArgs'][1:-1])
        self.assertIsInstance(args, dict)
        self.assertIsInstance(args['batchItems'], list)
        self.assertEqual(args['batchItems'][0][0], item_one['pySearchTerm'])
        self.assertEqual(args['batchItems'][0][1], item_one['commandArgs'])
        self.assertEqual(args['batchItems'][0][2], item_one['timeout'])
        self.assertEqual(args['batchItems'][1][0], item_two['pySearchTerm'])
        self.assertEqual(args['batchItems'][1][1], item_two.get('commandArgs'))
        self.assertEqual(args['batchItems'][1][2], item_two['timeout'])
        self.assertEqual(job['jobInfo']['resourceConfig']['cpu'], '1vCore')
        self.assertEqual(job['jobInfo']['resourceConfig']['name'], cfg_name)
        self.assertEqual(job['jobInfo']['resourceConfig']['ram'], '2Gb')
        self.assertEqual(job['jobInfo']['resourceConfig']['run_rate'], cfg_run_rate)

    def test_wksp_job_file_error(self) -> None:
        '''Get job error file.'''

        resp: str = self.API.wksp_job_file_error(self.WKSP, self.API._job_start_recent_key)
        self.assertIsInstance(resp, str)
        if resp.startswith('{\"result\":\"error\"'):
            err: dict = loads(resp)
            self.assertEqual(err['result'], 'error')
            self.assertIsInstance(err['error'], str)
            self.assertIsInstance(err['correlationId'], str)
            self.assertEqual(len(err['correlationId']), 36)
        else:
            self.assertGreater(len(resp), 0)

    def test_wksp_job_file_result(self) -> None:
        '''Get job result file.'''

        resp: str = self.API.wksp_job_file_result(self.WKSP, self.API._job_start_recent_key)
        self.assertIsInstance(resp, str)
        if resp.startswith('{\"result\":\"error\"'):
            err: dict = loads(resp)
            self.assertEqual(err['result'], 'error')
            self.assertIsInstance(err['error'], str)
            self.assertIsInstance(err['correlationId'], str)
            self.assertEqual(len(err['correlationId']), 36)
        else:
            self.assertGreater(len(resp), 0)

    def test_wksp_job_ledger(self) -> None:
        '''Get job ledger that has realtime messages.'''

        # Job.add_record method expects param message of type str
        # sidecar.py during job runtime emits messages that are not type str to test
        type_tup = (
            bool(1),
            int(1),
            float(1),
            [1],
            (1, 2),
            {1: 2},
            {1, 2},
            b'101',
        )
        # str version of object, ie int(1) == '1'
        type_strs: List[str] = sorted([t.__str__() for t in type_tup])

        job: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP,
            self.py_sidecar,
            resourceConfig='mini',
            tags='unittest',
        )
        res: bool = self.API.util_job_monitor(self.WKSP, job['jobKey'], stop_when='done')
        self.assertTrue(res)

        resp: Dict[str, Any] = self.API.wksp_job_ledger(self.WKSP, job['jobKey'])
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertGreaterEqual(resp['count'], 1)

        self.assertIsInstance(resp['records'], list)
        self.assertGreaterEqual(len(resp['records']), 1)
        for r in resp['records']:
            self.assertIsInstance(r, dict)
            self.assertEqual(len(r), 4)
            self.assertIsInstance(r['datetime'], str)
            self._date_iso_today(r['datetime'])
            self.assertIsInstance(r['key'], str)
            self.assertIn(r['key'], ('eta', 'type', '96k'))
            self.assertIsInstance(r['message'], str)
            self.assertLessEqual(len(r['message']), 32_000)
            self.assertIsInstance(r['timestamp'], int)

        # assert non str types messages cast to str by verifying the job ledger
        type_msgs: List[str] = sorted([r['message'] for r in resp['records'] if r['key'] == 'type'])
        self.assertEqual(len(type_strs), len(type_msgs))

    def test_wksp_job_metrics(self) -> None:
        '''Get one second cpu and memory sampling of a job.'''

        if len(self.__jobkey_quick) == 0:
            self._job_prereq()
        resp: Dict[str, Any] = self.API.wksp_job_metrics(self.WKSP, self.__jobkey_quick)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertGreaterEqual(resp['count'], 1)

        self.assertIsInstance(resp['max'], dict)
        self.assertEqual(len(resp['max']), 7)
        self.assertIsInstance(resp['max']['cpuAvailable'], Number)
        self.assertIsInstance(resp['max']['cpuPercent'], float)
        self.assertIsInstance(resp['max']['cpuUsed'], float)
        self.assertIsInstance(resp['max']['memoryAvailable'], int)
        self.assertIsInstance(resp['max']['memoryPercent'], float)
        self.assertIsInstance(resp['max']['memoryResident'], Number)
        self.assertIsInstance(resp['max']['processCount'], int)

        self.assertIsInstance(resp['records'], list)
        self.assertGreaterEqual(len(resp['records']), 1)
        self.assertIsInstance(resp['records'][0], dict)
        self.assertIsInstance(resp['records'][0]['timestamp'], int)
        self.assertIsInstance(resp['records'][0]['datetime'], str)
        self.assertTrue(self._date_iso_today(resp['records'][0]['datetime']))
        self.assertIsInstance(resp['records'][0]['cpuAvailable'], Number)
        self.assertIsInstance(resp['records'][0]['cpuPercent'], float)
        self.assertIsInstance(resp['records'][0]['cpuUsed'], float)
        self.assertIsInstance(resp['records'][0]['memoryAvailable'], int)
        self.assertIsInstance(resp['records'][0]['memoryPercent'], float)
        self.assertIsInstance(resp['records'][0]['memoryResident'], float)
        self.assertIsInstance(resp['records'][0]['processCount'], int)

    def test_wksp_job_metrics_max(self) -> None:
        '''Get peak cpu and memory stats of a job.'''

        if len(self.__jobkey_quick) == 0:
            self._job_prereq()
        resp = self.API.wksp_job_metrics_max(self.WKSP, self.__jobkey_quick)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['max'], dict)
        self.assertEqual(len(resp['max']), 7)
        self.assertIsInstance(resp['max']['memoryPercent'], float)
        self.assertIsInstance(resp['max']['memoryResident'], float)
        self.assertIsInstance(resp['max']['memoryAvailable'], int)
        self.assertIsInstance(resp['max']['cpuPercent'], Number)
        self.assertIsInstance(resp['max']['cpuUsed'], Number)
        self.assertIsInstance(resp['max']['cpuAvailable'], Number)
        self.assertIsInstance(resp['max']['processCount'], int)

    def test_wksp_job_metrics_mia(self) -> None:
        '''OE-5276 Job Metrics are Missing Sometimes.
        OE-5369 Job Metrics Missing v3.
        '''

        # spin up a few jobs to create load and evaluate all
        jobs_max: int = 9
        tag_time: float = time.time()
        tag: str = f'metrics_{tag_time}'
        secs: int = 20
        d: dict = {}  # store job key and elapsed time without metrics
        for job in range(jobs_max):
            resp = self.API.wksp_job_start(
                self.WKSP, self.py_sleep, tags=tag, timeout=secs, resourceConfig='mini'
            )
            if resp.get('crash'):
                print(resp)
                jobs_max -= 1
                continue
            d[resp['jobKey']] = {'seen_first': None, 'missing_last': None}

        # check the jobs that are about to run
        metrics_missing = False
        check: bool = True
        while check:
            # stop if all jobs finished
            jobs: Dict[str, Any] = self.API.wksp_jobs(self.WKSP, tags=tag)
            terminal: int = 0
            for t in self.API.JOBSTATES_TERMINAL:
                terminal += jobs['statusCounts'].get(t)
            if terminal == jobs_max:
                check = False
                break

            # check running jobs for metrics
            active: Dict[str, Any] = self.API.wksp_jobs(self.WKSP, status='running', tags=tag)
            for job in active['jobs']:
                # elapsed run time
                st: str = str(job['startDatetime'])
                st = st.replace('T', ' ')
                st = st.replace('Z', '')
                job_start: datetime = datetime.fromisoformat(st)
                now: datetime = datetime.now(timezone.utc)
                delta: timedelta = now - job_start

                # first time observed the job was running
                if d[job['jobKey']].get('seen_first') is None:
                    d[job['jobKey']]['seen_first'] = str(delta)

                # check for metrics
                resp: Dict[str, Any] = self.API.wksp_job_metrics(self.WKSP, job['jobKey'])
                self.assertEqual(resp['result'], 'success')
                self.assertIsInstance(resp['count'], int)

                # missing metrics?
                if resp['count'] == 0:
                    metrics_missing = True
                    d[job['jobKey']]['missing_last'] = str(delta)
                    print(f"{str(delta)} secs elapsed, metrics missing for job {job['jobKey']}")
                    with self.subTest():
                        self.assertLess(delta.total_seconds(), 10)

        if metrics_missing:
            print('\n\nTEST_WKSP_JOB_METRICS_MIA')
            print(f"\n\nJob Submitted: {jobs_max}, Job Duration: {secs}, Job Tag: {tag}")
            for item in d.items():
                print(item)

    def test_wksp_job_start(self) -> None:
        '''Creating a job.'''

        resp: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP, file_path=self.py_sleep, tags='unittest_start', resourceConfig='mini'
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp['jobKey']), 36)
        job_info_keys: Tuple[str, ...] = (
            'workspace',
            'directoryPath',
            'filename',
            'command',
            'resourceConfig',
            'tags',
            'timeout',
        )
        for key in resp['jobInfo'].keys():
            self.assertIn(key, job_info_keys)

    def test_wksp_job_start_self_aware(self) -> None:
        '''Active job in Andromeda is aware of it's own job key.'''

        # start a job and have it pluck out its own job key
        resp = self.API.wksp_job_start(
            self.WKSP, self.py_job_aware, tags='unittest_my_job_key', resourceConfig='mini'
        )
        self.API.util_job_monitor(self.WKSP, resp['jobKey'], stop_when='done')

        # verify self aware job has the correct job key
        ledger = self.API.wksp_job_ledger(self.WKSP, resp['jobKey'], 'job_key')
        self.assertEqual(resp['jobKey'], ledger['records'][0]['message'])

    def test_wksp_job_start_preview(self) -> None:
        '''Create a job using andromeda preview image and compare to stable.'''

        # 1) start preview job
        job_preview: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP,
            file_path=self.py_bash,
            commandArgs="'pip list -v --format json'",
            resourceConfig='mini',
            tags='unittest',
            preview_image=True,
        )
        self.assertEqual(job_preview['result'], 'success')

        # 2) start stable job
        job_stable: Dict[str, Any] = self.API.wksp_job_start(
            self.WKSP,
            file_path=self.py_bash,
            commandArgs="'pip list -v --format json'",
            resourceConfig='mini',
            tags='unittest',
            preview_image=False,
        )
        self.assertEqual(job_stable['result'], 'success')

        # 3) wait for jobs to finish
        done: bool = self.API.util_job_monitor(
            self.WKSP, job_key=job_preview['jobKey'], stop_when='done'
        )
        self.assertTrue(done)

        done: bool = self.API.util_job_monitor(
            self.WKSP, job_key=job_stable['jobKey'], stop_when='done'
        )
        self.assertTrue(done)

        # 4) Deserialize preview pip stdout into dict
        std_out: str = self.API.wksp_job_file_result(self.WKSP, job_preview['jobKey'])
        jsn: List[Dict[str, str]] = self._deserialize_pip_output(std_out)
        pkgs_preview: Dict[str, Dict[str, str]] = {d['name']: d for d in jsn}

        # 5) Deserialize stable pip stdout into dict
        std_out: str = self.API.wksp_job_file_result(self.WKSP, job_stable['jobKey'])
        jsn = self._deserialize_pip_output(std_out)
        pkgs_stable: Dict[str, Dict[str, str]] = {d['name']: d for d in jsn}

        # 6) Package differences
        diff: Dict[str, str] = {}
        for pkg in pkgs_stable:
            if pkgs_preview.get(pkg) is None:
                diff[pkg] = 'not found in preview image'
            elif pkgs_stable[pkg]['version'] != pkgs_preview[pkg]['version']:
                diff[pkg] = f"{pkgs_stable[pkg]['version']} != {pkgs_preview[pkg]['version']}"
        if diff:
            # diffs are expecting when preview image contains release candidates
            print(f'stable vs preview\n{dumps(diff, indent=2, sort_keys=True)}')

        # preview image
        self.assertRegex(pkgs_preview['anura']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_preview['costtoserve']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_preview['dendro']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_preview['frogspawn']['version'], r'2\.[7-9]\.\d+')
        self.assertRegex(pkgs_preview['hopper']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_preview['neo']['version'], r'2\.7\.\d+')

        self.assertTrue(
            any(
                [
                    match(r'2\.7\.\d+', pkgs_preview['optiengines']['version']),
                    match(r'0\.1\.[2-9]\d+\.dev', pkgs_preview['optiengines']['version']),
                ],
            )
        )
        # self.assertRegex(pkgs_preview['optiengines']['version'], r'2\.7\.\d+')

        self.assertRegex(pkgs_preview['optilogic']['version'], r'2\.\d+\.\d')
        self.assertRegex(pkgs_preview['riskrating']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_preview['scenarioexecution']['version'], r'1\.1\.[6-9]')
        self.assertRegex(pkgs_preview['throg']['version'], r'2\.7\.\d+')

        # stable image
        self.assertRegex(pkgs_stable['anura']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['costtoserve']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['dendro']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['frogspawn']['version'], r'2\.[7-9]\.\d+')
        self.assertRegex(pkgs_stable['hopper']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['neo']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['optiengines']['version'], r'0\.1\.[2-3]\d')
        self.assertRegex(pkgs_stable['optilogic']['version'], r'2\.\d+\.\d')
        self.assertRegex(pkgs_stable['riskrating']['version'], r'2\.7\.\d+')
        self.assertRegex(pkgs_stable['scenarioexecution']['version'], r'1\.1\.[6-9]')
        self.assertRegex(pkgs_stable['throg']['version'], r'2\.7\.\d+')

    def test_wksp_job_start_sample(self) -> None:
        '''Create job api call. The response time is the slow and fails often with 504s.'''

        max: int = int(self.API.account_info()['limits']['concurrentJobs'] * 0.5)
        min: int = 10
        job_count: int = max if max > min else min
        jobs: List[str] = []
        tag: str = 'unittest_job_speed'

        # start jobs
        for j in range(job_count):
            with self.subTest():
                resp = self.API.wksp_job_start(
                    self.WKSP, self.py_quick, tags=tag, resourceConfig='mini'
                )
                self.assertEqual(resp['result'], 'success')
            # d = {}
            # d['key'] = resp['jobKey']
            # jobs.append(d)
            # spin up a few jobs to create load and evaluate all

        return
        # what is current job count
        jobs_active: int = self.API._jobs_active
        jobs_max: int = self.API.account_info()['limits']['concurrentJobs']
        max: int = jobs_max - jobs_active if jobs_max > jobs_active else 0

        jobs_max: int = 9
        tag_time: float = time.time()
        tag: str = f'unittest_job_sample_{tag_time}'

        for job in range(jobs_max):
            self.API.wksp_job_start(self.WKSP, self.py_sleep, tags=tag)

        # check the jobs that are about to run
        d: dict = {}
        check: bool = True
        while check:
            jobs = self.API.wksp_jobs(self.WKSP, tags=tag)

            # jobs all finished?
            terminal: int = 0
            for t in self.API.JOBSTATES_TERMINAL:
                terminal += jobs['statusCounts'].get(t)

            if terminal == jobs_max:
                check = False
                break

            # check running jobs for metrics
            active = self.API.wksp_jobs(self.WKSP, status='running', tags=tag)

            if active['statusCounts']['running'] >= 1:
                for job in active['jobs']:
                    resp = self.API.wksp_job_metrics(self.WKSP, job['jobKey'])
                    self.assertEqual(resp['result'], 'success')
                    self.assertIsInstance(resp['count'], int)
                    # self.assertGreaterEqual(resp['count'], 1)

                    # missing metrics!
                    if resp['count'] == 0:
                        st: str = str(job['startDatetime'])
                        st = st.replace('T', ' ')
                        st = st.replace('Z', '')
                        job_start: datetime = datetime.fromisoformat(st)
                        now: datetime = datetime.now(timezone.utc)
                        delta: timedelta = now - job_start
                        d[job['jobKey']] = str(
                            delta
                        )  # store job key and elapsed time without metrics

                        print(
                            f"{str(delta)} secs elapsed and metrics missing for job {job['jobKey']}"
                        )
                        with self.subTest():
                            self.assertLess(delta.total_seconds(), 5)

            time.sleep(1)

        # were there any jobs that failed metric check?
        secs = 0
        if len(d) >= 1:
            print(f"\n\nJob Submitted: {jobs_max}, Job Duration: {secs}, Job Tag: {tag}")
            print('\n JobKey, LastSeenWithMissingMetricCount_RunDuration')
            for k in d.items():
                print(k[1], k[0])

    def test_wksp_job_status(self) -> None:
        '''Get job status for explicit state.'''

        resp: Dict[str, Any] = self.API.wksp_job_status(self.WKSP, self.API._job_start_recent_key)
        self.assertEqual(resp['result'], 'success')

        # varying resp attrs based on job state
        attrs = (
            'billedTime',
            'endDatetime',
            'jobInfo',
            'jobKey',
            'phase',
            'result',
            'runTime',
            'startDatetime',
            'status',
            'submittedDatetime',
        )
        self.assertTrue(all([True if k in attrs else False for k in resp.keys()]))

        # account for active job
        self.assertGreaterEqual(len(resp.keys()), 7)
        self.assertLessEqual(len(resp.keys()), 10)

        self._job_keys(resp)

    def test_wksp_job_stop(self) -> None:
        '''Stop a most recently created job.'''

        # guarantee a job is currently running
        resp = self.API.wksp_job_status(self.WKSP, self.API._job_start_recent_key)
        if resp['status'] in self.API.JOBSTATES_TERMINAL:
            resp = self.API.wksp_job_start(self.WKSP, self.py_sleep, resourceConfig='mini')
            success: bool = self.API.util_job_monitor(self.WKSP, resp['jobKey'])
            if success is False:
                self.skipTest('failed to start job within two minutes')

        # stop running job
        resp = self.API.wksp_job_stop(self.WKSP, self.API._job_start_recent_key)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['jobKey'], self.API._job_start_recent_key)
        keys: Tuple[str, ...] = ('result', 'message', 'jobKey', 'status', 'jobInfo')
        for key in resp.keys():
            self.assertIn(key, keys)

    def test_wksp_jobify(self) -> None:
        '''Batch queue many jobs.'''

        batch = {
            'batchItems': [
                {'pyModulePath': '/projects/quick_tests/sleep.py', 'timeout': 90},
                {
                    'pyModulePath': '/projects/quick_tests/airline_hub_location_cbc.py',
                    'timeout': 30,
                },
            ]
        }

        tag: str = 'unittest_batch_jobify'
        resp = self.API.wksp_jobify(self.WKSP, batch=batch, tags=tag)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'Jobs submitted')
        self.assertIsInstance(resp['count'], int)
        self.assertEqual(resp['count'], len(resp['jobKeys']))
        for key in resp['jobKeys']:
            self.assertIsInstance(key, str)
            self.assertEqual(len(key), 36)

    def test_wksp_jobify_findnrun(self) -> None:
        '''Search file paths yields many jobs to run each python module found.'''

        batch = {
            'batchItems': [
                {'pySearchTerm': '^/quick_tests/sleep.py', 'timeout': 90},
                {'pySearchTerm': '^/quick_tests/airline_hub_location_cbc.py', 'timeout': 30},
            ]
        }

        tag: str = 'unittest_batch_jobify_find'
        resp = self.API.wksp_jobify_findnrun(self.WKSP, batch=batch, tags=tag)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(resp['message'], 'Jobs submitted')
        self.assertIsInstance(resp['count'], int)
        self.assertEqual(len(batch['batchItems']), resp['count'])
        self.assertEqual(resp['count'], len(resp['jobKeys']))
        for key in resp['jobKeys']:
            self.assertIsInstance(key, str)
            self.assertEqual(len(key), 36)

    def test_wksp_jobs(self) -> None:
        '''List the jobs for a specific workspace.'''

        resp: Dict[str, Any] = self.API.wksp_jobs(self.WKSP)
        self.assertEqual(resp['result'], 'success')
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['statusCounts'], dict)

        status_keys: Tuple[str, ...] = self.API.JOBSTATES
        for status in resp['statusCounts']:
            self.assertIn(status, status_keys)
            self.assertGreaterEqual(resp['statusCounts'][status], 0)

        self.assertIsInstance(resp['tagCounts'], dict)
        self.assertIsInstance(resp['filters'], dict)

        filter_keys: Tuple[str, ...] = (
            'command',
            'history',
            'runSecsMax',
            'runSecsMin',
            'status',
            'tags',
        )
        for filter in resp['filters']:
            self.assertIn(filter, filter_keys)

        self.assertGreaterEqual(len(resp['jobs']), 1)

        for job in resp['jobs']:
            self._job_keys(job)

    def test_wksp_jobs_stats(self) -> None:
        '''Get the stats for jobs for a specific workspace.'''

        resp: Dict[str, Any] = self.API.wksp_jobs(self.WKSP)
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 6)
        self.assertIsInstance(resp['count'], int)
        self.assertIsInstance(resp['statusCounts'], dict)

        status_keys: Tuple[str, ...] = self.API.JOBSTATES
        for status in resp['statusCounts']:
            self.assertIn(status, status_keys)
            self.assertGreaterEqual(resp['statusCounts'][status], 0)

        self.assertIsInstance(resp['tagCounts'], dict)
        self.assertIsInstance(resp['filters'], dict)

        filter_keys: Tuple[str, ...] = (
            'command',
            'history',
            'runSecsMax',
            'runSecsMin',
            'status',
            'tags',
        )
        for filter in resp['filters']:
            self.assertIn(filter, filter_keys)

        for job in resp['jobs']:
            self._job_keys(job)

    def test_wksp_share_file(self) -> None:
        '''Share a file from a workspace to all other workspaces of a user/self.'''

        if self.API.auth_username is None:
            self.skipTest('test_wksp_share_folder requires a username')

        resp = self.API.wksp_share_file(
            self.WKSP, file_path=self.py_sleep, targetUsers=self.API.auth_username
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 8)
        self.assertIsInstance(resp['errored'], list)
        self.assertEqual(len(resp['errored']), 0)
        self.assertIsInstance(resp['erroredCount'], int)
        self.assertIsInstance(resp['jobs'], list)
        self.assertEqual(len(resp['jobs']), self.API.account_workspace_count - 1)
        for j in resp['jobs']:
            self.assertIsInstance(j['jobKey'], str)
            self.assertIsInstance(j['result'], str)
            self.assertEqual(j['result'], 'success')
        self.assertEqual(resp['jobsCount'], self.API.account_workspace_count - 1)
        self.assertIsInstance(resp['message'], str)
        self.assertEqual(resp['message'], 'Share Accepted')
        self.assertIsInstance(resp['sourceFileInfo'], dict)
        self.assertEqual(len(resp['sourceFileInfo'].keys()), 2)
        self.assertIsInstance(resp['sourceFileInfo']['directoryPath'], str)
        self.assertEqual(resp['sourceFileInfo']['directoryPath'], path.split(self.py_sleep)[0])
        self.assertIsInstance(resp['sourceFileInfo']['filename'], str)
        self.assertEqual(resp['sourceFileInfo']['filename'], path.split(self.py_sleep)[1])
        self.assertEqual(resp['targetUsers'], self.API.auth_username)

    def test_wksp_share_file_sample(self) -> None:
        '''OE-5840 API Share File/Folder Results in 500 Internal Server Error.'''

        if self.API.auth_username is None:
            self.skipTest('test_wksp_share_folder requires a username')

        if self.API.account_workspace_count < 2:
            self.skipTest('account does not have required multi-workspaces needed for sharing')

        test_result: bool = False

        # get all not Studio workspaces
        resp: dict = self.API.account_workspaces()
        wksp_names: list[str] = [w['name'] for w in resp['workspaces'] if w['name'] != 'Studio']
        wksp_not_studio: str = wksp_names[0]

        # upload files to share
        filenames: list[str] = []
        filepaths: list[str] = []
        tag: int = time.perf_counter_ns()
        for x in range(10):
            filename: str = f'{tag}_{x}.txt'
            file_path: str = f'/My Files/{tag}/{filename}'
            file_contents: str = f'{datetime.now()} {tag}_{x} unittest test_wksp_share_file_sample'
            resp = self.API.wksp_file_upload('Studio', file_path, filestr=file_contents)
            if resp.get('crash'):
                print(f'{x} {filename} upload attempt failed')
                continue
            filenames.append(filename)
            filepaths.append(file_path)

        # verify uploaded files arrived
        up_arrived: bool = False
        up_count_verified: int = 0
        up_start: float = time.perf_counter()

        while up_arrived is False and time.perf_counter() - up_start < 30:
            resp = self.API.wksp_files('Studio', str(tag))
            if resp.get('crash'):
                continue

            up_count_verified = resp.get('count', 0)
            print(
                f'{tag} {up_count_verified}/{len(filepaths)} confirmed files uploaded {time.perf_counter() - up_start} secs'
            )
            if resp.get('count') == len(filepaths):
                up_arrived = True
                break
            time.sleep(2)

        if up_arrived is False:
            print(f'verify upload failed {len(filepaths)} - {up_count_verified} files missing')
            print('30 seconds not enough time to verify?')

        # share files to other workspaces
        files_failed_sharing: int = 0
        for fp in filepaths:
            resp = self.API.wksp_share_file('Studio', fp, targetUsers=self.API.auth_username)
            if resp.get('crash'):
                print(f'share crash skipping {fp}')
                files_failed_sharing += 1

        # verify shared files arrived to determine test case can pass
        share_arrived: bool = False
        start_share: float = time.perf_counter()
        # TODO verify file share arrived to all non studio workspaces
        diffs = set()
        while share_arrived is False and time.perf_counter() - start_share < 180:
            resp = self.API.wksp_files(wksp_not_studio, str(tag))
            filenames_verified: set[str] = {f['filename'] for f in resp['files']}
            diffs: set[str] = set(filenames).symmetric_difference(filenames_verified)
            if resp.get('count') == up_count_verified and len(diffs) == 0:
                share_arrived = True
                break
            elif resp.get('count', 0) > up_count_verified:
                # BUG there might be file share retry logic
                # 1156398951931738_1.txt failed to share due to 500/504 issue but it showed up 5mins later
                # 1156398951931738_1_2022-10-15T021756Z.txt server tried more than once and created a duplicate!
                break
            time.sleep(2)

        if share_arrived:
            test_result = True
        else:
            print(f'verify share file diff: {len(diffs)}\n{sorted(diffs)}')

        # cleanup: remove files used to share out
        self.API.wksp_folder_delete('Studio', f'My Files/{tag}', force=True)

        # cleanup: remove files shared to other workspaces
        share_folders: list[str] = ['Sent to Me', 'sent_to_me']
        for ws in wksp_names:
            for share_folder in share_folders:
                resp = self.API.wksp_files(ws, share_folder)
                if resp.get('count') == 0:
                    continue
                for fn in filenames:
                    self.API.wksp_file_delete(ws, f'{share_folder}/{self.API.auth_username}/{fn}')

        self.assertTrue(test_result)

    def test_wksp_share_folder(self) -> None:
        '''Share a subtree from a workspace to all other workspaces of a user/self.'''

        if self.API.auth_username is None:
            self.skipTest('test_wksp_share_folder requires a username')

        resp = self.API.wksp_share_folder(
            self.WKSP, dir_path=self.dir_testdata_remote, targetUsers=self.API.auth_username
        )
        self.assertEqual(resp['result'], 'success')
        self.assertEqual(len(resp.keys()), 8)
        self.assertIsInstance(resp['errored'], list)
        self.assertEqual(len(resp['errored']), 0)
        self.assertIsInstance(resp['erroredCount'], int)
        self.assertIsInstance(resp['jobs'], list)
        self.assertEqual(len(resp['jobs']), self.API.account_workspace_count - 1)
        for j in resp['jobs']:
            self.assertIsInstance(j['jobKey'], str)
            self.assertIsInstance(j['result'], str)
            self.assertEqual(j['result'], 'success')
        self.assertEqual(resp['jobsCount'], self.API.account_workspace_count - 1)
        self.assertIsInstance(resp['message'], str)
        self.assertEqual(resp['message'], 'Share Accepted')
        self.assertIsInstance(resp['sourceFileInfo'], dict)
        self.assertEqual(len(resp['sourceFileInfo'].keys()), 1)
        self.assertIsInstance(resp['sourceFileInfo']['directoryPath'], str)
        self.assertEqual(resp['sourceFileInfo']['directoryPath'], self.dir_testdata_remote)
        self.assertEqual(resp['targetUsers'], self.API.auth_username)


if __name__ == '__main__':
    # !! TODO update module docstring to set your user defaults !!
    # apikey replace YOUR_USERNAME, YOUR_PASSWORD
    # appkey replace YOUR_USERNAME, YOUR_APPLICATION_KEY, and set auth_legacy to False

    args: dict = docopt(__doc__)
    TestApi.APPKEY = args.get('--appkey')
    TestApi.AUTH_LEGACY = args.get('--authlegacy', '').lower() == 'true'
    TestApi.USERNAME = args.get('--user')
    TestApi.USERPASS = args.get('--pass')
    TestApi.WKSP = args.get('--wksp', 'Studio')
    unittest.main(__name__, argv=['main'])
