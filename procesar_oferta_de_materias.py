from bs4 import BeautifulSoup
import sqlite3
from pprint import pprint


DEFAULT_DIR = './files/'
DEFAULT_FILENAME = 'oferta.htm'
DATABASE = 'materias.db'
TABLE = 'OFERTA'

codigo_turno = {
    '3': 'Mañana',
    '6': 'Tarde',
    '9': 'Noche'
}
codigo_dia = {
    '1': 'Lunes',
    '2': 'Martes',
    '3': 'Miercoles',
    '4': 'Jueves',
    '5': 'Viernes',
    '6': 'Sabado'
}

# Codigos de correlativas, se cursa varios dias por semana y no cumplen el formato de codigo de comision
CODIGOS_A_IGNORAR = [901, 902, 903, 904, 911, 912]


def main():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    load_table(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute(f'SELECT * FROM {TABLE}')
    pprint(res.fetchall())


def create_table(cur):
    cur.execute(f'''create table if not exists {TABLE} (
                    codigo int, 
                    comision int,
                    dia var(10),
                    turno var(10),
                    PRIMARY KEY (codigo, comision)
                    FOREIGN KEY(codigo) REFERENCES materias(codigo)
                )''')


def load_table(cur, filepath):
    # in case it doesn't exist
    create_table(cur)
    # in case it did exist
    cur.execute(f'DELETE FROM {TABLE}')

    with open(filepath) as file:
        soup = BeautifulSoup(file, 'html.parser')

    codigo_anterior = 0
    for row in [tr.find_all('td') for tr in soup.table.tbody.find_all('tr')]:
        s_codigo = row[0].string.strip()
        if not len(s_codigo) > 0:
            codigo = codigo_anterior
        else:
            codigo = int(s_codigo)
            codigo_anterior = codigo

        if codigo in CODIGOS_A_IGNORAR:
            continue

        s_comision = row[2].string.strip()
        try:
            comision = int(s_comision)
        except ValueError:
            continue

        cur.execute(f'''INSERT INTO {TABLE} (codigo, comision, dia, turno) VALUES
            ({codigo}, {comision}, "{codigo_dia[s_comision[0]]}", "{codigo_turno[s_comision[1]]}")
            ''')


if __name__ == '__main__':
    main()
