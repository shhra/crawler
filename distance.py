from analysis import Analyze
import numpy as np
import pandas as pd
from utils.helpers import hex_to_rgb_array, np_to_vips, vips_to_np


class Distance(Analyze):

    def __init__(self):
        super().__init__()
        self.color = None
        self.name = None

    def same_stack(self):
        self.color = self.color.reshape(-1, 1, 3)
        cp_same = np.hstack((self.color, self.color, self.color, self.color, self.color)).astype('float64')
        return cp_same

    def vips_lab(self, array):
        colors = np_to_vips(array.reshape(-1, 1, 3).astype('float64'))
        vips_c_lab = colors.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
        return vips_c_lab

    def top_colors(self):
        df = self.select_all()
        top_rgb = hex_to_rgb_array(df['hex'])
        return top_rgb

    def get_color_distance(self, palette,  colorbase, algo):
        self.color = colorbase
        cp_same = self.same_stack()
        color_palette = np.ones_like(cp_same)
        color_palette[:, :, :] = palette

        vips_same = np_to_vips(cp_same)
        # vips_same = vips_same.resize(20, kernel="nearest")
        # vips_same.write_to_file('same.png')

        vips_cp = np_to_vips(color_palette)
        # vips_cp = vips_cp.resize(20, kernel="nearest")
        # vips_cp.write_to_file('palette.png')
        if algo == 'de76':
            color_distance = vips_cp.dE76(vips_same)
        elif algo == 'de00':
            color_distance = vips_cp.dE00(vips_same)
        elif algo == 'deCMC':
            color_distance = vips_cp.dECMC(vips_same)

        dist = vips_to_np(color_distance).reshape(-1, 5)
        value1 = np.min(dist[:, 0])
        value2 = np.min(dist[:, 1])
        value3 = np.min(dist[:, 2])
        value4 = np.min(dist[:, 3])
        value5 = np.min(dist[:, 4])

        min1 = np.where(dist[:, 0] == value1)
        min2 = np.where(dist[:, 1] == value2)
        min3 = np.where(dist[:, 2] == value3)
        min4 = np.where(dist[:, 3] == value4)
        min5 = np.where(dist[:, 4] == value5)

        cc = np.array([self.color[min1],
                       self.color[min2],
                       self.color[min3],
                       self.color[min4],
                       self.color[min5]]).reshape(-1, 3)

        new_palette = {'values': [value1, value2, value3, value4, value5],
                   'new_palette': cc}
        return new_palette

    def compare_distance_algos(self, palette, colorbase):
        self.color = colorbase
        cp_same = self.same_stack()
        color_palette = np.ones_like(cp_same)
        color_palette[:, :, :] = palette

        vips_same = np_to_vips(cp_same)

        vips_cp = np_to_vips(color_palette)
        cd1 = vips_cp.dE76(vips_same)
        cd2 = vips_cp.dE00(vips_same)
        cd3 = vips_cp.dECMC(vips_same)

        value1 = []
        value2 = []
        value3 = []

        dist = vips_to_np(cd1).reshape(-1, 5)
        dist1 = vips_to_np(cd2).reshape(-1, 5)
        dist2 = vips_to_np(cd3).reshape(-1, 5)

        for i in range(5):
            value1.append(np.min(dist[:, i]))

        for i, each in enumerate(value1):
            min = np.where(dist[:, i] == each)
            value2.append(dist1[min, i])
            value3.append(dist2[min, i])

        return value1, value2, value3

    def palette(self):
        palette = self.select_colors_from_palette()
        # Getting the colors from top 1000 palette
        color1 = hex_to_rgb_array(np.array(palette['color1'])).astype('float64')  # .reshape(-1, 1, 3)
        color2 = hex_to_rgb_array(np.array(palette['color2'])).astype('float64')  # .reshape(-1, 1, 3)
        color3 = hex_to_rgb_array(np.array(palette['color3'])).astype('float64')  # .reshape(-1, 1, 3)
        color4 = hex_to_rgb_array(np.array(palette['color4'])).astype('float64')  # .reshape(-1, 1, 3)
        color5 = hex_to_rgb_array(np.array(palette['color5'])).astype('float64')  # .reshape(-1, 1, 3)
        palette_color = np.stack((color1, color2, color3, color4, color5), axis=1)
        return palette_color

    @staticmethod
    def reduce_colors(colors, thresh=0.2):
        cols = colors.shape[0]
        color_row = np.zeros(shape=(cols, cols, 3))
        color_col = np.zeros(shape=(cols, cols, 3))
        colors = colors.reshape(-1, 1, 3)
        color_row[:, :, :] = colors
        color_col[:, :, :] = colors.reshape(1, -1, 3)

        row_vips = np_to_vips(color_row)
        col_vips = np_to_vips(color_col)

        distance = col_vips.dE00(row_vips)
        np_dist = vips_to_np(distance)
        np_dist = np_dist.reshape(cols, cols)

        np_dist[np_dist > thresh] = 0
        np_dist[np_dist == 0] = 99
        min_array = np_dist[:, :].min(axis=1)
        min_array[min_array == 99] = np.nan
        np_dist[np_dist == 99] = np.nan

        df = pd.DataFrame(np_dist)
        # df = df.replace(0, np.nan)
        df['repeats'] = df.apply(lambda x: cols - x.isnull().sum(), axis='columns')

        # df.sort_values("repeats", inplace=True, ascending=False)
        df = df.drop(columns='repeats')

        index = np.argwhere(df.notnull().values).tolist()
        index = np.asarray(index)

        return index


if __name__ == '__main__':
    distance = Distance()
    df_1000 = pd.read_csv('top_1000.csv')
    df_1000 = df_1000.drop(columns='Unnamed: 0')
    top_colors = np.asarray(df_1000)
    df_palette = pd.read_csv('top_palettes.csv')
    df_palette = df_palette.drop(columns='Unnamed: 0')
    top_palette = np.asarray(df_palette)
    zeros = np.zeros_like(top_colors)

    cols = top_palette.shape[0]
    rows = top_colors.shape[0]
    color_row = np.zeros(shape=(rows, cols, 3))
    color_col = np.zeros(shape=(rows, cols, 3))
    colors = top_colors.reshape(-1, 1, 3)
    color_row[:, :, :] = colors
    colors = top_palette.reshape(1, -1, 3)
    color_col[:, :, :] = colors

    row_vips = np_to_vips(color_row)
    # row_vips.write_to_file('rows.png')
    col_vips = np_to_vips(color_col)

    distance = col_vips.dE00(row_vips)
    np_dist = vips_to_np(distance)
    np_dist = np_dist.reshape(rows, cols)

    np_dist[np_dist > 3] = 0
    np_dist[np_dist == 0] = 99
    min_array = np_dist[:, :].min(axis=1)
    min_array[min_array == 99] = np.nan
    np_dist[np_dist == 99] = np.nan
    #
    df = pd.DataFrame(np_dist)
    df = df.replace(0, np.nan)
    df['repeats'] = df.apply(lambda x: cols - x.isnull().sum(), axis='columns')
    sum = np.sum(df['repeats'])

    # # top_colors = distance.palette()
    # reduced_colors = top_colors.copy()
    # new_colors = top_colors.copy()

    # # repeat color reduction two times
    # for j in range(1, 3):
    #     for i in range(10, 310, 10):
    #         # reduce colors
    #         new = distance.reduce_colors(reduced_colors, thresh=i/100)
    #         hash = dict(new)
    #         for key, value in hash.items():
    #             new_colors[value, :] = reduced_colors[key, :]
    #         # with open("log_palette.txt", "a") as f:
    #
    #         # find unique hits
    #         uniques, indexes = np.unique(new_colors, axis=0, return_index=True)
    #             # f.write("There are %d unique colors \n" % len(uniques))
    #         reduced_colors = new_colors.copy()
    #
    #         # find replaced colors
    #         not_unique = np.delete(reduced_colors.copy(), indexes, axis=0)
    #         reduced_top = np.delete(top_colors.copy(), indexes, axis=0)
    #         final = np.hstack((not_unique.reshape(-1, 1, 3), reduced_top.reshape(-1, 1, 3)))
    #         # saver = np_to_vips(final.astype('float64'))
    #         # saver.resize(50, kernel="nearest").write_to_file('./reduced_palette/reduced_{}_{}.png'.format(str(i/100), str(j)))


# The following code is extremely necessary for plotting the figure.
# DO NO REMOVE.

# ars_colors = select_ars()
# pantone_colors = select_pantone()
# name = "output_algos"
# if not pathlib.Path('./{}'.format(name)).exists():
#     pathlib.Path('./{}'.format(name)).mkdir()
#
# fig = plt.figure()
# ax = plt.subplot(111)
# ax.set_title('DE76 Distance')
# ax.set_xlabel("From left to right: Original Palette, Top Colors, ARS, Pantone")
#
# for i, each in enumerate(palette):
#     top = distance.get_color_distance(each, top_colors, 'de76')
#     # ars = distance.get_color_distance(each, ars_colors)
#     # pantone = distance.get_color_distance(each, pantone_colors)
#     v1, v2, v3 = distance.compare_distance_algos(each, top_colors)
#
#     # combine = np.hstack((each, top['new_palette'], ars['new_palette'], pantone['new_palette']))
#     combine = np.hstack((each, top['new_palette'], top['new_palette'], top['new_palette']))
#     vips_combine = np_to_vips(combine.reshape(5, 4, 3))
#     vips_combine = vips_combine.resize(75, kernel="nearest")
#     array = vips_to_np(vips_combine) / 255
#
#     for y in range(1, 6):
#         ax.text(75 * 1, y * 75, r'{0:.2f}'.format(float(v1[y-1])), fontsize=10)
#         ax.text(75 * 2, y * 75, r'{0:.2f}'.format(float(v2[y-1])), fontsize=10)
#         ax.text(75 * 3, y * 75, r'{0:.2f}'.format(float(v3[y-1])), fontsize=10)
#
#     ax.imshow(array)
#     plt.savefig("./{}/{}.png".format(name, str(i+1)))
#     plt.cla()
#     print("Saving figure {}".format(i))
#     # if i == 0:
#     #     break

