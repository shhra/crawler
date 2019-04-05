#%% Handling Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyvips
from mpl_toolkits.mplot3d import axes3d
import sqlalchemy as db
import os
from utils.helpers import np_to_vips, vips_to_np, getRGBfromI, hex_to_rgb_array


class Analyze:

    def __init__(self):

        self.engine = db.create_engine('mysql+mysqlconnector://'+'color:color'+'@'+'localhost'+'/colorbase')

    def select_all(self):
        sql = """SELECT hex FROM colors"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_colors_from_palette(self):
        sql = """SELECT color1, color2, color3, color4, color5 FROM palettes"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_colors_from_pattern(self):
        sql = """SELECT color1, color2, color3, color4, color5 FROM patterns"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_average(self):
        sql = """SELECT hex, numViews, numVotes FROM colors WHERE numViews between 3000 and 15000
         and numVotes between 75 and 250"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_top(self):
        sql = """SELECT hex, numViews, numVotes FROM colors WHERE numViews > 14999 and numVotes > 249"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_bot(self):
        sql = """SELECT hex, numViews, numVotes FROM colors WHERE numViews < 3001 and numVotes < 76"""
        df = pd.read_sql(sql, self.engine)
        return df


if __name__ == '__main__':

    analysis = Analyze()
    df = analysis.select_all()

    top_rgb = hex_to_rgb_array(df['hex'])

    rgb_color = top_rgb
    name = 'top_rgb'
    cp_same = np.stack((rgb_color, rgb_color, rgb_color, rgb_color, rgb_color), axis=1).astype('float64')

    colors = np_to_vips(rgb_color.reshape(-1, 1, 3).astype('float64'))
    hsv_vips = colors.sRGB2HSV()
    hsv = vips_to_np(hsv_vips)
    hsv = hsv.reshape(-1, 3)

    colors = np_to_vips(rgb_color.reshape(-1, 1, 3).astype('float64'))
    vips_c_lab = colors.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
    lab = vips_to_np(vips_c_lab).reshape(-1, 3)

    #%%
    palette = analysis.select_colors_from_pattern()

    for index in range(1000):
        color1 = hex_to_rgb_array(np.array(palette['color1'])).astype('float64')  # .reshape(-1, 1, 3)
        color2 = hex_to_rgb_array(np.array(palette['color2'])).astype('float64')  # .reshape(-1, 1, 3)
        color3 = hex_to_rgb_array(np.array(palette['color3'])).astype('float64')  # .reshape(-1, 1, 3)
        color4 = hex_to_rgb_array(np.array(palette['color4'])).astype('float64')  # .reshape(-1, 1, 3)
        color5 = hex_to_rgb_array(np.array(palette['color5'])).astype('float64')  # .reshape(-1, 1, 3)
        palette_color = np.stack((color1, color2, color3, color4, color5), axis=1)

        color_palette = np.ones_like(cp_same)
        color_palette[:, :, :] = palette_color[index]

        vips_same = np_to_vips(cp_same)
        vips_same_lab = colors.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()

        vips_cp = np_to_vips(color_palette)
        vips_cp_lab = colors.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()

        distance = vips_cp.dE76(vips_same)

        dist = vips_to_np(distance).reshape(-1, 5)
        value1 = np.min(dist[:, 0])
        value2 = np.min(dist[:, 1])
        value3 = np.min(dist[:, 2])
        value4 = np.min(dist[:, 3])
        value5 = np.min(dist[:, 4])

        sum = value1 + value2 + value3 + value4 + value5

        min1 = np.where(dist[:, 0] == value1)
        min2 = np.where(dist[:, 1] == value2)
        min3 = np.where(dist[:, 2] == value3)
        min4 = np.where(dist[:, 3] == value4)
        min5 = np.where(dist[:, 4] == value5)

        with open(name+"_palette.csv", "a") as f:
            color = (df['hex'][min1[0][0]]
                     + ',' + df['hex'][min2[0][0]]
                     + ',' + df['hex'][min3[0][0]]
                     + ',' + df['hex'][min4[0][0]]
                     + ',' + df['hex'][min5[0][0]] + '\n')
            f.write(color)

        cc = np.array([rgb_color[min1],
                      rgb_color[min2],
                      rgb_color[min3],
                      rgb_color[min4],
                      rgb_color[min5]]).reshape(-1, 3)

        p1 = color_palette[index].reshape(-1, 3)

        combine = np.hstack((p1, cc))
        # vips_combine = np_to_vips(combine.reshape(5, 2, 3))
        # vips_combine = vips_combine.resize(75, kernel="nearest")

        # if not os.path.exists('./output_{}'.format(name)):
        #     os.mkdir('./output_{}'.format(name))
        # vips_combine.write_to_file("./output_{}/".format(name) + str(index) + ".png")
