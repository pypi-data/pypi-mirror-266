#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import Pattern
from unittest import main
from unittest import TestCase

from uhw.parser import command_to_regex
from uhw.parser import command_to_compiled_regex
from uhw.parser import split_line


class ParserTestCase(TestCase):
    def test_split_line(self):
        result = split_line("TESTA;TESTB?")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], tuple)
        self.assertEqual(len(result[0]), 3)

    def test_command_to_regex(self):
        result = command_to_regex("")
        self.assertIsInstance(result, str)

    def test_command_to_compiled_regex(self):
        result = command_to_compiled_regex("")
        self.assertIsInstance(result, Pattern)


if __name__ == "__main__":
    main()
