import re
from flask import Flask, jsonify, request
import json  # Kept as per user's original imports
import sqlite3
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# --- Configuration ---
K = 32  # User's original K-factor for ELO calculation
db = "./game_database.db"  # User's original database path
DEFAULT_ELO = 480
CURRENT_SEASON = 2


# --- User's Original ELO Helper Functions (UNCHANGED) ---
def expected(score_a, score_b):
    return 1 / (1 + 10 ** ((score_b - score_a) / 400))


def update_elo(winner_elo, loser_elo):  # Kept as is
    exp_win = expected(winner_elo, loser_elo)
    exp_lose = expected(loser_elo, winner_elo)
    return (winner_elo + K * (1 - exp_win), loser_elo + K * (0 - exp_lose))


def get_k(username, cursor):
    # Counts all games (archived or not) for K-factor, as per user's original.
    # If K-factor should only consider active games, add "AND archived = 0" to the query
    cursor.execute(
        "SELECT COUNT(*) FROM games WHERE p1 = ? OR p2 = ?", (username, username)
    )
    count_row = cursor.fetchone()
    count = count_row[0] if count_row else 0
    return 16 if count > 30 else 32


def recalculate_all_elos():
    print("Recalculating all ELOs using locked K-factor logic...")
    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Reset all player ELOs to the default before recalculating
        cursor.execute("UPDATE players SET ELO = ?", (DEFAULT_ELO,))

        # Fetch all games in chronological order
        cursor.execute("SELECT p1, p2, winner FROM games WHERE season = ? ORDER BY id ASC", (CURRENT_SEASON,))
        all_games = cursor.fetchall()

        if not all_games:
            print("No games found. ELOs reset to default.")
            conn.commit()
            return

        game_counts = {}  # Track number of games played per user so far

        for p1_name, p2_name, winner_name in all_games:
            # Initialize counts if new player
            game_counts[p1_name] = game_counts.get(p1_name, 0)
            game_counts[p2_name] = game_counts.get(p2_name, 0)

            # Fetch current ELOs
            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p1_name,))
            p1_row = cursor.fetchone()
            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p2_name,))
            p2_row = cursor.fetchone()

            if not p1_row or not p2_row:
                print(
                    f"Warning: Missing player in game ({p1_name} vs {p2_name}). Skipping."
                )
                continue

            p1_elo = p1_row[0]
            p2_elo = p2_row[0]

            # Determine K-factor based on games played so far
            k1 = 16 if game_counts[p1_name] >= 30 else 32
            k2 = 16 if game_counts[p2_name] >= 30 else 32

            exp_p1 = expected(p1_elo, p2_elo)
            exp_p2 = expected(p2_elo, p1_elo)

            if winner_name == p1_name:
                p1_elo += k1 * (1 - exp_p1)
                p2_elo += k2 * (0 - exp_p2)
            elif winner_name == p2_name:
                p1_elo += k1 * (0 - exp_p1)
                p2_elo += k2 * (1 - exp_p2)
            else:
                print(
                    f"Warning: Invalid winner '{winner_name}' in game ({p1_name} vs {p2_name}). Skipping."
                )
                continue

            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p1_elo), p1_name),
            )
            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p2_elo), p2_name),
            )

            # Increment game counts after processing
            game_counts[p1_name] += 1
            game_counts[p2_name] += 1

        conn.commit()
        print("ELO recalculation complete.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()


# --- User's Original Get Data Function ---
def get_data():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Fetch only non-archived games for general display
    cursor.execute(
        "SELECT id, p1, p2, winner, date_played, archived, season FROM games WHERE season = ? AND archived = 0 ORDER BY id ASC", (CURRENT_SEASON,)
    )
    all_games_rows = cursor.fetchall()
    games_list = []

    for row in all_games_rows:
        id_val, p1_val, p2_val, winner_val, timestamp_val, archived_val, season_val = (
            row
        )
        if not archived_val:
            games_list.append(
                {
                    "id": id_val,
                    "players": [p1_val, p2_val],
                    "winner": winner_val,
                    "date": timestamp_val,
                    "season": season_val,
                }
            )

    players_list = []
    cursor.execute("SELECT username, ELO, description, achievements FROM players")
    all_players_rows = cursor.fetchall()
    for username_val, elo_val, desc_val, achieve_val in all_players_rows:
        try:
            achievements_parsed = json.loads(achieve_val)
        except Exception:
            achievements_parsed = []  # fallback if it's malformed

        players_list.append(
            {
                "username": username_val,
                "elo": elo_val,
                "description": desc_val,
                "achievements": achievements_parsed,
            }
        )

    obj = {"players": players_list, "games": games_list}
    conn.close()
    return obj


# --- User's Original Global Scope Calls ---
# recalculate_all_elos() # This was in user's provided code. It will run on every script (re)load.
# For production, usually triggered by an admin action.
# get_data() # This call's return value is not used here.


# --- User's Original Routes ---
@app.route("/api/get_data", methods=["GET"])
@app.route("/get_data", methods=["GET"])
def get_data_route():
    try:
        obj = get_data()
        return jsonify(obj), 200
    except sqlite3.Error as e:
        print(f"Database error in get_data_route: {e}")
        return (
            jsonify(
                {"error": "Failed to retrieve data from database", "details": str(e)}
            ),
            500,
        )
    except Exception as e:
        print(f"Unexpected error in get_data_route: {e}")
        return (
            jsonify(
                {"error": "An unexpected server error occurred", "details": str(e)}
            ),
            500,
        )


# --- Tournament Endpoints (Placeholders) ---
@app.route("/get_tournaments", methods=["GET"])
@app.route("/api/get_tournaments", methods=["GET"])
def get_tournaments():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, active, winner FROM tournaments")
    rows = cursor.fetchall()
    conn.close()
    tournaments = [
        {"id": r[0], "name": r[1], "active": bool(r[2]), "winner": r[3]} for r in rows
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

    if not tournament_row[1] and not tournament_row[3]:
        conn.close()
        return jsonify({"message": "Tournament has not started yet"})

    cursor.execute(
        "SELECT player_one, player_two, winner, finished, round FROM tournament_games WHERE tournament_id = ? ORDER BY round ASC, id ASC",
        (tournament_id,),
    )
    games_data = cursor.fetchall()
    rounds = {}
    for game_row_data in games_data:
        round_num = game_row_data[4]
        rounds.setdefault(round_num, []).append(
            [
                game_row_data[0],
                game_row_data[1],
                game_row_data[2],
                bool(game_row_data[3]),
            ]
        )
    rounds_list = [rounds[rn] for rn in sorted(rounds.keys())]
    conn.close()
    return (
        jsonify(
            {
                "name": tournament_row[0],
                "active": bool(tournament_row[1]),
                "winner": tournament_row[2],
                "rounds": rounds_list,
            }
        ),
        200,
    )


recalculate_all_elos()
if __name__ == "__main__":
    # The global call to recalculate_all_elos() from user's original code:
    # This will run every time the Flask development server reloads.
    # For a production environment, or if recalculation is slow,
    # it's better to trigger this via an explicit admin action (like the route above).
    app.run(host="0.0.0.0", port=3000, debug=True)
