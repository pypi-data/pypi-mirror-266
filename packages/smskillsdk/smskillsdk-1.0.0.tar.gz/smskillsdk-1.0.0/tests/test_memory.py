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
from smskillsdk.utils import memory


class TestMemoryUtils(unittest.TestCase):
    def test_serialize(self):
        memory_dict = {
            "key1": "value1",
            "key2": True,
            "key3": None,
        }

        memory_array = memory.serialize_memory(memory_dict)
        self.assertEqual(len(memory_array), 3)

        for memory_element in memory_array:
            self.assertIsNone(memory_element.session_id)
            self.assertIn(memory_element.name, memory_dict)
            self.assertEqual(memory_element.value, memory_dict[memory_element.name])

    def test_serialize_with_session_id(self):
        memory_dict = {
            "key1": "value1",
            "key2": True,
            "key3": None,
        }
        session_id = "123"

        memory_array = memory.serialize_memory(memory_dict, session_id)
        self.assertEqual(len(memory_array), 3)

        for memory_element in memory_array:
            self.assertIn(memory_element.name, memory_dict)
            self.assertEqual(memory_element.value, memory_dict[memory_element.name])
            self.assertEqual(memory_element.session_id, session_id)

    def test_serialize_with_scope(self):
        memory_dict = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        scope = MemoryScope.PUBLIC

        memory_array = memory.serialize_memory(memory_dict, scope=scope)
        self.assertEqual(len(memory_array), 3)

        for memory_element in memory_array:
            self.assertIn(memory_element.name, memory_dict)
            self.assertEqual(memory_element.value, memory_dict[memory_element.name])
            self.assertEqual(memory_element.scope, scope)

    def test_deserialize(self):
        memory_array = [
            Memory(**{"name": "key1", "value": "value1"}),
            Memory(**{"name": "key2", "value": 1}),
            Memory(**{"name": "key3", "value": {"subkey2": "subvalue2"}}),
        ]

        memory_dict = memory.deserialize_memory(memory_array)
        self.assertEqual(len(memory_dict), 3)

        for memory_element in memory_array:
            self.assertIn(memory_element.name, memory_dict)
            self.assertEqual(memory_element.value, memory_dict[memory_element.name])

    def test_deserialize_with_session_id(self):
        memory_array = [
            Memory(**{"name": "key1", "value": "value1", "session_id": "123"}),
            Memory(**{"name": "key2", "value": 1}),
            Memory(
                **{
                    "name": "key3",
                    "value": {"subkey2": "subvalue2"},
                    "session_id": "123",
                }
            ),
        ]

        memory_dict = memory.deserialize_memory(memory_array, "123")
        self.assertEqual(set(memory_dict.keys()), {"key1", "key3"})

    def test_deserialize_with_scope(self):
        memory_array = [
            Memory(**{"name": "key1", "value": "1", "scope": "PUBLIC"}),
            Memory(**{"name": "key2", "value": "2", "scope": "PRIVATE"}),
            Memory(**{"name": "key3", "value": "3"}),
            Memory(**{"name": "key4", "value": "4", "scope": "PRIVATE"}),
            Memory(**{"name": "key5", "value": "5", "scope": "PUBLIC"}),
        ]

        memory_dict = memory.deserialize_memory(memory_array, scope=MemoryScope.PUBLIC)
        self.assertEqual(set(memory_dict.keys()), {"key1", "key5"})

        memory_dict = memory.deserialize_memory(memory_array, scope=MemoryScope.PRIVATE)
        self.assertEqual(set(memory_dict.keys()), {"key2", "key3", "key4"})

        memory_dict = memory.deserialize_memory(memory_array)
        self.assertEqual(
            set(memory_dict.keys()), {"key1", "key2", "key3", "key4", "key5"}
        )

    def test_set_memory_value(self):
        memories: List[Memory] = list()

        memory.set_memory_value(memories, "key1", "value1")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0].name, "key1")
        self.assertEqual(memories[0].value, "value1")

        memory.set_memory_value(memories, "key1", "value2", "sessionid1")
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].name, "key1")
        self.assertEqual(memories[0].value, "value1")
        self.assertIsNone(memories[0].session_id)
        self.assertEqual(memories[-1].name, "key1")
        self.assertEqual(memories[-1].value, "value2")
        self.assertEqual(memories[-1].session_id, "sessionid1")

        memory.set_memory_value(memories, "key1", "value3")
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].name, "key1")
        self.assertEqual(memories[0].value, "value3")
        self.assertEqual(memories[-1].name, "key1")
        self.assertEqual(memories[-1].value, "value2")

        memory.set_memory_value(memories, "key1", "value4", "sessionid1")
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].name, "key1")
        self.assertEqual(memories[0].value, "value3")
        self.assertEqual(memories[-1].name, "key1")
        self.assertEqual(memories[-1].value, "value4")

        memory.set_memory_value(memories, "key1", "value5", scope=MemoryScope.PRIVATE)
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].name, "key1")
        self.assertEqual(memories[0].value, "value5")
        self.assertEqual(memories[-1].name, "key1")
        self.assertEqual(memories[-1].value, "value4")

        memory.set_memory_value(memories, "key2", "value6")
        self.assertEqual(len(memories), 3)
        self.assertEqual(memories[-1].name, "key2")
        self.assertEqual(memories[-1].value, "value6")

        memory.set_memory_value(memories, "key2", "value7", scope=MemoryScope.PUBLIC)
        self.assertEqual(len(memories), 4)
        self.assertEqual(memories[-1].name, "key2")
        self.assertEqual(memories[-1].value, "value7")

    def test_get_memory_value(self):
        memories: List[Memory] = list()

        self.assertEqual(memory.get_memory_value(memories, "key1")[0], False)

        memories.append(Memory(**{"name": "key1", "value": "value1"}))
        self.assertEqual(memory.get_memory_value(memories, "key1"), (True, "value1"))
        self.assertFalse(
            memory.get_memory_value(memories, "key1", scope=MemoryScope.PUBLIC)[0]
        )
        self.assertTrue(
            memory.get_memory_value(memories, "key1", scope=MemoryScope.PRIVATE)[0]
        )

        memories.append(
            Memory(**{"name": "key1", "value": "value2", "session_id": "sessionid1"})
        )
        self.assertEqual(memory.get_memory_value(memories, "key1"), (True, "value1"))
        self.assertEqual(
            memory.get_memory_value(memories, "key1", "sessionid1"), (True, "value2")
        )
        self.assertFalse(memory.get_memory_value(memories, "key1", "sessionid2")[0])

        memories.append(
            Memory(**{"name": "key1", "value": "value3", "scope": "PUBLIC"})
        )
        self.assertEqual(memory.get_memory_value(memories, "key1"), (True, "value1"))
        self.assertEqual(
            memory.get_memory_value(memories, "key1", scope=MemoryScope.PRIVATE),
            (True, "value1"),
        )
        self.assertEqual(
            memory.get_memory_value(memories, "key1", scope=MemoryScope.PUBLIC),
            (True, "value3"),
        )


if __name__ == "__main__":
    unittest.main()
