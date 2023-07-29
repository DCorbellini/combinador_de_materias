from bs4 import BeautifulSoup
import sqlite3
from pprint import pprint


DEFAULT_DIR = './files/'
DEFAULT_FILENAME = 'oferta.htm'
DATABASE = 'materias_db'

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
    con = sqlite3.connect('materias.db')
    cur = con.cursor()

    load_table_ofertas(cur, DEFAULT_DIR+DEFAULT_FILENAME)
    con.commit()

    res = cur.execute('SELECT * FROM OFERTA')
    pprint(res.fetchall())


def create_table_ofertas(cur):
    cur.execute('''create table if not exists OFERTA (
                    codigo int, 
                    comision int,
                    dia var(10),
                    turno var(10)
                )''')


def load_table_ofertas(cur, fullpath):
    # in case it doesn't exist
    create_table_ofertas(cur)
    # in case it did exist
    cur.execute('DELETE FROM OFERTA')

    with open(fullpath) as f_oferta:
        soup = BeautifulSoup(f_oferta, 'html.parser')

    codigo_anterior = 0
    for row in [_ for _ in [tr.find_all('td') for tr in soup.table.find_all('tr')] if len(_) > 0]:
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

        cur.execute(f'''INSERT INTO OFERTA (codigo, comision, dia, turno) VALUES
            ({codigo}, {comision}, "{codigo_dia[s_comision[0]]}", "{codigo_turno[s_comision[1]]}")
            ''')


if __name__ == '__main__':
    main()
