from bs4 import BeautifulSoup
import sqlite3
from pprint import pprint


DEFAULT_DIR = './files/'
DEFAULT_FILENAME = 'historia.htm'
DATABASE = 'materias.db'
TABLE = 'HISTORIA'


def main():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    load_table(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute(f'SELECT * FROM {TABLE}')
    pprint(res.fetchall())


def create_table(cur):
    cur.execute(f'''create table if not exists {TABLE} (
                    codigo int PRIMARY KEY, 
                    nota int
                )''')


def load_table(cur, filepath):
    # in case it doesn't exist
    create_table(cur)
    # in case it did exist
    cur.execute(f'DELETE FROM {TABLE}')

    with open(filepath) as file:
        soup = BeautifulSoup(file, 'html.parser')

    for row in [tr.find_all('td') for tr in soup.table.tbody.find_all('tr')]:
        codigo = int(row[0].div.string.strip())
        nota = int(row[3].div.string.strip())

        cur.execute(f'''INSERT INTO {TABLE} (codigo, nota) VALUES
            ({codigo}, {nota})
            ''')


if __name__ == '__main__':
    main()
