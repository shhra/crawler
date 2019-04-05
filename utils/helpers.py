import numpy as np
import pandas as pd
import pyvips


def np_to_vips(array):
    # map np dtypes to vips
    dtype_to_format = {
        'uint8': 'uchar',
        'int8': 'char',
        'uint16': 'ushort',
        'int16': 'short',
        'uint32': 'uint',
        'int32': 'int',
        'int64': 'int',
        'float32': 'float',
        'float64': 'double',
        'complex64': 'complex',
        'complex128': 'dpcomplex',
    }
    # make a vips image from the numpy array
    height, width, bands = array.shape
    linear = array.reshape(width * height * bands)
    vi = pyvips.Image.new_from_memory(linear.data, width, height, bands,
                                      dtype_to_format[str(array.dtype)])
    return vi


def vips_to_np(img):
    mem_img = img.write_to_memory()
    # map vips formats to np dtypes
    format_to_dtype = {
        'uchar': np.uint8,
        'char': np.int8,
        'ushort': np.uint16,
        'short': np.int16,
        'uint': np.uint32,
        'int': np.int32,
        'float': np.float32,
        'double': np.float64,
        'complex': np.complex64,
        'dpcomplex': np.complex128,
    }

    array = np.ndarray(buffer=mem_img,
                       dtype=format_to_dtype[img.format],
                       shape=[img.height, img.width, img.bands])
    return array


def getRGBfromI(RGBint):
    red = RGBint & 255
    green = (RGBint >> 8) & 255
    blue = (RGBint >> 16) & 255
    return red, green, blue


def _hex_to_rgb(h):
    if h == 'NULL':
        h = '000000'
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgb_array(array):
    rgb_color = np.array(list(map(_hex_to_rgb, array)))
    return rgb_color


def select_pantone():
    pantone_df = pd.read_csv("./data/pantone.txt", sep='\t', names=['name', 'color'])
    pantone_df = pantone_df.drop(axis=0, index=0)
    pantone_color = np.array(pantone_df['color'])
    pantone_rgb = np.array(list(map(getRGBfromI, pantone_color.astype('int'))))

    return pantone_rgb


def select_ars():
    ars_df = pd.read_csv("./data/ARS 1400.txt", sep='\t', names=['name', 'R', 'G', 'B'])
    ars_df = ars_df.drop(labels=['name'], axis=1)
    ars_rgb = np.array(ars_df)
    return ars_rgb


# def visualize():
# # 3d plotting
#     fig = plt.figure()
#     ax = fig.gca(projection='3d')
#     ax.scatter(hsv[:, 0], hsv[:, 1], hsv[:, 2], c=rgb_color/255)
#     plt.xlabel('hue')
#     plt.ylabel('saturation')
#
#     fig2 = plt.figure()
#     ax2 = fig2.gca(projection='3d')
#     ax2.scatter(lab[:, 0], lab[:, 1], lab[:, 2], c=rgb_color/255)
#     plt.xlabel('L')
#     plt.ylabel('A')
#
#
#     fig3 = plt.figure()
#
#     ax3 = fig3.gca(projection='3d')
#     ax3.get_proj = lambda: np.dot(axes3d.Axes3D.get_proj(ax3), np.diag([1.5, 1.5, 1.5, 1]))
#     #
#     colors = analysis.np_to_vips(rgb_color.reshape(-1, 1, 3).astype('float64'))
#     vips_c_lab = colors.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
#     lab = analysis.vips_to_np(vips_c_lab).reshape(-1, 3)
#     ax3.scatter(rgb_color[:, 0], rgb_color[:, 1], rgb_color[:, 2], c=rgb_color/255, s=100)
#     ax3.scatter(cc[:, 0], cc[:, 1], cc[:, 2], c=cc/255, edgecolor='k', linewidths=4, s=200)
#     ax3.scatter(p1[:, 0], p1[:, 1], p1[:, 2], c=p1/255, edgecolor='b', linewidths=4, s=200)
#     plt.xlabel('R')
#     plt.ylabel('G')
