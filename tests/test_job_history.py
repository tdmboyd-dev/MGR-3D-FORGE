"""Saved journal navigation must not create, retry or accept corrupt output."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from forge.cli import build
from forge.spec import WorldSpec
from forge.studio_server import ForgeWorkstation
from forge.job_history import SOURCES


class SavedJobsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        build(WorldSpec(seed=9, columns=2, rows=2, buildings=2), self.root / 'world')
        self.studio = ForgeWorkstation(self.root / 'world', self.root / 'workspace')

    def listing(self, **payload):
        return self.studio.command('/api/saved-jobs', payload)

    def create(self):
        return self.studio.command('/api/creature-create', {
            'request_id': 'saved-creature-001', 'prompt': 'original winged crystal creature',
            'seed': 31, 'variants': 1, 'morph': {}})

    def test_empty_reads_never_allocate_jobs_or_ledgers(self):
        before = sorted(p.name for p in self.studio.workspace.iterdir())
        self.assertEqual(self.listing()['items'], [])
        self.assertEqual(self.studio.command('/api/saved-job-reopen', {
            'kind': 'creature', 'request_id': 'not-found-00001'})['status'], 'NOT_FOUND')
        self.assertEqual(before, sorted(p.name for p in self.studio.workspace.iterdir()))

    def test_real_saved_creature_survives_restart_and_reopen_never_creates(self):
        original = self.create()
        ledger = self.studio.workspace / 'creature-requests.json'
        before = ledger.read_bytes()
        self.studio = ForgeWorkstation(self.root / 'world', self.root / 'workspace')
        item, = self.listing()['items']
        self.assertFalse(item['artifact_verified'])
        with patch.object(self.studio, 'create_job', side_effect=AssertionError('read created a job')):
            reopened = self.studio.command('/api/saved-job-reopen', {
                'kind': item['kind'], 'request_id': item['request_id']})
        self.assertEqual(reopened['creature_sha256'], original['creature_sha256'])
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 1)

    def test_tampered_artifact_cannot_reopen_even_if_journal_claims_materialized(self):
        original = self.create()
        asset = self.studio.valid_job(original['job_id']) / 'creature' / 'creature.glb'
        asset.write_bytes(asset.read_bytes() + b'corrupt')
        self.assertFalse(self.listing()['items'][0]['artifact_verified'])
        with self.assertRaisesRegex(RuntimeError, 'SHA-256'):
            self.studio.command('/api/saved-job-reopen', {
                'kind': 'creature', 'request_id': original['request_id']})
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 1)

    def test_all_five_original_journals_and_interrupted_state_without_leaking_payloads(self):
        for kind, (ledger, _) in SOURCES.items():
            rows = {'history-request-0001': {'job_id': 'a' * 24, 'status': 'RUNNING',
                    'prompt': 'PRIVATE ORIGINAL', 'private_path': 'private/path'}}
            (self.studio.workspace / ledger).write_text(json.dumps(rows), encoding='utf8')
        result = self.listing()
        self.assertEqual({row['kind'] for row in result['items']}, set(SOURCES))
        self.assertTrue(all(row['status'] == 'NEEDS_RECONCILIATION' for row in result['items']))
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('private/path', json.dumps(result))
        self.studio.human_active_jobs.add('history-request-0001')
        self.assertEqual(self.listing(kind='human')['items'][0]['status'], 'RUNNING')

    def test_pagination_is_stable_filtered_and_stale_cursor_refuses(self):
        rows = {f'page-request-{i:04}': {'job_id': f'{i:024x}', 'status': 'STARTED'} for i in range(45)}
        ledger = self.studio.workspace / 'creature-requests.json'
        ledger.write_text(json.dumps(rows), encoding='utf8')
        result = self.listing(kind='creature')
        seen = result['items'][:]
        while result['next_cursor']:
            result = self.listing(kind='creature', cursor=result['next_cursor'])
            seen.extend(result['items'])
        self.assertEqual(len(seen), 45)
        self.assertEqual(len({r['request_id'] for r in seen}), 45)
        cursor = self.listing(limit=1)['next_cursor']
        rows['page-request-0000']['status'] = 'FAILED'
        ledger.write_text(json.dumps(rows), encoding='utf8')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.listing(cursor=cursor)

    def test_corrupt_journal_is_explicit_and_other_kind_still_works(self):
        self.create()
        ledger = self.studio.workspace / 'world-requests.json'
        for raw in ('broken json', json.dumps({'bad': None}), json.dumps({'valid-request-0001': {'status': []}})):
            ledger.write_text(raw, encoding='utf8')
            result = self.listing()
            self.assertEqual(result['unavailable_kinds'], ['world'])
            self.assertEqual(len(result['items']), 1)
            self.assertEqual(result['items'][0]['kind'], 'creature')

    def test_invalid_inputs_and_read_only_reopen_contract(self):
        for payload in ({'limit': True}, {'limit': 21}, {'kind': []}, {'kind': 'external'},
                        {'cursor': '../'}, {'cursor': 'a' * 64 + ':9999'}, {'create': True}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.studio.command('/api/saved-jobs', payload)
        for payload in ({'kind': 'creature', 'request_id': '../'},
                        {'kind': [], 'request_id': 'valid-request-001'},
                        {'kind': 'creature', 'request_id': 'valid-request-001', 'retry': True}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.studio.command('/api/saved-job-reopen', payload)
        self.assertEqual(len(list(self.studio.jobs.iterdir())), 0)
