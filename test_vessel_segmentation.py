#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import unittest
import vessel_segmentation

class TestVesselSegmentation(unittest.TestCase):
    def test_calc_dist_001(self):
        vessel = np.zeros((100, 100, 100))
        vessel[50, 50, :] = 1
        path = vessel_segmentation.calc_dist(vessel, sx=50, sy=50, sz=0, tx=50, ty=50, tz=99)
        self.assertTrue(abs(vessel_segmentation.calc_length(path, spacing=[1,1,1]) - 99) < 1e-5)

    def test_calc_dist_002(self):
        vessel = np.zeros((100, 100, 100))
        vessel[50, 50, :] = 1
        vessel[:, 50, 50] = 1
        path = vessel_segmentation.calc_dist(vessel, sx=50, sy=50, sz=0, tx=99, ty=50, tz=50)
        self.assertTrue(abs(vessel_segmentation.calc_length(path, spacing=[1,1,1]) - 98.41421356237309) < 1e-5) # 97 + math.sqrt(2)

    def test_calc_dist_003(self):
        vessel = np.zeros((100, 100, 100))
        vessel[40:61, 40:61, :] = 1
        path = vessel_segmentation.calc_dist(vessel, sx=40, sy=40, sz=0, tx=60, ty=60, tz=99)
        self.assertTrue(abs(vessel_segmentation.calc_length(path, spacing=[1,1,1]) - 113.64101615137754) < 1e-5) # 79 + 20 * math.sqrt(3)

    def test_calc_dist_004(self):
        vessel = np.array([[
            [2, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 1],
            [1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 3],
        ]])
        path = vessel_segmentation.calc_dist(vessel, sx=0, sy=0, sz=0, tx=0, ty=5, tz=5)
        self.assertTrue(abs(vessel_segmentation.calc_length(path, spacing=[1,1,1]) - 9.414213562373096) < 1e-5) # 8 + math.sqrt(2)

    def test_calc_dist_unreachable_001(self):
        vessel = np.zeros((100, 100, 100))
        vessel[50, 50, :] = 1
        vessel[99, 99, 99] = 1
        path = vessel_segmentation.calc_dist(vessel, sx=50, sy=50, sz=0, tx=99, ty=99, tz=99)
        self.assertTrue(vessel_segmentation.calc_length(path, spacing=[1,1,1]) < 1e-5) # unreachable

    def test_calc_radius(self):
        vessel = np.ones((5, 5, 5), dtype=np.int8)
        vessel_radius = vessel_segmentation.calc_radius(vessel)
        self.assertEqual(vessel_radius[2,2,2], 3)
        self.assertEqual(vessel_radius[2,1,2], 2)
        self.assertEqual(vessel_radius[0,0,0], 1)

if __name__ == '__main__':
    unittest.main()
