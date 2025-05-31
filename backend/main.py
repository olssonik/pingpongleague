from flask import Flask, jsonify
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

K = 32
db = "./game_database.db"


def expected(score_a, score_b):
    return 1 / (1 + 10 ** ((score_b - score_a) / 400))


def update_elo(winner_elo, loser_elo):
    exp_win = expected(winner_elo, loser_elo)
    exp_lose = expected(loser_elo, winner_elo)
    return (winner_elo + K * (1 - exp_win), loser_elo + K * (0 - exp_lose))


def get_k(username, cursor):
    cursor.execute(
        "SELECT COUNT(*) FROM games WHERE p1 = ? OR p2 = ?", (username, username)
    )
    count = cursor.fetchone()[0]
    return 16 if count > 30 else 32


def recalculate_all_elos():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET ELO = 400")
    cursor.execute("SELECT p1, p2, winner FROM games ORDER BY id ASC")
    all_games = cursor.fetchall()

    for p1, p2, winner in all_games:
        cursor.execute("SELECT ELO FROM players WHERE username = ?", (p1,))
        p1_elo = cursor.fetchone()[0]
        cursor.execute("SELECT ELO FROM players WHERE username = ?", (p2,))
        p2_elo = cursor.fetchone()[0]

        k1 = get_k(p1, cursor)
        k2 = get_k(p2, cursor)

        exp_p1 = expected(p1_elo, p2_elo)
        exp_p2 = expected(p2_elo, p1_elo)

        if winner == p1:
            p1_elo += k1 * (1 - exp_p1)
            p2_elo += k2 * (0 - exp_p2)
        else:
            p1_elo += k1 * (0 - exp_p1)
            p2_elo += k2 * (1 - exp_p2)

        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(p1_elo), p1)
        )
        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(p2_elo), p2)
        )

    conn.commit()
    conn.close()


def get_data():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, p1, p2, winner, date_played, archived FROM games ORDER BY id ASC"
    )
    all_games = cursor.fetchall()
    games = []

    for id, p1, p2, winner, timestamp, archived in all_games:
        if not archived:
            games.append(
                {"id": id, "players": [p1, p2], "winner": winner, "date": timestamp}
            )

    players = []
    cursor.execute("SELECT username, ELO FROM players")
    all_players = cursor.fetchall()
    for username, elo in all_players:
        players.append({"username": username, "elo": elo})

    obj = {"players": players, "games": games}

    conn.commit()
    conn.close()

    return obj


recalculate_all_elos()

get_data()


@app.route("/api/get_data", methods=["GET"])
@app.route("/get_data", methods=["GET"])
def get_data_route():
    obj = get_data()
    return jsonify(obj), 200


@app.route("/get_tournaments", methods=["GET"])
@app.route("/api/get_tournaments", methods=["GET"])
def get_tournaments():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, active, winner FROM tournaments")
    rows = cursor.fetchall()
    conn.close()

    tournaments = [
        {"id": row[0], "name": row[1], "active": bool(row[2]), "winner": row[3]}
        for row in rows
    ]
    return jsonify({"tournaments": tournaments}), 200


@app.route("/tournament/<int:tournament_id>", methods=["GET"])
@app.route("/api/tournament/<int:tournament_id>", methods=["GET"])
def get_tournament(tournament_id):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, active, winner, finished FROM tournaments WHERE id = ?",
        (tournament_id,),
    )
    tournament_row = cursor.fetchone()

    if not tournament_row:
        conn.close()
        return jsonify({"error": "Tournament not found"}), 404

    active, finished = tournament_row[1], tournament_row[3]
    if not active and not finished:
        conn.close()
        return jsonify({"message": "Tournament has not started yet"})

    # Get all games grouped by round, ordered by round and id (to keep order)
    cursor.execute(
        """
        SELECT player_one, player_two, winner, finished, round
        FROM tournament_games
        WHERE tournament_id = ?
        ORDER BY round ASC, id ASC
        """,
        (tournament_id,),
    )
    games = cursor.fetchall()

    # Group games by round
    rounds = {}
    for game in games:
        player_one, player_two, winner, finished, round_num = game
        rounds.setdefault(round_num, []).append(
            [player_one, player_two, winner, finished]
        )

    conn.close()

    # Convert dict to list sorted by round number
    rounds_list = [rounds[round_num] for round_num in sorted(rounds.keys())]

    return jsonify({"rounds": rounds_list}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
