from Camera import *
import xml.etree.ElementTree as ET
import os
import numpy as np
import cv2
import pandas as pd
import json

class Camera():
    def __int__(self):
        pass

    @staticmethod
    def string_to_float(string, delimiter=' ', suppress_warning=False):
        output = []
        for x in string.split(delimiter):
            try:
                output.append(float(x))
            except ValueError:
                if not suppress_warning:
                    print(f'Warning: \'{x}\' in string \'{string} \'is not a float.')
        if len(output) == 1:
            return output[0]
        else:
            return np.array(output)

    @staticmethod
    def rot3x3_from_quaternion(quaternion):
        # quaternion = [w, x, y, z]
        x, y, z, w = quaternion
        rot_matrix = np.array([[1 - 2 * y ** 2 - 2 * z ** 2, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w],
                               [2 * x * y + 2 * z * w, 1 - 2 * x ** 2 - 2 * z ** 2, 2 * y * z - 2 * x * w],
                               [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x ** 2 - 2 * y ** 2]])
        return rot_matrix


    @staticmethod
    def rot3x4_from_rot3x3_and_position(rot3x3, position):
        rot3x4 = np.hstack([rot3x3, -rot3x3.dot(position.reshape(-1, 1))])
        return rot3x4

    def get_camera_intrinsic_matrix(self):
        K = np.array([[self.FOCAL_LENGTH, self.SKEW, self.PRINCIPAL_POINT[0]],
                      [0, self.FOCAL_LENGTH / self.PIXEL_ASPECT_RATIO, self.PRINCIPAL_POINT[1]],
                      [0, 0, 1]])
        return K

    @staticmethod
    def projection_matrix_from_intrinsic_matrix_and_rot3x4(K, rot3x4):
        P = K.dot(rot3x4)
        return P

    def undistort(self, points_2d):
        raise NotImplementedError

    def distort(self, points_2d):
        raise NotImplementedError

    def get_projection_matrix(self):
        self.rot3x3 = self.rot3x3_from_quaternion(self.ORIENTATION)
        self.rot3x4 = self.rot3x4_from_rot3x3_and_position(self.rot3x3, self.POSITION)
        self.intrinsic_matrix = self.get_camera_intrinsic_matrix()
        self.projection_matrix = self.projection_matrix_from_intrinsic_matrix_and_rot3x4(self.intrinsic_matrix, self.rot3x4)
        return self.projection_matrix

    def project(self, points_3d):
        ''' extrinsic and intrinsic projection
        :param points_3d: 3d points in world coordinate
        :return: 2d points in camera coordinate, in pixel
        '''
        self.get_projection_matrix()
        points_3d = np.array(points_3d)
        points_2d = self.projection_matrix.dot(np.vstack([points_3d.T, np.ones([1, points_3d.shape[0]])]))
        points_2d = points_2d[0:2, :] / points_2d[2, :]
        points_2d = points_2d.T
        return points_2d

    def project_w_depth(self, points_3d):
        ''' world to camera coordinate system, extrinsic projection
        :param points_3d: 3d points in world coordinate
        :return: 3d points in camera coordinate, with depth, in mm/m
        '''
        self.get_projection_matrix()
        points_3d = np.array(points_3d)
        points_3d_cam = self.rot3x4.dot(np.vstack([points_3d.T, np.ones([1, points_3d.shape[0]])]))
        # translation_vector = self.POSITION.reshape([3, 1])
        # rotM = self.rot3x3
        # points_3d_cam = (rotM.dot(points_3d.T) + translation_vector).T
        return points_3d_cam.T

    def _weak_project(self, pose3d):
        """ From LCN, intrinsic projection
        """
        fx, fy = self.FOCAL_LENGTH, self.FOCAL_LENGTH / self.PIXEL_ASPECT_RATIO
        cx, cy = self.PRINCIPAL_POINT
        pose2d = pose3d[:, :2] / pose3d[:, 2:3]
        pose2d[:, 0] *= fx
        pose2d[:, 1] *= fy
        pose2d[:, 0] += cx
        pose2d[:, 1] += cy
        return pose2d

    def draw_2d(self, image, points_2d, color=(0, 0, 255)):
        for point_idx, point_2d in enumerate(points_2d):
            cv2.circle(image, (int(point_2d[0]), int(point_2d[1])), 3, color, -1)
            cv2.putText(image, str(point_idx), (int(point_2d[0]), int(point_2d[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return image
