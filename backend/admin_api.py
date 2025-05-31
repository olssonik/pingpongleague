import sqlite3

DB_PATH = "./game_database.db"


def update_games(game):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    p1 = game.get("p1")
    p2 = game.get("p2")
    doubles = game.get("doubles", None)
    winner = game.get("winner")
    archived = game.get("archived", None)
    season = game.get("season", None)

    cursor.execute(
        """
        INSERT INTO "games" ("p1", "p2", "doubles", "winner", "archived", "season")
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (p1, p2, doubles, winner, archived, season),
    )

    conn.commit()
    conn.close()


def set_tournament_active(tournament_id, is_active: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    active_val = 1 if is_active else 0
    cursor.execute(
        "UPDATE `tournaments` SET active = ? WHERE id = ?", (active_val, tournament_id)
    )

    conn.commit()
    conn.close()
