import pandas as pd
import numpy as np
import time
import sqlalchemy as db


class Visualize:

    def __init__(self):
        self.engine = db.create_engine('mysql+mysqlconnector://'+'color:color'+'@'+'localhost'+'/colorbase', encoding='UTF-8', max_overflow=30)

    def select_templates(self, range):
        start = time.time()
        sql = """SELECT templateNumber, imageUrl FROM patterns WHERE id BETWEEN {} and {}""".format(range[0], range[1])
        df = pd.read_sql(sql, self.engine)
        print("Currently at {}. Took {} secs".format(range[0], time.time() - start))
        return df

    def get_last_id(self, table):
        sql = """SELECT id FROM {} ORDER BY ID DESC LIMIT 1""".format(table)
        df = pd.read_sql(sql, self.engine)
        return df

    @staticmethod
    def template_url(id):
        url = 'http://www.colourlovers.com/patternPreview/{}/CCCCCC/999999/666666/333333/000000.png'.format(str(id))
        return url, 3


def change_number(url):
    new_number = url.split('/')[-2]
    return new_number


def main():
    data = Visualize()

# def main():
#     start = time.time()
#     data = Visualize()
    # print("The process as started")
    # sql = """UPDATE patterns AS f SET f.templateNumber = (SELECT temp.templateNumber FROM temp_table AS temp WHERE f.imageUrl = temp.imageUrl)"""
    # with data.engine.begin() as conn:  # TRANSACTION
    #     print("Executing query")
    #     conn.execute(sql)
    #     print("Successful")
    # print("Done")


if __name__ == '__main__':
    main()





