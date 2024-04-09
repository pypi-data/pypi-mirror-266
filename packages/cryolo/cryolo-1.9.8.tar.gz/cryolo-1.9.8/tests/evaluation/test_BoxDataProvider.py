import unittest
from cryolo.evaluation.boxdataprovider import BoxDataProvider


class MyTestCase(unittest.TestCase):
    def test_group_method_lastfolder(self):
        group = BoxDataProvider.group_method_lastfolder(
            "/this/is/an/example/group/file.txt"
        )
        self.assertEqual("group", group)


if __name__ == "__main__":
    unittest.main()
