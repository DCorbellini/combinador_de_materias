from bs4 import BeautifulSoup
import sqlite3
from pprint import pprint


DEFAULT_DIR = './files/'
DEFAULT_FILENAME = 'historia.htm'
DATABASE = 'materias.db'
TABLE = 'MATERIAS'


def main():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    load_table(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute(f'SELECT * FROM {TABLE}')
    pprint(res.fetchall())


def load_table(cur, filepath):

    with open(filepath) as file:
        soup = BeautifulSoup(file, 'html.parser')

    for row in [tr.find_all('td') for tr in soup.table.tbody.find_all('tr')]:
        codigo = int(row[0].div.string.strip())
        nota = int(row[3].div.string.strip())

        cur.execute(f'UPDATE {TABLE} SET nota = {nota} WHERE codigo = {codigo}')


if __name__ == '__main__':
    main()
