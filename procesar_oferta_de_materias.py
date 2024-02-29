from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import IntegrityError
from pprint import pprint
import warnings


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

CODIGOS_A_IGNORAR = [
    # las materias transversales se cursan mas de un dia por semana
    901, 902, 903, 904, 911, 912,
    # las materias electivas no tienen sus correlativas
    3677, 3678, 3679
                     ]


def main():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    load_table(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute(f'SELECT * FROM {TABLE}')
    pprint(res.fetchall())


def create_table(cur):
    # cur.execute(f'''drop table {TABLE}''')
    cur.execute(f'''create table if not exists {TABLE} (
                    codigo int, 
                    comision int,
                    dia var(10),
                    turno var(10),
                    modalidad var(25),
                    PRIMARY KEY (codigo, comision)
                    FOREIGN KEY(codigo) REFERENCES materias(codigo)
                )''')


def load_table(cur, filepath):
    # in case it doesn't exist
    create_table(cur)
    # in case it did exist
    cur.execute(f'DELETE FROM {TABLE}')

    with open(filepath, encoding='cp1252') as file:
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

        modalidad = row[5].string.strip(' ()"')

        try:
            cur.execute(f'''INSERT INTO {TABLE} (codigo, comision, dia, turno, modalidad) VALUES
                ({codigo}
                , {comision}
                , "{codigo_dia[s_comision[0]]}"
                , "{codigo_turno[s_comision[1]]}"
                , "{modalidad}")
                ''')
        except IntegrityError as e:
            warnings.warn(f'La materia {codigo} tiene multiples comisiones con el codigo {comision}. '
                          'Se tomara la primera y se ignorara el resto')



if __name__ == '__main__':
    main()
