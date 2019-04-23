import pyvips
import numpy as np
import pathlib
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from PIL import Image
from utils import helpers


if __name__ == '__main__':
    path_same = pathlib.Path('./colors/indistinguishable')
    path_diff = pathlib.Path('./colors/distinguishable')

    same = [file for file in path_same.iterdir()]
    diff = [file for file in path_diff.iterdir()]

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.set_xlabel('H')
    ax.set_ylabel('S')
    ax.set_zlabel('V')
    # ax = plt.subplot(111)

    colors = [same, diff]

    list_color = [[], []]
    for i, color in enumerate(colors):
        for each in color:
            img = np.asarray(Image.open(each.absolute()).convert('RGB'))
            color_1 = img[240, 210]
            list_color[i].append(color_1.tolist())
            color_2 = img[240, 430]
            list_color[i].append(color_2.tolist())

    # LAB
    same_colors = np.array(list_color[0])
    same_lab = helpers.np_to_vips(same_colors.copy().reshape(-1, 1, 3).astype('float64'))
    same_lab = same_lab.copy().sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
    np_same_lab = helpers.vips_to_np(same_lab).reshape(-1, 3)

    diff_colors = np.array(list_color[1])
    diff_lab = helpers.np_to_vips(diff_colors.copy().reshape(-1, 1, 3).astype('float64'))
    diff_lab = diff_lab.copy().sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
    np_diff_lab = helpers.vips_to_np(diff_lab).reshape(-1, 3)

    # HSV
    same_hsv = helpers.np_to_vips(same_colors.copy().reshape(-1, 1, 3).astype('float64'))
    same_hsv = same_hsv.copy().sRGB2HSV()
    np_same_hsv = helpers.vips_to_np(same_hsv).reshape(-1, 3)

    diff_hsv = helpers.np_to_vips(diff_colors.copy().reshape(-1, 1, 3).astype('float64'))
    diff_hsv = diff_hsv.copy().sRGB2HSV()
    np_diff_hsv = helpers.vips_to_np(diff_hsv).reshape(-1, 3)

    # ax.scatter3D(same_colors[:, 0], same_colors[:, 1], same_colors[:, 2], color=same_colors/255)
    # ax.scatter3D(diff_colors[:, 0], diff_colors[:, 1], diff_colors[:, 2], color=diff_colors/255)
    # plt.show()

    # ax.scatter3D(np_same_lab[:, 1], np_same_lab[:, 2], np_same_lab[:, 0], color=same_colors/255, linewidths=1, edgecolor='b', s=75)
    # ax.scatter3D(np_diff_lab[:, 1], np_diff_lab[:, 2], np_diff_lab[:, 0], color=diff_colors/255, linewidths=1, edgecolor='r', s=75)

    ax.scatter3D(np_same_lab[:, 0], np_same_hsv[:, 1], np_same_hsv[:, 2], color='b', linewidths=1, edgecolor='b', s=75)
    ax.scatter3D(np_diff_lab[:, 0], np_diff_hsv[:, 1], np_diff_hsv[:, 2], color='r', linewidths=1, edgecolor='r', s=75)
    plt.show()


    print("HHHH")



