import pandas as pd
from colordb import ColorDB
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import logging
from multiprocessing import Pool
from sys import exit


class XMLParser:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.init_logger()
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
                (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        self.db = ColorDB()
        self.db.create_tables()
        self.db.change_to_utf()

    def init_logger(self):
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(filename='error.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_item(self, item, idx):
        one_item = self.df['{}'.format(item)][idx]
        try:
            tree = ET.parse(one_item)
        except ET.ParseError:
            return None

        root = tree.getroot()
        try:
            first_child = root.find("./")
            item_dict = {}
            for child in first_child:
                if child.tag != 'colors':
                    item_dict[child.tag] = child.text
                else:
                    item_dict[child.tag] = [item.text for item in child]
        except TypeError:
            return None
        return item_dict

    def get_from_url(self, api_url, iter):
        req = Request(url=api_url[0], headers=self.headers)
        with urlopen(req) as url:
            try:
                tree = ET.parse(url)
            except ET.ParseError:
                if api_url[1] == 0:
                    self.logger.error('No color at iteration:{}'.format(iter))
                elif api_url[1] == 1:
                    self.logger.error('No palette at iteration:{}'.format(iter))
                else:
                    self.logger.error('No pattern at iteration:{}'.format(iter))
                return None
            root = tree.getroot()
            try:
                first_child = root.find("./")
                item_dict = {}
                for child in first_child:
                    if child.tag != 'colors':
                        item_dict[child.tag] = child.text
                    else:
                        item_dict[child.tag] = [item.text for item in child]
            except TypeError:
                return None
            return item_dict

    @staticmethod
    def color_url(hex):
        url = "http://www.colourlovers.com/api/color/{}".format(hex)
        return url, 0

    @staticmethod
    def palette_url(id):
        url = 'http://www.colourlovers.com/api/palette/{}?showPaletteWidths=1'.format(str(id))
        return url, 1

    @staticmethod
    def pattern_url(id):
        url = 'http://www.colourlovers.com/api/pattern/{}'.format(str(id))
        return url, 2

    def write_to_color(self, start_iter):
        if start_iter == 0:
            self.db.drop_colors()
            self.db.create_tables()
        # for hex in range(start_iter, 16777216):
        for hex in range(start_iter, 1000):
            try:
                color_url = self.color_url('{0:06X}'.format(hex))
                color = self.get_from_url(color_url, hex)
                if color is None:
                    continue
                values = (color['id'],
                      color['userName'],
                      color['hex'],
                      color['numViews'],
                      color['numVotes'],
                      color['numHearts'])
                self.db.insert_color(values)
            except:
                self.logger.error("Color iterator stopped at: {}".format(str(hex)))

    def write_to_palette(self, start_iter):
        if start_iter == 0:
            self.db.drop_palettes()
            self.db.create_tables()
        # for id in range(start_iter, 4638914):
        for id in range(start_iter, 1000):
            try:
                palette_url = self.palette_url(id)
                palette = self.get_from_url(palette_url, id)
                if palette is None:
                    continue
                pcolor = palette['colors']
                if palette['colorWidths'] is not None:
                    colorWidths = palette['colorWidths'].split(',')
                else:
                    colorWidths = ['NULL' for _ in range(len(pcolor))]

                if len(pcolor) != 5:
                    curlen = len(pcolor)
                    value = 5 - len(pcolor)
                    for _ in range(value):
                        pcolor.append('NULL')
                        colorWidths.append('NULL')

                values = (palette['id'],
                          palette['userName'],
                          palette['numViews'],
                          palette['numVotes'],
                          palette['numHearts'],
                          pcolor[0],
                          pcolor[1],
                          pcolor[2],
                          pcolor[3],
                          pcolor[4],
                          colorWidths[0],  # 'NULL',  #
                          colorWidths[1],  # 'NULL',  #
                          colorWidths[2],  # 'NULL',  #
                          colorWidths[3],  # 'NULL',  #
                          colorWidths[4]   # 'NULL',  #
                          )
                self.db.insert_palette(values)
            except:
                self.logger.info("Palette iterator stopped at: {}".format(str(id)))

    def write_to_pattern(self, start_iter):
        if start_iter == 0:
            self.db.drop_patterns()
            self.db.create_tables()
        # for id in range(start_iter, 5788439):
        for id in range(start_iter, 1000):
            try:
                pattern_url = self.palette_url(id)
                pattern = self.get_from_url(pattern_url, id)
                if pattern is None:
                    continue
                pcolor = pattern['colors']
                if len(pcolor) != 5:
                    curlen = len(pcolor)
                    value = 5 - len(pcolor)
                    for _ in range(value):
                        pcolor.append('NULL')
                try:
                    template_number = pattern['url'].split('/')[-2]
                except KeyError:
                    template_number = -1
                values = (pattern['id'],
                          pattern['userName'],
                          pattern['numViews'],
                          pattern['numVotes'],
                          pattern['numHearts'],
                          pcolor[0],
                          pcolor[1],
                          pcolor[2],
                          pcolor[3],
                          pcolor[4],
                          pattern['imageUrl'],
                          template_number)
                self.db.insert_pattern(values)
            except:
                self.logger.info("Pattern iterator stopped at: {}".format(str(id)))


if __name__ == '__main__':
    pool = Pool(processes=4)
    parser = XMLParser()
    # evaluate "f(20)" asynchronously
    pool.apply_async(parser.write_to_color, range(0))  # runs in *only* one process
    pool.apply_async(parser.write_to_palette, range(0))
    pool.apply_async(parser.write_to_pattern, range(0))

    print("Execution complete")


# EXTREMELY IMPORTANT
#
# color = df[df['path'].str.contains('/color/')].reset_index().drop(columns=['index'])
# color = color.rename(columns={'path': 'color'})
# palettes = df[df['path'].str.contains('/palette/')].reset_index().drop(columns=['index'])
# palettes = palettes.rename(columns={'path': 'palette'})
# pattern = df[df['path'].str.contains('/pattern/')].reset_index().drop(columns=['index'])
# pattern = pattern.rename(columns={'path': 'pattern'})
#
# new_df = pd.concat([color, palettes, pattern], axis=1)
# new_df = new_df.drop(new_df.index[100001:])
# new_df.to_csv('data_paths.csv')
