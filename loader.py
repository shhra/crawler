from colordb import ColorDB
from urllib.request import Request, urlopen
from urllib.error import URLError
import xml.etree.ElementTree as ET
import logging
from threading import Thread
from sys import exit
import argparse
import os
from PIL import Image
import requests
from io import BytesIO


class ThreadWithReturn(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None

    def run(self):
        target = getattr(self, '_target')
        if not target is None:
            self._return = target(*getattr(self, '_args'), **getattr(self, '_kwargs'))

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return


class XMLParser:

    def __init__(self, st, cstart, pstart, ptstart, end):
        self.st = st
        self.cst = cstart
        self.pst = pstart
        self.ptst = ptstart
        self.end = end
        self.logger = logging.getLogger(__name__)
        self.init_logger()
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
                (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        self.db = ColorDB()
        self.db.create_tables()
        self.db.change_to_utf()

    def init_logger(self):
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(filename='./logs/error_{}.log'.format(self.st))
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
        with urlopen(req, timeout=2) as url:
            try:
                tree = ET.parse(url)
            except ET.ParseError:
                if api_url[1] == 0:
                    self.logger.error('No color at iteration:{}'.format(iter))
                elif api_url[1] == 1:
                    self.logger.error('No palette at iteration:{}'.format(iter))
                elif api_url[1] == 2:
                    self.logger.error('No pattern at iteration:{}'.format(iter))
                return None
            root = tree.getroot()
            try:
                first_child = root.find("./")
                item_dict = {}
                for child in first_child:
                    item_dict[child.tag] = child.text
                    if child.tag == 'colors':
                        item_dict['colors'] = [item.text for item in child]
                    if child.tag == 'template':
                        item_dict['template'] = [item.text for item in child]
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

    @staticmethod
    def template_url(id):
        url = 'http://www.colourlovers.com/patternPreview/{}/CCCCCC/999999/666666/333333/000000.png'.format(str(id))
        return url, 3

    def write_to_color(self):
        cur = self.db.create_connection()
        for hex in range(self.cst, self.end):
        # for hex in range(start_iter, 1000):
            if hex % 1000 == 0:
                self.logger.info('color @ {}'.format(str(hex)))
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
                      color['numHearts'],
                      color['rank'],
                      color['dateCreated'])
                self.db.insert_color(values, cur)
            except URLError:
                # print("Re-establishing connection")
                return 404
            except:
                self.logger.exception("Color iterator stopped at: {}".format(str(hex)))
        return 0

    def write_to_palette(self):
        # print("writing palette")
        cur = self.db.create_connection()
        for id in range(self.pst, self.end):
            if id % 1000 == 0:
                self.logger.info("palette @ {}".format(str(id)))
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

                curlen = len(pcolor)
                if len(pcolor) != 5:
                    value = 5 - len(pcolor)
                    for _ in range(value):
                        pcolor.append('NULL')
                        colorWidths.append('NULL')

                values = (palette['id'],
                          palette['userName'],
                          palette['numViews'],
                          palette['numVotes'],
                          palette['numHearts'],
                          palette['rank'],
                          palette['dateCreated'],
                          pcolor[0],
                          pcolor[1],
                          pcolor[2],
                          pcolor[3],
                          pcolor[4],
                          colorWidths[0],  # 'NULL',  #
                          colorWidths[1],  # 'NULL',  #
                          colorWidths[2],  # 'NULL',  #
                          colorWidths[3],  # 'NULL',  #
                          colorWidths[4],
                          curlen  # 'NULL',  #
                          )
                self.db.insert_palette(values, cur)
            except URLError:
                # print("Re-establishing connection")
                return 404
            except:
                self.logger.exception("Palette iterator stopped at: {}".format(str(id)))
        return 0

    def write_to_pattern(self):
        # print("writing pattern")
        cur = self.db.create_connection()
        for id in range(self.ptst, self.end):
            if id % 1000 == 0:
                self.logger.info("pattern @ {}".format(str(id)))
            try:
                pattern_url = self.pattern_url(id)
                pattern = self.get_from_url(pattern_url, id)
                if pattern is None:
                    continue

                imageurl = pattern['imageUrl'].split('/')
                imageurl[2] = 'static.colourlovers.com'
                finalurl = '/'.join(imageurl)

                pcolor = pattern['colors']
                curlen = len(pcolor)
                if len(pcolor) != 5:
                    value = 5 - len(pcolor)
                    for _ in range(value):
                        pcolor.append('NULL')
                try:
                    template_number = pattern['template']['url'].split('/')[-2]
                except KeyError:
                    template_number = -1
                values = (pattern['id'],
                          pattern['userName'],
                          pattern['numViews'],
                          pattern['numVotes'],
                          pattern['numHearts'],
                          pattern['rank'],
                          pattern['dateCreated'],
                          pcolor[0],
                          pcolor[1],
                          pcolor[2],
                          pcolor[3],
                          pcolor[4],
                          finalurl,
                          template_number,
                          curlen)
                self.db.insert_pattern(values, cur)
            except URLError:
                # wait for connection re-establishment
                # print("Re-establishing connection")
                return 404
            except:
                self.logger.exception("Pattern iterator stopped at: {}".format(str(id)))
        return 0

    def update_pattern_and_fetch_image(self):
        cur = self.db.create_connection()
        cursor = cur.cursor()
        sql = """SELECT patternId FROM patterns WHERE patternId BETWEEN %s and %s"""
        value = (self.ptst, self.end)
        cursor.execute(sql, value)
        ids = cursor.fetchall()
        for x in ids:
            id = x[0]
            # if id % 1000 == 0:
            if id % 1000 == 0:
                self.logger.info("pattern @ {}".format(str(id)))
            pattern_url = self.pattern_url(id)
            pattern = self.get_from_url(pattern_url, id)
            try:
                template_number = pattern['template'][1].split('/')[-2]
            except KeyError:
                template_number = -1
            values = (template_number,
                          id)
            self.db.update_patterns(values, cur)
        return 0

    def fetch_images(self):
        for i in range(self.ptst, self.end):
            try:
                filename = str(i)+'.png'
                # image = url
            except URLError:
                continue
        return 0


def get_last_row(st, end):
    try:
        db = ColorDB()
        db.create_tables()
        db.change_to_utf()
        cur = db.conn.cursor()

        sql = "SELECT hex FROM colors WHERE hex BETWEEN '%06X' and '%06X' ORDER BY ID DESC LIMIT 1" % (st, end+1)
        cur.execute(sql)
        out = cur.fetchall()
        if len(out) != 0:
            last_color = int(out[0][0], 16)
        else:
            last_color = -1

        sql = """SELECT patternId FROM patterns WHERE patternId BETWEEN {} and {} ORDER BY ID ASC LIMIT 1""".format(st, end)
        cur.execute(sql)
        out = cur.fetchall()
        if len(out) != 0:
            last_pattern = out[0][0]
        else:
            last_pattern = -1

        sql = """SELECT paletteId FROM palettes WHERE paletteID BETWEEN {} and {} ORDER BY ID DESC LIMIT 1""".format(st,end+1)
        cur.execute(sql)
        out = cur.fetchall()
        if len(out) != 0:
            last_palette = out[0][0]
        else:
            last_palette = -1

        return last_color, last_palette, last_pattern
    except:
        logging.exception("error in range")
        return None


if __name__ == '__main__':
    path = './templates'
    if not os.path.exists(path):
        os.mkdir(path)
    aparser = argparse.ArgumentParser(description='Define ranger of parser')
    aparser.add_argument('--start', metavar='-S', type=int, default=1, help='Start iterator')
    aparser.add_argument('--end', metavar='-E', type=int, default=500, help='End iterator')
    args = aparser.parse_args()

    color = palette = 0

    d = 100000
    parser = XMLParser(args.start, color+1, palette+1, args.start, args.start + d)
    parser1 = XMLParser(args.start + d, color+1, palette+1, args.start + d, args.start + 2*d)
    parser2 = XMLParser(args.start + 2*d, color+1, palette+1, args.start + 2 * d, args.end)
    parser3 = XMLParser(args.start + 3*d, color+1, palette+1, args.start + 4 * d, args.end)
    parser4 = XMLParser(args.start + 4*d, color+1, palette+1, args.start + 5 * d, args.end)

    print(args.start, args.start+d, args.start+2*d, args.start+3*d, args.start+4*d, args.end)
    pattern_thread_1 = ThreadWithReturn(name='Pattern_1', target=parser.update_pattern_and_fetch_image)
    pattern_thread_2 = ThreadWithReturn(name='Pattern_2', target=parser1.update_pattern_and_fetch_image)
    pattern_thread_3 = ThreadWithReturn(name='Pattern_3', target=parser2.update_pattern_and_fetch_image)
    pattern_thread_4 = ThreadWithReturn(name='Pattern_3', target=parser3.update_pattern_and_fetch_image)
    pattern_thread_5 = ThreadWithReturn(name='Pattern_3', target=parser4.update_pattern_and_fetch_image)

    print(" Starting thread at {}".format(args.start))

    pattern_thread_1.start()
    pattern_thread_2.start()
    pattern_thread_3.start()
    pattern_thread_4.start()
    pattern_thread_5.start()

    out  = pattern_thread_1.join()
    out2 = pattern_thread_2.join()
    out3 = pattern_thread_3.join()
    out4 = pattern_thread_4.join()
    out5 = pattern_thread_5.join()

    if out == out2 == out3 == out4 == out5 == 0:
        print("Successful")
        exit(0)
    else:
        exit(-1073741819)

    # important loader code
    # import time
    # start = time.time()
    #
    # aparser = argparse.ArgumentParser(description='Define ranger of parser')
    # aparser.add_argument('--start', metavar='-S', type=int, default=0, help='Start iterator')
    # aparser.add_argument('--end', metavar='-E', type=int, default=10, help='End iterator')
    # args = aparser.parse_args()
    # last = get_last_row(args.start, args.end)
    # color, palette, pattern = last
    # if last[0] == -1:
    #     color = args.start
    # if last[1] == -1:
    #     palette = args.start
    # if last[2] == -1:
    #     pattern = args.start
    #
    # parser = XMLParser(args.start, color+1, palette+1, pattern+1, args.end)
    # # parser.db.drop_tables()
    # # parser.db.create_tables()
    # # parser.db.change_to_utf()
    # # print("starting threads")
    #
    # out = out2 = out3 = 0
    # color_thread = ThreadWithReturn(name='Color', target=parser.write_to_color)
    # # palette_thread = ThreadWithReturn(name='Palette', target=parser.write_to_palette)
    # # pattern_thread = ThreadWithReturn(name='Pattern', target=parser.write_to_pattern)
    #
    # color_thread.start()
    # # palette_thread.start()
    # # pattern_thread.start()
    #
    # out = color_thread.join()
    # # out2 = palette_thread.join()
    # # out3 = palette_thread.join()
    #
    # # parser.logger.info("{} {} {}".format(out, out2, out3))
    # # parser.logger.info("{} {} {}".format(out))
    # if out == out2 == out3 == 0:
    #     exit(0)
    # else:
    #     exit(-1073741819)

    # if out != 0:
    #     # print("From color: ", out)
    #     exit(-1073741819)
    # if out2 != 0:
    #     # print("From pattern: ", out)
    #     exit(-1073741819)
    # if out3 != 0:
    #     # print("From palette: ", out2)
    #     exit(-1073741819)
    # print(out, out2, out3)

    # print("Completed")

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
