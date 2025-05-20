from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
K = 32
db = "./game_database.db"


def expected(score_a, score_b):
    return 1 / (1 + 10 ** ((score_b - score_a) / 400))


def update_elo(winner_elo, loser_elo):
    exp_win = expected(winner_elo, loser_elo)
    exp_lose = expected(loser_elo, winner_elo)
    return (winner_elo + K * (1 - exp_win), loser_elo + K * (0 - exp_lose))


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

        if winner == p1:
            new_p1, new_p2 = update_elo(p1_elo, p2_elo)
        else:
            new_p2, new_p1 = update_elo(p2_elo, p1_elo)

        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(new_p1), p1)
        )
        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(new_p2), p2)
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
def trigger_recalc():
    obj = get_data()
    return jsonify(obj), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
