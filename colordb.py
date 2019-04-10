import mysql.connector


class ColorDB:

    def __init__(self):
        self.create_colordb()
        self.conn = self.create_connection()

    @staticmethod
    def create_connection():
        mydb = mysql.connector.connect(
            host="localhost",
            user="color",
            passwd="color",
            database="colorbase"
        )
        # print("Connection established successfully.")
        return mydb

    @staticmethod
    def create_colordb():
        initdb = mysql.connector.connect(
            host="localhost",
            user="color",
            passwd="color",
        )
        cur = initdb.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS colorbase")

    def create_tables(self):
        cur = self.conn.cursor()
        color_table = """
                      CREATE TABLE IF NOT EXISTS colors ( 
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      colorId INT,
                      userName VARCHAR (255),
                      hex VARCHAR (255),
                      numViews INT,
                      numVotes INT,
                      numHearts INT,
                      colorRank INT,
                      dateCreated DATE
                      )
                    """
        cur.execute(color_table)

        pattern_table = """
                      CREATE TABLE IF NOT EXISTS patterns ( 
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      patternId INT,
                      username VARCHAR (255),
                      numViews INT,
                      numVotes INT,
                      numHearts INT,
                      patternRank INT,
                      dateCreated DATE,
                      color1 VARCHAR (255),
                      color2 VARCHAR (255),
                      color3 VARCHAR (255),
                      color4 VARCHAR (255),
                      color5 VARCHAR (255),
                      numColors INT,
                      imageUrl VARCHAR (255),
                      templateNumber INT (255)
                      )
                    """
        cur.execute(pattern_table)

        palette_table = """
                      CREATE TABLE IF NOT EXISTS palettes ( 
                      id INT AUTO_INCREMENT PRIMARY KEY,
                      paletteId INT,
                      username VARCHAR (255),
                      numViews INT,
                      numVotes INT,
                      numHearts INT,
                      paletteRank INT,
                      dateCreated DATE,
                      color1 VARCHAR (255),
                      color2 VARCHAR (255),
                      color3 VARCHAR (255),
                      color4 VARCHAR (255),
                      color5 VARCHAR (255),
                      colorWidths1 VARCHAR (255),
                      colorWidths2 VARCHAR (255),
                      colorWidths3 VARCHAR (255),
                      colorWidths4 VARCHAR (255),
                      colorWidths5 VARCHAR (255),
                      numColors INT
                      )
        """
        cur.execute(palette_table)

    def insert_color(self, value, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        query = """
        INSERT INTO colors (colorid, userName, hex, numViews, numVotes, numHearts, colorRank, dateCreated)
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """
        cur.execute(query, value)
        if cur is None:
            self.conn.commit()
        else:
            conn.commit()

    def insert_palette(self, value, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        query = """
        INSERT INTO palettes (paletteId, username, numViews, numVotes, numHearts, paletteRank, dateCreated,
        color1, color2, color3, color4, color5,
        colorWidths1, colorWidths2, colorWidths3, colorWidths4, colorWidths5, numColors)
        VALUES (%s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, value)
        if cur is None:
            self.conn.commit()
        else:
            conn.commit()

    def insert_pattern(self, value, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        query = """
        INSERT INTO patterns (patternId, username, numViews, numVotes, numHearts, patternRank, dateCreated,
        color1, color2, color3, color4, color5, imageUrl, templateNumber, numColors)
        VALUES (%s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, value)
        if cur is None:
            self.conn.commit()
        else:
            conn.commit()

    def drop_colors(self, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        cur.execute("DROP TABLE colors")

    def drop_palettes(self, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        cur.execute("DROP TABLE palettes")

    def drop_patterns(self, conn=None):
        if conn is None:
            cur = self.conn.cursor()
        else:
            cur = conn.cursor()
        cur.execute("DROP TABLE patterns")

    def drop_tables(self):
        self.drop_colors()
        self.drop_palettes()
        self.drop_patterns()

    def change_to_utf(self):
        cur = self.conn.cursor()
        cur.execute("""ALTER TABLE colorbase.colors CONVERT TO CHARACTER SET utf8""")
        cur.execute("""ALTER TABLE colorbase.patterns CONVERT TO CHARACTER SET utf8""")
        cur.execute("""ALTER TABLE colorbase.palettes CONVERT TO CHARACTER SET utf8""")


if __name__ == '__main__':
    db = ColorDB()
    db.create_tables()

