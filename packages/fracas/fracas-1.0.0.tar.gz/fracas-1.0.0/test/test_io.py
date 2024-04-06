import unittest

import fracas.io


class TestSplit(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(fracas.io.split(""), {})

    def test_date(self):
        s = """
        2023-10-12 11:41
        When in the course of human events it becomes necessary...

        2023-10-12 11:59
        for one people to dissolve the political bands which have
        connected them with another.

        2023-11-24 17:21
        and to assume among the powers of the earth.
        """
        d = fracas.io.split(s)
        self.assertEqual(len(d), 3)
        b1 = d["2023-10-12 11:41"]
        b2 = d["2023-10-12 11:59"]
        b3 = d["2023-11-24 17:21"]
        self.assertTrue("When in the course of human events" in b1)
        self.assertTrue("for one people to dissolve" in b2)
        self.assertTrue("and to assume among the powers" in b3)

    def test_title(self):
        s = """
        2023-10-12 11:41 Declaration Part I
        When in the course of human events it becomes necessary...

        2023-10-12 11:59 Declaration Part II
        for one people to dissolve the political bands which have
        connected them with another.

        2023-11-24 17:21 Declaration Part III
        and to assume among the powers of the earth.
        """
        d = fracas.io.split(s)
        self.assertEqual(len(d), 3)
        b1 = d["2023-10-12 11:41"]
        b2 = d["2023-10-12 11:59"]
        b3 = d["2023-11-24 17:21"]
        self.assertTrue("Declaration Part I" in b1)
        self.assertTrue("Declaration Part II" in b2)
        self.assertTrue("Declaration Part III" in b3)


class TestJoin(unittest.TestCase):
    def test_title(self):
        s = """
        2023-10-12 11:41 Declaration Part I
        When in the course of human events it becomes necessary...

        2023-10-12 11:59 Declaration Part II
        for one people to dissolve the political bands which have
        connected them with another.

        2023-11-24 17:21 Declaration Part III
        and to assume among the powers of the earth.
        """
        d = fracas.io.split(s)
        joined = fracas.io.join(d)
        self.assertTrue("2023-10-12 11:41 Declaration Part I" in joined)
        self.assertTrue("2023-10-12 11:59 Declaration Part II" in joined)
        self.assertTrue("2023-11-24 17:21 Declaration Part III" in joined)


if __name__ == "__main__":
    unittest.main()
