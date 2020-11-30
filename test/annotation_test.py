from typing import Tuple

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
        db_path = self.tmpdir + "/testA.db"

        @SimDataDB2(db_path, "results1")
        def fake_sim(x: float, y: float) -> Tuple[float]:
            return x + 2.0 * y,

        fake_sim(1.0, 1.5)
        fake_sim(1.0, 1.5)
        fake_sim(1.0, 2.5)

        sdb = SimDataDB2(db_path, "results1")
        results = sdb.GrabAll()
        print(results)
        self.assertTrue(True)

    def test_new_dir(self):
        db_path = self.tmpdir + "/non/existent/path/testA.db"

        @SimDataDB2(db_path, "results1")
        def fake_sim(x: float, y: float) -> Tuple[float]:
            return x + 2.0 * y,

        fake_sim(1.0, 1.5)
        fake_sim(1.0, 1.5)
        fake_sim(1.0, 2.5)

        sdb = SimDataDB2(db_path, "results1")
        results = sdb.GrabAll()
        print(results)
        self.assertTrue(True)


if __name__ == "__main__":
    ut.main()
