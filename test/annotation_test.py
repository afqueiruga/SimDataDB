from typing import Tuple

import os
import unittest as ut
import tempfile, shutil

from SimDataDB import *


class annotation_test(ut.TestCase):
    """Test infering from python3 type annotations."""
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test(self):
        db_path = os.path.join(self.tmpdir, "testA.db")

        @SimDataDB2(db_path, "results1")
        def fake_sim(x: float, y: float) -> Tuple[float]:
            return x + 2.0 * y,

        self.assertAlmostEqual(fake_sim(1.0, 1.5)[0], 4.0)
        # This one should be memoized:
        self.assertAlmostEqual(fake_sim(1.0, 1.5)[0], 4.0)
        self.assertAlmostEqual(fake_sim(1.0, 2.5)[0], 6.0)

        sdb = SimDataDB2(db_path, "results1")
        results = sdb.GrabAll()
        print(results)
        self.assertEqual(len(results), 2)

    def test_new_dir(self):
        db_path = os.path.join(self.tmpdir, "non/existent/path/testA.db")

        @SimDataDB2(db_path, "results1")
        def fake_sim(x: float, y: float) -> Tuple[float]:
            return x + 2.0 * y,

        self.assertAlmostEqual(fake_sim(1.0, 1.5)[0], 4.0)
        # This one should be memoized:
        self.assertAlmostEqual(fake_sim(1.0, 1.5)[0], 4.0)
        self.assertAlmostEqual(fake_sim(1.0, 2.5)[0], 6.0)

        sdb = SimDataDB2(db_path, "results1")
        results = sdb.GrabAll()
        print(results)
        self.assertEqual(len(results), 2)

    def test_more_types(self):
        db_path = os.path.join(self.tmpdir, "testA.db")

        @SimDataDB2(db_path, "results1")
        def fake_sim(x: int, y: str) -> Tuple[int, str]:
            return x + 1, y + "foo"

        a, b = fake_sim(1, "foo")
        self.assertEqual(a, 2)
        self.assertEqual(b, "foofoo")
        # This one should be memoized:
        a, b = fake_sim(1, "foo")
        self.assertEqual(a, 2)
        self.assertEqual(b, "foofoo")
        a, b = fake_sim(2, "yap")
        self.assertEqual(a, 3)
        self.assertEqual(b, "yapfoo")
        
        sdb = SimDataDB2(db_path, "results1")
        results = sdb.GrabAll()
        print(results)
        # Only two unique runs:
        self.assertEqual(len(results), 2)

if __name__ == "__main__":
    ut.main()
