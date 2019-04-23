# import pathlib
#
# path = pathlib.Path('./colors/indistinguishable')
# path2 = pathlib.Path('./colors/')
#
# files = [file.name.split('/')[-1] for file in path.iterdir() if file.name.endswith('.png')]
# color_file = [file for file in path2.iterdir() if file.name.endswith('.png')]
# for each in color_file:
#     if each.name.split('/')[-1] in files:
#         print(each)
#         each.unlink()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyvips
from mpl_toolkits.mplot3d import axes3d
import sqlalchemy as db


def select_templates():
    engine = db.create_engine('mysql+mysqlconnector://'+'color:color'+'@'+'localhost'+'/colorbase')
    sql = """SELECT templateNumber, imageUrl FROM patterns WHERE id between 1 and 100"""
    df = pd.read_sql(sql, engine)
    return df


def remap(url):
    return url.split('/')[-2]


def main():
    df = select_templates()
    df['templateNumber'] = map(remap, df['imageUrl'])
    print("There are %d unique templates." % len(df))


if __name__ == '__main__':
    main()




