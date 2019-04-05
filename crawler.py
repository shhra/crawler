from urllib.request import Request, urlopen
from colordb import ColorDB
import json


class Colors:
    
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
     (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

    def get_color(self, color):
        api_url = "http://www.colourlovers.com/api/color/{}?format=json".format(color)
        req = Request(url=api_url, headers=self.headers)
        with urlopen(req) as url:
            data = json.loads(url.read())
            each = data[0]
            final = {'id': each['id'],
                     'userName': each['userName'],
                     'hex': each['hex'],
                     'numViews': each['numViews'],
                     'numVotes': each['numVotes'],
                     'numHearts': each['numHearts'],
                     'rank': each['rank']}
        return final

    def get_top_color(self, offset):
        response = []
        api_url = "http://www.colourlovers.com/api/colors/top?format=json&numResults=100&resultOffset={}".format(offset)
        req = Request(url=api_url, headers=self.headers)
        with urlopen(req) as url:
            data = json.loads(url.read())
            for each in data:
                final = {'id': each['id'],
                         'userName': each['userName'],
                         'hex': each['hex'],
                         'numViews': each['numViews'],
                         'numVotes': each['numVotes'],
                         'numHearts': each['numHearts']}
                response.append(final)
        return response

        # print("The color id {}, by user{}, is {}, has {} views, {} votes and {}\
        # hearts".format(each['id'], each['userName'], each['hex'], each['numViews'],
        # each['numVotes'], each['numHearts']))

    def get_top_palettes(self, offset):
        response = []
        api_url = "http://www.colourlovers.com/api/palettes/top?format=json&numResults=100&resultOffset={}&showPaletteWidths=1".format(offset)
        req = Request(url=api_url, headers=self.headers)
        with urlopen(req) as url:
            data = json.loads(url.read())
            for each in data:
                # print(i, each['id'], each['title'], each['userName'], each['numViews'],
                # each['numVotes'], each['numHearts'],
                # each['colors'], each['colorWidths'])
                widths = [str(val) for val in each['colorWidths']]
                final = {'id': each['id'],
                         'userName': each['userName'],
                         'numViews': each['numViews'],
                         'numVotes': each['numVotes'],
                         'numHearts': each['numHearts'],
                         'colors': each['colors'],
                         'colorWidths': widths}
                response.append(final)
        return response

    def get_top_users(self, offset):
        response = []
        api_url = "http://www.colourlovers.com/api/lovers/top?format=json&numResults=100&resultOffset={}".format(offset)
        req = Request(url=api_url, headers=self.headers)
        with urlopen(req) as url:
            data = json.loads(url.read())
            for each in data:
                final = {'username': each['userName'],
                         'rating': each['rating'],
                         'numColors': each['numColors'],
                         'numPalettes': each['numPalettes'],
                         'numPatterns': each['numPatterns']}
                response.append(final)
        return response

    def get_top_patterns(self, offset):
        response = []
        api_url = "http://www.colourlovers.com/api/patterns/top?format=json&numResults=100&resultOffset={}".format(offset)
        req = Request(url=api_url, headers=self.headers)
        with urlopen(req) as url:
            data = json.loads(url.read())
            for each in data:
                imageurl = each['imageUrl'].split('/')
                imageurl[2] = 'static.colourlovers.com'
                finalurl = '/'.join(imageurl)
                try:
                    template_number = each['template']['url'].split('/')[-2]
                except KeyError:
                    template_number = -1
                final = {'id': each['id'],
                         'userName': each['userName'],
                         'numViews': each['numViews'],
                         'numVotes': each['numVotes'],
                         'numHearts': each['numHearts'],
                         'colors': each['colors'],
                         'imageUrl': finalurl,
                         'templateNumber': template_number
                         }
                response.append(final)
        return response


if __name__ == '__main__':
    colors = Colors()
    db = ColorDB()
    db.drop_tables()
    db.create_tables()
    db.change_to_utf()
    for i in range(0, 1000, 100):
        color = colors.get_top_color(i)
        for test in color:
            values = (test['id'],
                      test['userName'],
                      test['hex'],
                      test['numViews'],
                      test['numVotes'],
                      test['numHearts'])
            db.insert_color(values)
        print("Current batch {} for color is inserted".format(i))

        pattern = colors.get_top_patterns(i)
        for test in pattern:
            color = test['colors']
            if len(color) != 5:
                curlen = len(color)
                value = 5 - len(color)
                for _ in range(value):
                    color.append('NULL')

            values = (test['id'],
                      test['userName'],
                      test['numViews'],
                      test['numVotes'],
                      test['numHearts'],
                      color[0],
                      color[1],
                      color[2],
                      color[3],
                      color[4],
                      test['imageUrl'],
                      test['templateNumber'])

            db.insert_pattern(values)
        print("Current batch {} for pattern is inserted".format(i))

        palette = colors.get_top_palettes(i)
        for test in palette:
            color = test['colors']
            colorWidths = test['colorWidths']
            if len(color) != 5:
                curlen = len(color)
                value = 5 - len(color)
                for _ in range(value):
                    color.append('NULL')
                    colorWidths.append('NULL')

            values = (test['id'],
                      test['userName'],
                      test['numViews'],
                      test['numVotes'],
                      test['numHearts'],
                      color[0],
                      color[1],
                      color[2],
                      color[3],
                      color[4],
                      str(colorWidths[0]),
                      str(colorWidths[1]),
                      str(colorWidths[2]),
                      str(colorWidths[3]),
                      str(colorWidths[4])
                      )
            db.insert_palette(values)

        print("Current batch {} for palette is inserted".format(i))

