import sqlite3
import datetime

from pathlib import Path
from os.path import join
from core.utils.directory_manipulation import Directory

def insert_teams_data(team_data):
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.executemany("""
        INSERT INTO team (
            team_id,
            team_name,
            team_abv
        ) VALUES (?,?,?)""", team_data)

        db_connection.commit()
        print("Team data inserted successfully")
    except Exception as e:
        print(e)
        raise e


def insert_participation_data(participation_data):
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.executemany("""
        INSERT INTO participation (
            participation_id,
            fk_team_id,
            team_name,
            team_is_home,
            minutes_played,
            field_goals,
            field_goals_attempts,
            field_goals_percentage,
            three_point_field_goals,
            three_point_field_goals_attempts,
            three_point_field_goals_percentage,
            free_throws,
            free_throws_attempts,
            free_throws_percentage,
            offensive_rebounds,
            defensive_rebounds,
            total_rebounds,
            assists,
            steals,
            blocks,
            turnover,
            personal_faults,
            points,
            mat_count_by_team,
            won
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", participation_data)

        db_connection.commit()
        print("Participation data inserted successfully")
    except Exception as e:
        print(e)
        raise e


def insert_match_data(match_data):

    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.executemany("""
            INSERT INTO match_data (
                fk_participation_home,
                fk_participation_away,
                date
            ) VALUES (?, ?, ?);
        """, match_data)

        db_connection.commit()
        print("Match data inserted successfully")
    except Exception as e:
        print(e)
        raise e


def retrieve_participation_data(match_id, team_is_home):
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute(
            """SELECT * FROM participation WHERE fk_match_id = ? AND team_is_home = ?""", (match_id, team_is_home))
        return(cursor.fetchall())
    except Exception as e:
        print(e)
        raise e


def retrieve_match_data(match_id):
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute("""SELECT * FROM match_data WHERE id = ?""", match_id)
        return(cursor.fetchall())
    except Exception as e:
        print(e)
        raise e


def retrieve_team_id_from_abv(team_abv):
    """
    Recebe a abreviação de um time e procura na tabela team do banco qual é o id desse time

    Se for usar essa função pra conseguir 1 time, usar no formato: retrieve_team_data(('___',))
    """

    # Filtrar por abreviação
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute(
            """SELECT team_id FROM team WHERE team_name = ?""", team_abv)
        return(cursor.fetchone())
    except Exception as e:
        print(e)
        raise e


def match_data_factory(cursor, row):
    #! Essa função foi feita completamente na base da gambiarra. Otimizar depois.
    match_stats = {
        "home_team_stats": {},
        "away_team_stats": {}
    }

    index_offset = 4

    # Inserção de dados dos times
    for value_index, column in enumerate(cursor.description[index_offset:]):
        # Fiz essa checagem pra esse método poder funcionar num INNER JOIN
        # com 2 linhas da mesma tabela (time de casa e time fora)
        if(column[0] not in match_stats["home_team_stats"]):
            match_stats["home_team_stats"][column[0]
                                           ] = row[value_index + index_offset]
        else:
            match_stats["away_team_stats"][column[0]
                                           ] = row[value_index + index_offset]

    entries_to_remove = ['participation_id', 'fk_team_id',
                         'team_name', 'team_is_home', 'minutes_played']

    # Tirando o lixo que não precisa
    for entry in entries_to_remove:
        match_stats["home_team_stats"].pop(entry, None)
        match_stats["away_team_stats"].pop(entry, None)

    return match_stats


def retrieve_match_stats():
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        db_connection.row_factory = match_data_factory
        cursor = db_connection.cursor()

        cursor.execute(
            """
            SELECT * 
            FROM match_data as md
            INNER JOIN participation as home_tp
            ON md.fk_participation_home = home_tp.participation_id
            INNER JOIN participation as away_tp
            ON md.fk_participation_away = away_tp.participation_id;""")
        results = cursor.fetchall()
        print("Match stats retrieved!")

        return results
    except Exception as e:
        print(e)
        raise e


def check_tables():
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute(""" SELECT * FROM participation;""")
        print(cursor.fetchall())
        cursor.execute("""SELECT * FROM match_data;""")
        print(cursor.fetchall())
        cursor.execute(""" SELECT * FROM team;""")
        print(cursor.fetchall())
    except Exception as e:
        print(e)
        raise e


def create_id_participation():
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute(
            """ SELECT participation_id FROM participation ORDER BY participation_id DESC  ;""")
        lista = cursor.fetchall()

        try:
            team_id = lista[0][0]
            return team_id + 1

        except Exception as e:
            return 0

    except Exception as e:
        print(e)
        raise e


def get_datetime(date):
    return datetime.date(date[0], date[1], date[2])


def get_last_date():
    """Gera uma lista de datas no formato [ano,mes,dia] começando pelo ultimo dia+1 que temos dados no banco

    Returns:
        list: A lista de datas formatadas como listas [ano,mes,dia]
    """
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute("""SELECT date FROM match_data ORDER BY date DESC""")
        dates = cursor.fetchall()

        try:
            formatted_date = dates[0][0].split("-")
            formatted_date[0] = int(formatted_date[0])  # ano
            formatted_date[1] = int(formatted_date[1])  # mes
            formatted_date[2] = int(formatted_date[2])  # dia

            return formatted_date

        except Exception as e:
            return [2017, 10, 17]

    except Exception as e:
        print(e)
        raise e

def get_teams_abbreviations():
    try:
        db_connection = sqlite3.connect(join(Directory(Path(__file__).resolve().parent.parent.parent).cwd,
                                                 'data', 'database.sqlite3'))
        cursor = db_connection.cursor()

        cursor.execute("SELECT t.team_name, t.team_abv FROM team as t")

        results = cursor.fetchall()

        dicionario = {}
        for item in results:
            dicionario[item[0]] = item[1]

        return dicionario
    except Exception as e:
        print(e)
        raise e



if __name__ == "__main__":

    # fake_team_data = [('Magic', 'Orlando 2', '39:56', 7, 20, 0.350, 0,
    #                    0, 0.350, 8, 8, 1.000, 4, 5, 9, 1, 1, 0, 5, 4, 22, 3, 1, 0, 1)]
    # fake_match_data = [(2, 1, '31-12-2018', 1)]

    print(get_teams_abbreviations())
    # print(get_teams_abbreviations())
    # SELECT * FROM match_data as md INNER JOIN participation as tp ON md.fk_participation_home = tp.team_id;
