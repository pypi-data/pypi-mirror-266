import unittest
from cryolo.evaluation.tomoevaluation import evaluate, create_parser, EvaluationResult, group_evaluation_results, run
from cryolo.evaluation.pathsboxdataprovider import PathsDataProvider
from cryolo.evaluation.pathsfilamentprovider import PathsFilamentProvider
from cryolo.evaluation.recallprecisionmetric3d import RecallPrecisionMetric3D
from cryolo.evaluation.boxdataprovider import BoxDataProvider
from cryolo.evaluation.resultsview import SimpleView
from cryolo.CoordsIO import read_cbox_boxfile
import os
import glob


class MyTestCase(unittest.TestCase):

    def test_run(self):
        path_gt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/01_gt_filament/",
            )
        )

        path_measured = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/01_gt_filament/",
            )
        )
        parser = create_parser()
        args = parser.parse_args(
            ["-gtb", path_gt, "-pb", path_measured, "--filament"]
        )

        results = run(args=args, metrics=[RecallPrecisionMetric3D()], view=SimpleView())

        recall = [m.value for m in results if m.metric == "recall"][0]
        precision = [m.value for m in results if m.metric == "precision"][0]

        self.assertNotEqual(None,results)
        self.assertEqual(recall, 1.0)
        self.assertEqual(precision, 1.0)



    def test_group_evaluation_result(self):
        results = [
            EvaluationResult(
                metric="recall",
                value=0.5,
                number_datapoints=1,
                dataset="A"
            ),
            EvaluationResult(
                metric="recall",
                value=1,
                number_datapoints=1,
                dataset="A"
            ),
            EvaluationResult(
                metric="recall",
                value=1,
                number_datapoints=1,
                dataset="B"
            ),
            EvaluationResult(
                metric="recall",
                value=1,
                number_datapoints=1,
                dataset="B"
            ),
        ]

        results_grouped = group_evaluation_results(results)
        results_recall = [e.value for e in results_grouped]
        results_recall.sort()

        self.assertEqual(len(results_grouped),2)
        self.assertEqual(results_recall[0], 0.75)
        self.assertEqual(results_recall[1], 1)
        self.assertEqual(results_grouped[0].number_datapoints, 2)


    def test_evaluation_filament(self):
        path_gt = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../resources/test_FolderDataProvider/01_gt_filament/*.cbox",
            )
        )

        gtfiles = glob.glob(path_gt)
        mfiles = glob.glob(path_gt)

        # As measured and gt point to the same files, recall and precision should be 1
        gtProvider = PathsFilamentProvider(
            paths=gtfiles,
            reading_method=read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        mProvider = PathsFilamentProvider(
            paths=mfiles,
            reading_method=read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )

        # Setup metrics
        metrics = []
        metrics.append(RecallPrecisionMetric3D())

        # Evaluate all metric on the box pairs
        result = evaluate(gtProvider, mProvider, metrics)
        recall = [m.value for m in result if m.metric == "recall"][0]
        precision = [m.value for m in result if m.metric == "precision"][0]

        self.assertEqual(recall, 1.0)
        self.assertEqual(precision, 1.0)

    def test_evaluation_particles(self):
        path_gt = os.path.join(
            os.path.dirname(__file__),
            "../../resources/test_FolderDataProvider/00_gt/*.cbox",
        )
        """
        path_measured = os.path.join(os.path.dirname(__file__),
                                     "../../resources/test_FolderDataProvider/00_measured/*.cbox")
        """
        gtfiles = glob.glob(path_gt)
        mfiles = glob.glob(path_gt)

        # As measured and gt point to the same files, recall and precision should be 1
        gtProvider = PathsDataProvider(
            paths=gtfiles,
            reading_method=read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )
        mProvider = PathsDataProvider(
            paths=mfiles,
            reading_method=read_cbox_boxfile,
            group_method=BoxDataProvider.group_method_lastfolder,
        )

        # Setup metrics
        metrics = []
        metrics.append(RecallPrecisionMetric3D())

        # Evaluate all metric on the box pairs
        result = evaluate(gtProvider, mProvider, metrics)
        recall = [m.value for m in result if m.metric == "recall"][0]
        precision = [m.value for m in result if m.metric == "precision"][0]
        self.assertEqual(recall, 1.0)
        self.assertEqual(precision, 1.0)

    def test_parser(self):
        parser = create_parser()

        gt_path = "bla/blub/"
        predicted_path = "bla/blub2/"

        args = parser.parse_args(
            ["-gtb", gt_path, "-pb", predicted_path, "--filament", "-bd", "10"]
        )

        self.assertEqual(args.groundtruth, gt_path)
        self.assertEqual(args.predicted, predicted_path)
        self.assertEqual(args.boxdistance, 10)
        self.assertEqual(args.filament, True)


if __name__ == "__main__":
    unittest.main()
