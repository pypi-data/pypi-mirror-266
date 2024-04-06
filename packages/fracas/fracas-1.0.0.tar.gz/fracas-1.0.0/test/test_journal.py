import unittest
from unittest.mock import patch

import fracas.journal
import fracas.io


class Args:
    def __init__(self, to_date=None, from_date=None, search_terms=""):
        self.to_date = to_date
        self.from_date = from_date
        self.search_terms = search_terms


class TestDateRange(unittest.TestCase):
    def setUp(self):
        self.d = {
            "1964-11-24 12:00": "a",
            "1987-02-13 12:00": "c",
            "2023-11-14 12:00": "d",
        }

    def test_from(self):
        args = Args(from_date="1980-01-01 01:00")
        found = fracas.journal.search_date_range(self.d, args)
        self.assertEqual(len(found.values()), 2)
        self.assertTrue("c" in found.values())
        self.assertTrue("d" in found.values())

    def test_to(self):
        args = Args(to_date="1980-01-01 01:00")
        found = fracas.journal.search_date_range(self.d, args)
        self.assertEqual(len(found.values()), 1)
        self.assertTrue("a" in found.values())

    def test_to_from(self):
        args = Args(from_date="1970-05-30 01:00", to_date="1995-01-01 01:00")
        found = fracas.journal.search_date_range(self.d, args)
        self.assertEqual(len(found.values()), 1)
        self.assertTrue("c" in found.values())

    def test_validate_date(self):
        self.assertTrue(fracas.journal.validate("1980-01-01 01:00"))
        with self.assertRaises(ValueError):
            fracas.journal.validate("1980/01/01 01:00")

        self.assertTrue(fracas.journal.validate("1980-01-01"))
        with self.assertRaises(ValueError):
            fracas.journal.validate("1980/01/01")


class TestDiff(unittest.TestCase):
    def setUp(self):
        self.d1 = {
            "1964-11-24 12:00": "a",
            "1987-02-13 12:00": "b",
            "2023-11-14 12:00": "c",
        }

    def test_add(self):
        s1 = fracas.io.join(self.d1)
        # Text editor adds 1 entry.
        s2 = "1964-11-24 12:00\na\n1987-02-13 12:00\nb\n2023-11-14 12:00\nc\n2024-02-24 12:00\nd\n"
        d2 = fracas.io.split(s2)
        diff = fracas.journal.diff(self.d1, d2)
        msg = "0 modified, 0 deleted, 1 added."
        self.assertEqual(diff, msg)

    def test_delete(self):
        s1 = fracas.io.join(self.d1)
        # Text editor deletes 1 entry.
        s2 = "1964-11-24 12:00\na\n2023-11-14 12:00\nc"
        d2 = fracas.io.split(s2)
        diff = fracas.journal.diff(self.d1, d2)
        msg = "0 modified, 1 deleted, 0 added."
        self.assertEqual(diff, msg)

    def test_modify(self):
        s1 = fracas.io.join(self.d1)
        # Text editor adds 1 entry.
        s2 = "1964-11-24 12:00\na\n1987-02-13 12:00\nx\n2023-11-14 12:00\nc\n"
        d2 = fracas.io.split(s2)
        diff = fracas.journal.diff(self.d1, d2)
        msg = "1 modified, 0 deleted, 0 added."
        self.assertEqual(diff, msg)


class TestEdit(unittest.TestCase):
    def setUp(self):
        self.d1 = {
            "1964-11-24 12:00": "a",
            "1987-02-13 12:00": "b",
            "2023-11-14 12:00": "c",
        }

    @patch("fracas.journal.edit_file")
    @patch("fracas.io.write")
    @patch("fracas.io.read")
    def test_add(self, mock_read, mock_write, mock_edit):
        mock_read.return_value = self.d1
        mock_edit.return_value = (
            "1987-02-13 12:00\nb\n2023-11-14 12:00\nc\n2024-04-27 12:00\nd"
        )
        args = Args(from_date="1986-01-01")
        stats = fracas.journal.edit(args)
        msg = "0 modified, 0 deleted, 1 added."
        self.assertEqual(stats, msg)

    @patch("fracas.journal.edit_file")
    @patch("fracas.io.write")
    @patch("fracas.io.read")
    def test_delete(self, mock_read, mock_write, mock_edit):
        mock_read.return_value = self.d1
        mock_edit.return_value = "1987-02-13 12:00\nb"
        args = Args(from_date="1986-01-01")
        stats = fracas.journal.edit(args)
        msg = "0 modified, 1 deleted, 0 added."
        self.assertEqual(stats, msg)

    @patch("fracas.journal.edit_file")
    @patch("fracas.io.write")
    @patch("fracas.io.read")
    def test_modify(self, mock_read, mock_write, mock_edit):
        mock_read.return_value = self.d1
        mock_edit.return_value = "1987-02-13 12:00\nb\n2023-11-14 12:00\nhello"
        args = Args(from_date="1986-01-01")
        stats = fracas.journal.edit(args)
        msg = "1 modified, 0 deleted, 0 added."
        self.assertEqual(stats, msg)


class TestKeywordSearch(unittest.TestCase):
    def test_simple(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["Nature's"])
        self.assertEqual(len(found), 1)
        self.assertTrue("2024-02-17 06:01" in found)

    def test_phrase(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["HUMAN EVENTS"])
        self.assertEqual(len(found), 1)
        self.assertTrue("2023-10-12 11:41" in found)

    def test_and(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary law #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["law", "nature"])
        self.assertEqual(len(found), 1)
        self.assertTrue("2024-02-17 06:01" in found)

    def test_or(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary law #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["god|political"])
        self.assertEqual(len(found), 2)
        self.assertTrue("2023-10-12 11:59" in found)
        self.assertTrue("2024-02-17 06:01" in found)


class TestTagSearch(unittest.TestCase):
    def test_simple(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["#tag2"])
        self.assertEqual(len(found), 2)
        self.assertTrue("2023-10-12 11:59" in found)
        self.assertTrue("2024-02-17 06:01" in found)

    def test_space(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary#tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag1

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag12345
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["#tag1"])
        self.assertEqual(len(found), 1)
        self.assertTrue("2023-10-12 11:59" in found)

    def test_hyphen(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary #tag1-2

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag1

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag1-23

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag1-2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["#tag1-2"])
        self.assertEqual(len(found), 2)
        self.assertTrue("2023-10-12 11:41" in found)
        self.assertTrue("2024-02-17 06:01" in found)

    def test_or(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary law #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #tag2
        """
        d = fracas.io.split(s)
        found = fracas.journal.find(d, ["#tag1|#tag2"])
        self.assertEqual(len(found), 3)
        self.assertTrue("2023-10-12 11:41" in found)
        self.assertTrue("2023-10-12 11:59" in found)
        self.assertTrue("2024-02-17 06:01" in found)

    def test_tag_count(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary #tag1

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another, #tag2

        2023-11-24 17:21
        and to assume among the powers of the earth, #tag3

        2024-02-17 06:01
        the separate and equal station to which the Laws of Nature and
        of Nature's God entitle them #Tag2
        """
        entries = fracas.io.split(s)
        tags = fracas.journal.get_tag_count(entries)
        self.assertEqual(tags, {"#tag1": 1, "#tag2": 2, "#tag3": 1})


if __name__ == "__main__":
    unittest.main()
