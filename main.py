import sqlite3
from pprint import pprint
from tabulate import tabulate
import pandas as pd

import procesar_materias
import procesar_historia_academica
import procesar_oferta_de_materias

DEFAULT_DIR = './files/'
FILE_MATERIAS = 'materias.htm'
FILE_HISTORIA = 'historia.htm'
FILE_OFERTA = 'oferta.htm'
DATABASE = 'materias.db'
TABLE_HISTORIA = 'HISTORIA'
TABLE_OFERTA = 'OFERTA'
TABLE_CORRELATIVAS = 'CORRELATIVAS'
TABLE_MATERIAS = 'MATERIAS'

dias = [
    'Lunes',
    'Martes',
    'Miercoles',
    'Jueves',
    'Viernes',
    'Sabado'
]
turnos = [
    'Mañana',
    'Tarde',
    'Noche'
]


def main(file_materias, file_historia, file_oferta):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    procesar_materias.load_table(cur, file_materias)
    con.commit()
    procesar_historia_academica.load_table(cur, file_historia)
    con.commit()
    procesar_oferta_de_materias.load_table(cur, file_oferta)
    con.commit()

    ofertas = get_ofertas(cur, '''
    (
        Turno="Tarde" OR
        Turno="Noche" AND NOT EXISTS (SELECT * FROM OFERTA O2 WHERE O2.CODIGO=O.CODIGO AND O2.Turno="Tarde")
        ) OR
    Dia="Sabado"
    ''')
    generar_combinaciones(cur, ofertas, [3628, 3630] )
    # print_combinacion(cur, {
    #     'Jueves': (3679, 4900),
    #     'Lunes': (3649, 1900),
    #     'Martes': (3677, 2900),
    #     'Miercoles': (3649, 3900),
    #     'Sabado': (3628, 6300),
    #     'Viernes': (3630, 5300)
    # })


def generar_combinaciones(cur, ofertas, requisitos=None, combinacion=None, i=0, materias=None):
    if requisitos is None:
        requisitos = []
    if materias is None:
        materias = [None for _ in dias]
    if combinacion is None:
        combinacion = {}

    if i >= len(dias):
        if set(requisitos).issubset(materias):
            print_combinacion(cur, combinacion)
        return

    dia = dias[i]

    # Dias que no tienen ninguna materia
    if not ofertas[dia]:
        combinacion[dia] = None
        generar_combinaciones(cur, ofertas, requisitos, combinacion, i + 1, materias)
    else:
        for oferta in ofertas[dia]:
            codigo, _ = oferta
            if codigo in materias:
                continue
            materias[i] = codigo
            combinacion[dia] = oferta
            generar_combinaciones(cur, ofertas, requisitos, combinacion, i + 1, materias)
            materias[i] = None


def print_combinacion(cur, combinacion):
    table = {dia: {turno: '' for turno in turnos} for dia in dias}
    for dia in dias:
        if not combinacion[dia]:
            continue
        codigo, comision = combinacion[dia]
        res = cur.execute(f'''
            SELECT M.Nombre, O.Turno 
            FROM {TABLE_OFERTA} O
            INNER JOIN {TABLE_MATERIAS} M ON O.Codigo=M.Codigo 
            WHERE O.Codigo={codigo} AND O.Comision={comision}
        ''')
        nombre, turno = res.fetchone()
        table[dia][turno] = f'{nombre}\n{codigo} - {comision}'

    df = pd.DataFrame(table)
    print(tabulate(df,
                   headers="keys",
                   tablefmt='grid',
                   colalign=['center' for i in range(7)]))

    # print(tabulate(table,
    #                headers=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Vienes', 'Sabado'],
    #                showindex=['M', 'T', 'N'],
    #                tablefmt='grid',
    #                colalign=['center' for i in range(7)]))


def get_ofertas(cur, condiciones=''):
    crear_vista_disponibles(cur)

    ofertas = {}
    for dia in dias:
        ofertas[dia] = cur.execute(f'''
            SELECT O.Codigo, O.Comision
              FROM {TABLE_OFERTA} O
             WHERE O.Codigo in (SELECT D.Codigo FROM DISPONIBLES D)
               AND O.Dia = "{dia}"
               {'AND (' + condiciones + ')' if condiciones else ''}
        ''').fetchall()

    # res = cur.execute('SELECT Codigo FROM DISPONIBLES')
    # pprint(res.fetchall())

    return ofertas


def crear_vista_disponibles(cur):
    cur.execute(f'''
        CREATE TEMP VIEW APROBADAS AS
        SELECT M.Codigo
        FROM {TABLE_MATERIAS} M
        WHERE M.Nota>=4
    ''')

    cur.execute(f'''
        CREATE TEMP VIEW DISPONIBLES AS
        SELECT M.Codigo
        FROM {TABLE_MATERIAS} M
        WHERE NOT EXISTS (
            SELECT * FROM {TABLE_CORRELATIVAS} C 
            WHERE C.Codigo = M.Codigo AND C.Correlativa NOT IN (SELECT * FROM APROBADAS)
        )
        EXCEPT
        SELECT A.Codigo
        FROM APROBADAS A
    ''')


if __name__ == '__main__':
    main(DEFAULT_DIR + FILE_MATERIAS,
         DEFAULT_DIR + FILE_HISTORIA,
         DEFAULT_DIR + FILE_OFERTA)
