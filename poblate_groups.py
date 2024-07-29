import os
from typing import List, Dict
import pymysql
from pymysql import Connection
from pymysql.cursors import Cursor


def get_connection() -> Connection:
    user = os.getenv("U_CUP_DB_USER")
    password = os.getenv("U_CUP_DB_PASSWORD")

    return pymysql.connect(
        host="localhost",
        user=user,
        password=password,
        database="u_cup_2024"
    )


def execute_query(sql: str, return_data=False):
    data = None
    connection = get_connection()
    cursor: Cursor = connection.cursor()
    cursor.execute(sql)

    if return_data:
        data = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return data


def get_teams():
    """
    Obtener los datos de equipos_grupos, equipos y grupos
    """
    query = """
        SELECT
            g.id AS grupo_id,
            GROUP_CONCAT(e.id ORDER BY eg.equipo_posicion) AS equipos
        FROM
            equipos_grupos eg
            JOIN equipos e ON eg.equipo_id = e.id
            JOIN grupos g ON eg.grupo_id = g.id
        GROUP BY g.id
    """
    return execute_query(query, return_data=True)


def get_teams_by_groups(teams: List[Dict[str, str]]) -> Dict[int, List[int]]:
    return {
        group_id: [int(equipo_id) for equipo_id in equipos.split(',')]
        for group_id, equipos in teams
    }


def generate_inserts(teams: List[Dict[str, str]]):
    """
    A partir de los equipos y grupos, genera los enfrentamientos de ida y vuelta
    Sea el grupo A = { a1, a2, a3, a4 }
    Las combinatorias resultantes de ida de los enfrentamientos son:
        a1, a2
        a3, a4
        a1, a3
        a4, a2
        a2, a3
        a4, a1
    Las de vuelta son el mismo conjunto de pares pero intercambiando (x, y) por (y, x)
    """

    groups = get_teams_by_groups(teams)
    print(groups)
    partidos = []

    for group, _teams in groups.items():
        comb_ida = [
            (_teams[0], _teams[1]),
            (_teams[2], _teams[3]),
            (_teams[0], _teams[2]),
            (_teams[3], _teams[1]),
            (_teams[1], _teams[2]),
            (_teams[3], _teams[0]),
        ]
        comb_vuelta = [(_tuple[-1], _tuple[0]) for _tuple in comb_ida]

        combinations = comb_ida + comb_vuelta

        partidos.append({"group": group, "partidos": combinations})

    print(partidos)
    sql_queries = []

    for group in partidos:
        for _partido in group["partidos"]:
            sql = f"""
                INSERT INTO partidos (local_id, visitante_id, grupo_id)
                VALUES ({_partido[0]}, {_partido[1]}, {group["group"]})
            """
            sql_queries.append(sql)

    for sentencia in sql_queries:
        execute_query(sentencia)


def main():
    """
    Obtiene equipos y realiza los inserts con el algoritmo de enfrentamientos
    """
    teams = get_teams()
    generate_inserts(teams)


if __name__ == "__main__":
    main()