#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest import main
from unittest.mock import MagicMock
from unittest.mock import patch

from uhw.protocol import find
from uhw.protocol import ProtocolFactory


class TestProtocol(TestCase):
    def test_find_no_match(self):
        result = find({}, "NO_MATCH")
        self.assertIsNone(result)

    def test_find_match(self):
        mock_regex = MagicMock()
        mock_regex.match.return_value = True
        commands = {"TEST": {"regex": mock_regex}}
        result = find(commands, "TEST")
        self.assertEqual(result, commands["TEST"])


class TestProtocolFactory(TestCase):
    def setUp(self):
        self.transport = MagicMock()
        self.protocol = ProtocolFactory({})
        self.protocol.connection_made(self.transport)

    @patch("uhw.protocol.split_line")
    @patch("uhw.protocol.find")
    def test_data_received(self, mock_find, mock_split_line):
        mock_split_line.return_value = [
            ("COMMAND", "ARGS", False),
        ]
        mock_find.return_value = {
            "push": MagicMock(),
            "pull": MagicMock(),
        }
        self.protocol.data_received(b"DUMMY")
        self.transport.write.assert_not_called()

    @patch("uhw.protocol.split_line")
    @patch("uhw.protocol.find")
    def test_data_received_as_query(self, mock_find, mock_split_line):
        mock_split_line.return_value = [
            ("COMMAND", "ARGS", True),
        ]
        mock_find.return_value = {
            "push": MagicMock(),
            "pull": MagicMock(),
        }
        self.protocol.data_received(b"DUMMY")
        self.transport.write.assert_called_once()


if __name__ == "__main__":
    main()
