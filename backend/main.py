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
DEFAULT_ELO = 400  # Centralized default ELO


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


# --- REVERTED Recalculate All ELOs Function (to match user's provided logic) ---
def recalculate_all_elos():
    print("Recalculating all ELOs using user's specified sequential update logic...")
    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        # Reset all player ELOs to the DEFAULT_ELO before recalculating
        cursor.execute("UPDATE players SET ELO = ?", (DEFAULT_ELO,))

        # Fetch all games (archived or not, as per user's original logic for this function)
        # Ordered by ID ASC for sequential processing
        cursor.execute("SELECT p1, p2, winner FROM games ORDER BY id ASC")
        all_games = cursor.fetchall()

        if not all_games:
            print("No games found to recalculate ELOs. Player ELOs reset to default.")
            conn.commit()  # Commit the ELO reset
            conn.close()
            return

        for p1_name, p2_name, winner_name in all_games:
            # Fetch current ELO for p1 for this specific game
            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p1_name,))
            p1_elo_row = cursor.fetchone()
            # Fetch current ELO for p2 for this specific game
            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p2_name,))
            p2_elo_row = cursor.fetchone()

            if not p1_elo_row or not p2_elo_row:
                print(
                    f"Warning: Player {p1_name} or {p2_name} not found during ELO recalculation for game. Skipping this game's ELO update."
                )
                continue

            p1_elo = p1_elo_row[0]
            p2_elo = p2_elo_row[0]

            k1 = get_k(p1_name, cursor)
            k2 = get_k(p2_name, cursor)

            exp_p1 = expected(p1_elo, p2_elo)
            exp_p2 = expected(p2_elo, p1_elo)

            # Calculate new ELOs based on this single game
            if winner_name == p1_name:
                p1_elo += k1 * (1 - exp_p1)  # Direct modification of current ELO
                p2_elo += k2 * (0 - exp_p2)  # Direct modification of current ELO
            elif winner_name == p2_name:
                p1_elo += k1 * (0 - exp_p1)
                p2_elo += k2 * (1 - exp_p2)
            else:
                print(
                    f"Warning: Winner '{winner_name}' in game between {p1_name} and {p2_name} is not one of the players. Skipping ELO update for this game."
                )
                continue

            # Update ELOs in the database for these two players IMMEDIATELY
            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p1_elo), p1_name),
            )
            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p2_elo), p2_name),
            )
            # The ELOs for these players are now updated in the DB before the next game in the loop is processed.

        conn.commit()  # Final commit after all games in the loop are processed
        print(
            f"ELO recalculation complete. All player ELOs updated based on game history, starting from {DEFAULT_ELO}."
        )
    except sqlite3.Error as e:
        print(f"Database error during ELO recalculation: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error during ELO recalculation: {e}")
    finally:
        if conn:
            conn.close()


# --- User's Original Get Data Function ---
def get_data():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    # Fetch only non-archived games for general display
    cursor.execute(
        "SELECT id, p1, p2, winner, date_played, archived, season FROM games WHERE archived = 0 ORDER BY id ASC"
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


if __name__ == "__main__":
    # The global call to recalculate_all_elos() from user's original code:
    # This will run every time the Flask development server reloads.
    # For a production environment, or if recalculation is slow,
    # it's better to trigger this via an explicit admin action (like the route above).
    recalculate_all_elos()
    app.run(host="0.0.0.0", port=3000, debug=True)
