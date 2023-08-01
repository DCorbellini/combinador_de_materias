from bs4 import BeautifulSoup
import sqlite3
from pprint import pprint


DEFAULT_DIR = './files/'
DEFAULT_FILENAME = 'materias.htm'
DATABASE = 'materias.db'
TABLE_MATERIAS = 'MATERIAS'
TABLE_CORRELATIVAS = 'CORRELATIVAS'


def main():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    load_table(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute(f'SELECT * FROM {TABLE_MATERIAS}')
    pprint(res.fetchall())


def create_table(cur):
    cur.execute(f'''create table if not exists {TABLE_MATERIAS} (
                    codigo int PRIMARY KEY, 
                    nombre var(50),
                    nota int
                )''')
    cur.execute(f'''create table if not exists {TABLE_CORRELATIVAS} (
                    codigo int, 
                    correlativa int,
                    PRIMARY KEY (codigo, correlativa)
                    FOREIGN KEY(codigo) REFERENCES materias(codigo)
                    FOREIGN KEY(correlativa) REFERENCES materias(codigo)
                )''')


def load_table(cur, filepath):
    # in case they don't exist
    create_table(cur)
    # in case they did exist
    cur.execute(f'DELETE FROM {TABLE_CORRELATIVAS}')
    cur.execute(f'DELETE FROM {TABLE_MATERIAS}')

    with open(filepath, encoding='cp1252') as file:
        soup = BeautifulSoup(file, 'html.parser')

    for table in soup.find_all('tbody'):
        # primer tr es el titulo
        for row in table.find_all('tr')[1:]:
            codigo = int(row.th.string)
            nombre = row.find_all('td')[0].string.strip()
            cur.execute(f'''INSERT INTO {TABLE_MATERIAS} (codigo, nombre, nota) VALUES
                ({codigo}, "{nombre}", 0)
                ''')

            # correlativas puede estar vacio
            correlativas = row.find_all('td')[1].string or ''
            for correlativa in [_.strip() for _ in correlativas.split('/') if _.strip().isnumeric()]:
                cur.execute(f'''INSERT INTO {TABLE_CORRELATIVAS} (codigo, correlativa) VALUES
                    ({codigo}, {correlativa})
                    ''')


if __name__ == '__main__':
    main()
