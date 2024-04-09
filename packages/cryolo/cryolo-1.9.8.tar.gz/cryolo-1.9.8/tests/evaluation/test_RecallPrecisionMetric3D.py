import unittest
from cryolo.evaluation.recallprecisionmetric3d import RecallPrecisionMetric3D
import numpy as np
import copy


class MyTestCase(unittest.TestCase):
    def test_precision_available(self):

        predicted = np.random.random(size=(10, 6))

        gt = np.random.random(size=(10, 6))
        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertTrue("precision" in results)

    def test_recall_available(self):

        predicted = np.random.random(size=(10, 6))

        gt = np.random.random(size=(10, 6))
        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertTrue("recall" in results)

    def test_recall_1(self):

        predicted = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        gt = copy.deepcopy(predicted)

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(1.0, results["recall"])

    def test_recall_pred_none(self):

        predicted = None

        gt = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(0.0, results["recall"])
        self.assertEqual(0.0, results["precision"])

    def test_recall_gt_none(self):
        predicted = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        gt = None

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(0.0, results["recall"])
        self.assertEqual(0.0, results["precision"])

    def test_precision_1(self):

        predicted = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        gt = copy.deepcopy(predicted)

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(1.0, results["precision"])

    def test_recall_2_expected_1(self):

        predicted = np.array(
            [
                [100, 10, 10, 9, 9, 9],
                [300, 30, 30, 9, 9, 9],
                [500, 50, 50, 9, 9, 9],
                [10, 10, 10, 9, 9, 9],
                [30, 30, 30, 9, 9, 9],
                [50, 50, 50, 9, 9, 9],
            ]
        )

        gt = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(1.0, results["recall"])

    def test_recall_3_expected_2over3(self):
        predicted = np.array([[30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]])

        gt = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(2 / 3, results["recall"])

    def test_precision_expected_05(self):

        predicted = np.array(
            [
                [100, 10, 10, 9, 9, 9],
                [300, 30, 30, 9, 9, 9],
                [500, 50, 50, 9, 9, 9],
                [10, 10, 10, 9, 9, 9],
                [30, 30, 30, 9, 9, 9],
                [50, 50, 50, 9, 9, 9],
            ]
        )

        gt = np.array(
            [[10, 10, 10, 9, 9, 9], [30, 30, 30, 9, 9, 9], [50, 50, 50, 9, 9, 9]]
        )

        eval = RecallPrecisionMetric3D()
        results = eval.eval(predicted, gt)

        self.assertEqual(0.5, results["precision"])
