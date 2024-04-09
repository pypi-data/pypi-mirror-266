import unittest
import os
from cryolo.evaluation.pathsboxdataprovider import PathsDataProvider
from cryolo.evaluation.pathsfilamentprovider import PathsFilamentProvider
from cryolo.evaluation.boxdataprovider import BoxDataProvider
import cryolo.CoordsIO as io
import glob


class MyTestCase(unittest.TestCase):
    def test_path_filament_provider_resampling(self):
        path_gt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/01_gt_filament/*.cbox",
            )
        )
        files = glob.glob(path_gt)
        fdp5 = PathsFilamentProvider(
            paths=files,
            reading_method=io.read_cbox_boxfile,
            resampling_distance=1,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        fdp10 = PathsFilamentProvider(
            paths=files,
            reading_method=io.read_cbox_boxfile,
            resampling_distance=2,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        res5 = fdp5.get_boxes()
        res10 = fdp10.get_boxes()
        self.assertAlmostEquals(2, len(res5[0].data) / len(res10[0].data), delta=0.1)

    def test_path_filament_provider(self):
        path_gt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/01_gt_filament/*.cbox",
            )
        )
        files = glob.glob(path_gt)
        fdp = PathsFilamentProvider(
            paths=files,
            reading_method=io.read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        res = fdp.get_boxes()
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0].data), 684 - 21 + 1)  # LAST_LINE - FIRST_LINE  + 1

    def test_get_correct_number(self):

        path_gt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/00_gt/*.cbox",
            )
        )
        files = glob.glob(path_gt)
        fdp = PathsDataProvider(
            paths=files,
            reading_method=io.read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        res = fdp.get_boxes()

        self.assertEqual(len(res), 1)
        self.assertEqual(len(res[0].data), 3)


if __name__ == "__main__":
    unittest.main()
