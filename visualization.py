import pandas as pd
import numpy as np
import sqlalchemy as db
import matplotlib.pyplot as plt
import time
from sklearn.cluster import KMeans
from utils.helpers import *
import pickle


class Visualize:

    def __init__(self):
        self.engine = db.create_engine('mysql+mysqlconnector://'+'color:color'+'@'+'localhost'+'/colorbase', encoding='UTF-8', max_overflow=30)

    def select_templates(self, range):
        sql = """SELECT numViews, numVotes FROM patterns WHERE id BETWEEN {} and {}""".format(range[0], range[1])
        df = pd.read_sql(sql, self.engine)
        return df

    def select_two_colors(self):
        sql = """SELECT * FROM patterns WHERE numColors = 2"""
        df = pd.read_sql(sql, self.engine)
        return df

    def select_top_2500(self, table):
        sql = """SELECT * FROM {} WHERE {} between 1 and 2500""".format(table, table[:-1]+'Rank')
        df = pd.read_sql(sql, self.engine)
        return df

    def get_last_id(self, table):
        sql = """SELECT id FROM {} ORDER BY ID DESC LIMIT 1""".format(table)
        df = pd.read_sql(sql, self.engine)
        return df

    @staticmethod
    def template_url(id):
        url = 'http://www.colourlovers.com/patternPreview/{}/CCCCCC/999999/666666/333333/000000.png'.format(str(id))
        return url, 3


class Extract:
    def __init__(self):
        self.csv_root = './csv/'
        self.pvv = pd.read_csv(self.csv_root+'pattern_VV.csv', index_col=0)  # pvv = views and votes in patterns
        self.two_color = pd.read_csv(self.csv_root+'two_colors.csv', index_col=0)
        self.df_2500 = pd.read_csv(self.csv_root+'./top_colors_2500.csv', index_col=0)
        self.rgb_2500 = hex_to_rgb_array(np.unique(self.df_2500['hex'].values))
        self.clustered = pd.read_csv(self.csv_root+'reduced_lab_colors.csv', index_col=0)
        self.fig = plt.figure()
        self.ax = plt.axes()

    def plot_color(self, x_data, y_data, label, color='c'):
        # ax.scatter(condition['numViews'], condition['numVotes'], c='c')
        self.ax.scatter(x_data, y_data, c=color)
        self.ax.set_xlabel(label['x'])
        self.ax.set_ylabel(label['y'])

    def plot_all_patterns(self):
        pvv = self.pvv
        condition = pvv[(pvv['numViews'] < 10000) & (pvv['numViews'] > 100) & (pvv['numVotes'] > 5) & (pvv['numVotes'] < 10000)]
        ratio = condition['numViews']/condition['numVotes']
        mean = np.mean(ratio)
        sigma = np.std(ratio)
        ratio = (ratio - mean) / sigma
        print(" There are {} data".format(len(pvv)))
        # print("After first condition data was reduced to {}".format(len(condition)))
        print("The standard deviation of view to vote ratio is:{}".format(sigma))
        print("While the mean of view to vote ratio is: {}".format(mean))

    def plot_two_patterns(self):
        pvv = self.two_color
        print("There are {} patterns with two colors".format(len(pvv)))
        # pvv = pvv[(pvv['numViews'] < 5000) & (pvv['numViews'] > 100) & (pvv['numVotes'] > 0) & (pvv['numVotes'] < 50)]
        pvv = pvv[(pvv['numVotes'] > 0)]
        print("After applying the condition, data was reduced to {}".format(len(pvv)))
        ratio = pvv['numViews'] / pvv['numVotes']
        mean = np.mean(ratio)
        std = np.std(ratio)
        print(" The mean is %0.2f and sigma is %0.2f" % (mean, std))

        ranked = pvv[['color1', 'color2', 'patternRank']]
        uniques = np.unique(ranked[['color1', 'color2']].values)
        print("Out of %d colors, there are %d unique colors" % (len(pvv) * 2, len(uniques)))

    def map_minimum(self, value):
        colors = self.rgb_2500.reshape(1, -1, 3)
        color = np.zeros_like(colors)
        color[:, :, :] = value

        vips_colors = np_to_vips(colors.astype('float'))
        vips_color = np_to_vips(color.astype('float'))
        dist = vips_color.dE00(vips_colors)
        del vips_colors
        del vips_color
        np_dist = vips_to_np(dist).reshape(-1, 1)
        del dist
        min = np.where(np_dist == np_dist.min())
        value = self.rgb_2500[min[0], :]
        return value[0][:]

    def reduce_colors(self, nc):
        pvv = self.two_color
        pvv = pvv[pvv['numVotes'] > 0]
        uniques = np.unique(pvv[['color1', 'color2']].values)
        unique_array = hex_to_rgb_array(pd.DataFrame(uniques, columns=['color'])['color'])
        vips_unique = np_to_vips(unique_array.reshape(-1, 1, 3).astype('float64'))
        vips_lab = vips_unique.sRGB2scRGB().scRGB2XYZ().XYZ2Lab()
        np_lab = vips_to_np(vips_lab)
        clt = KMeans(n_clusters=nc)
        labels = clt.fit_predict(np_lab.reshape(-1, 3))
        pickle.dump(clt, open("kmeans.sav", "wb"))
        return np.concatenate((np_lab.reshape(-1, 3), labels.reshape(-1, 1)), axis=1)

    @staticmethod
    def lab_to_rgb(array):
        vips_lab = np_to_vips(array.reshape(-1, 1, 3))
        vips_rgb = vips_lab.Lab2XYZ().XYZ2scRGB().scRGB2sRGB()
        rgb = vips_to_np(vips_rgb).reshape(-1, 3)
        return rgb

    def get_centroids(self, labels):
        model = pickle.load(open("kmeans.sav", "rb"))
        centroids = model.cluster_centers_[labels]
        rgb = self.lab_to_rgb(centroids)
        return rgb

    def evaluation(self, cluster_number):
        clustered = self.clustered
        lab_cluster1 = clustered[clustered['3'] == cluster_number]
        lab_cluster_array = np.asarray(lab_cluster1[['0', '1', '2']])
        l = lab_cluster_array[:, 0]
        a = lab_cluster_array[:, 1]
        b = lab_cluster_array[:, 2]
        labels = {'x': '*b',
                  'y': '*a'}
        rgb = self.lab_to_rgb(lab_cluster_array)
        return rgb

    @staticmethod
    def db_to_csv():
        start = time.time()
        data = Visualize()
        df = None
        # last = data.get_last_id("patterns")
        cur = data.select_top_2500('colors')
        df = pd.concat((df, cur))
        # print("It took {} secs to fetch {} data.".format(time.time()-start, last['id'][0]))
        df.to_csv('./csv/top_colors_2500.csv')


if __name__ == '__main__':
    extract = Extract()
    extract.plot_two_patterns()
    # for i in range(1, 12):
    #     extract.evaluation(i)
    # extract.fig.savefig("./outputs/colorcluster.png")
    import os
    output_path = './outputs/cluster/'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    for i in range(2500):
        out = extract.evaluation(i).reshape(-1, 1, 3)
        centroid = extract.get_centroids(i)[0]
        img = np.zeros_like(out)
        img[:, :, :] = centroid
        out = np.concatenate((out, img), axis=1)
        image = np_to_vips(out)
        image = image.resize(50, kernel='nearest')
        image.write_to_file(output_path+'{}.png'.format(i))
        if i == 0:
            break


    # out = extract.reduce_colors(2500)
    # df = pd.DataFrame(out)
    # print("saving labels and colors")
    # df.to_csv("./csv/reduced_lab_colors.csv")







