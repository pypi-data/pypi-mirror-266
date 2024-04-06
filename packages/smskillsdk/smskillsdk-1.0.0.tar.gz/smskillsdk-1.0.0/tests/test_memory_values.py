# Copyright 2024 Soul Machines Ltd

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from typing import List

from smskillsdk.models.common import Memory, MemoryScope
from smskillsdk.utils.memory_values import (
    get_user_identity,
    get_user_location,
    set_user_identity,
    set_user_location,
)


class TestMemoryUtils(unittest.TestCase):
    def test_user_identity(self):
        memories: List[Memory] = list()

        set_user_identity(memories, first_name="Joe", preferred_name="Bob")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].scope, MemoryScope.PUBLIC)

        user_identity = get_user_identity(memories)
        self.assertIsNotNone(user_identity)
        self.assertEqual(user_identity.firstName, "Joe")
        self.assertEqual(user_identity.preferredName, "Bob")
        self.assertIsNone(user_identity.lastName)
        self.assertIsNone(user_identity.id)

        set_user_identity(memories, last_name="Bloggs")
        self.assertEqual(len(memories), 1)

        user_identity = get_user_identity(memories)
        self.assertIsNotNone(user_identity)
        self.assertEqual(user_identity.firstName, "Joe")
        self.assertEqual(user_identity.preferredName, "Bob")
        self.assertEqual(user_identity.lastName, "Bloggs")
        self.assertIsNone(user_identity.id)

    def test_user_location(self):
        memories: List[Memory] = list()

        set_user_location(memories, city="Auckland")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].scope, MemoryScope.PUBLIC)

        user_location = get_user_location(memories)
        self.assertIsNotNone(user_location)
        self.assertEqual(user_location.city, "Auckland")
        self.assertIsNone(user_location.country)

        set_user_location(memories, country="New Zealand")
        self.assertEqual(len(memories), 1)

        user_location = get_user_location(memories)
        self.assertIsNotNone(user_location)
        self.assertEqual(user_location.city, "Auckland")
        self.assertEqual(user_location.country, "New Zealand")


if __name__ == "__main__":
    unittest.main()
