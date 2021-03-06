import types
from unittest import mock

from base import CachetTestcase
import cachetclient
from fakeapi import FakeHttpClient


@mock.patch('cachetclient.client.HttpClient', new=FakeHttpClient)
class SubscriberTests(CachetTestcase):

    def test_create(self):
        client = self.create_client()
        sub = client.subscribers.create(email='user@example.com')
        self.assertEqual(sub.id, 1)
        self.assertEqual(sub.email, 'user@example.com')

        # Count subscribers
        self.assertEqual(client.subscribers.count(), 1)

        # Inspect subscribers
        sub = next(client.subscribers.list())
        self.assertEqual(sub.id, 1)
        self.assertEqual(sub.email, 'user@example.com')
        self.assertTrue(sub.is_global)
        self.assertIsNotNone(sub.verify_code)
        self.assertIsNotNone(sub.verified_at)
        self.assertIsNotNone(sub.created_at)
        self.assertIsNotNone(sub.updated_at)

        # Delete subscriber
        sub.delete()
        self.assertEqual(client.subscribers.count(), 0)

    def test_list(self):
        """Create a bunch of subscribers and list them"""
        client = self.create_client()
        num_subs = 20 * 4 + 5
        for i in range(num_subs):
            client.subscribers.create(
                email="user{}@example.com".format(str(i).zfill(3)),
                verify=True,
            )

        # Ensure the count matches
        self.assertEqual(client.subscribers.count(), num_subs)

        # List should return a generator
        self.assertIsInstance(client.subscribers.list(), types.GeneratorType)

        # Request specific page
        sub = next(client.subscribers.list(page=2, per_page=10))
        self.assertEqual(sub.id, 11)

        # Delete them all (We cannot delete while iterating)
        subs = list(client.subscribers.list())
        self.assertEqual(len(subs), num_subs)
        self.assertEqual(len(set(subs)), num_subs)
        for sub in subs:
            sub.delete()

        # We should have no subs left
        self.assertEqual(client.subscribers.count(), 0)
