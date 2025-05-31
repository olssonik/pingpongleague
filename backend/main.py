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
        players_list.append(
            {
                "username": username_val,
                "elo": elo_val,
                "description": desc_val,
                "achievements": achieve_val,
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


# --- Add Player Route (Uses DEFAULT_ELO) ---
@app.route("/add_player", methods=["POST"])
@app.route("/api/add_player", methods=["POST"])
def add_player_route():
    data = request.get_json()
    if not data or not data.get("username"):
        return jsonify({"error": "Username is required"}), 400

    username = data["username"].strip()
    description = data.get("description", "").strip()
    achievements = data.get("achievements", "").strip()
    elo = data.get("ELO", DEFAULT_ELO)
    try:
        elo = int(elo)
    except ValueError:
        return jsonify({"error": "ELO must be a valid number."}), 400

    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (username, description, ELO, achievements) VALUES (?, ?, ?, ?)",
            (username, description, elo, achievements),
        )
        conn.commit()
        new_player_id = cursor.lastrowid
        return (
            jsonify(
                {
                    "message": "Player added successfully",
                    "player": {
                        "id": new_player_id,
                        "username": username,
                        "description": description,
                        "ELO": elo,
                        "achievements": achievements,
                    },
                }
            ),
            201,
        )
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except sqlite3.Error as e:
        print(f"Database error in add_player_route: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if conn:
            conn.close()


# --- Add Single Game Route ---
# This route performs ELO updates for the specific game being added.
# It does NOT call recalculate_all_elos().
@app.route("/add_game", methods=["POST"])
@app.route("/api/add_game", methods=["POST"])
def add_game_route():
    data = request.get_json()
    required_fields = ["p1", "p2", "winner", "season"]
    if not all(field in data for field in required_fields):
        return (
            jsonify({"error": "Missing required game data (p1, p2, winner, season)"}),
            400,
        )

    p1_name = data["p1"]
    p2_name = data["p2"]
    winner_name = data["winner"]
    season = data.get("season")
    try:
        season = int(season) if season is not None else None
    except ValueError:
        return jsonify({"error": "Season must be a valid number."}), 400
    if season is None:  # Assuming season is mandatory
        return jsonify({"error": "Season is required for the game."}), 400

    date_played = data.get("date_played", None)
    doubles = data.get("doubles", 0)
    archived = data.get("archived", 0)

    if p1_name == p2_name:
        return jsonify({"error": "Player 1 and Player 2 cannot be the same"}), 400
    if winner_name not in [p1_name, p2_name]:
        return jsonify({"error": "Winner must be one of the players"}), 400

    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO games (p1, p2, doubles, winner, archived, season, date_played) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (p1_name, p2_name, doubles, winner_name, archived, season, date_played),
        )

        cursor.execute("SELECT ELO FROM players WHERE username = ?", (p1_name,))
        p1_elo_row = cursor.fetchone()
        cursor.execute("SELECT ELO FROM players WHERE username = ?", (p2_name,))
        p2_elo_row = cursor.fetchone()

        if not p1_elo_row or not p2_elo_row:
            conn.rollback()
            return (
                jsonify(
                    {
                        "error": "One or both players not found for ELO update. Game not added."
                    }
                ),
                500,
            )

        p1_elo_before, p2_elo_before = p1_elo_row[0], p2_elo_row[0]
        k1, k2 = get_k(p1_name, cursor), get_k(p2_name, cursor)
        exp_p1, exp_p2 = expected(p1_elo_before, p2_elo_before), expected(
            p2_elo_before, p1_elo_before
        )

        if winner_name == p1_name:
            p1_elo_after, p2_elo_after = p1_elo_before + k1 * (
                1 - exp_p1
            ), p2_elo_before + k2 * (0 - exp_p2)
        else:
            p1_elo_after, p2_elo_after = p1_elo_before + k1 * (
                0 - exp_p1
            ), p2_elo_before + k2 * (1 - exp_p2)

        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?",
            (round(p1_elo_after), p1_name),
        )
        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?",
            (round(p2_elo_after), p2_name),
        )
        conn.commit()
        return jsonify({"message": "Game added and ELOs updated successfully"}), 201
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in add_game_route: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if conn:
            conn.close()


# --- Add Multiple Games Route ---
# This route performs ELO updates for each game in the batch.
# It does NOT call recalculate_all_elos().
@app.route("/add_multiple_games", methods=["POST"])
@app.route("/api/add_multiple_games", methods=["POST"])
def add_multiple_games_route():
    data = request.get_json()
    games_to_add = data.get("games")
    use_current_time_for_batch = data.get("use_current_time", False)

    if not isinstance(games_to_add, list) or not games_to_add:
        return (
            jsonify({"error": "Request must include a non-empty list of games."}),
            400,
        )

    conn = None
    processed_games_count = 0
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        for game_data in games_to_add:
            p1_name = game_data.get("p1")
            p2_name = game_data.get("p2")
            winner_name = game_data.get("winner")
            season = game_data.get("season")
            try:
                season = int(season) if season is not None else None
            except ValueError:
                raise ValueError(f"Season must be a valid number in game: {game_data}")
            if season is None:
                raise ValueError(f"Season is required for game in batch: {game_data}")

            if not all([p1_name, p2_name, winner_name]):
                raise ValueError(
                    f"A game in the batch is missing p1, p2, or winner: {game_data}"
                )
            if p1_name == p2_name:
                raise ValueError(f"Players cannot be the same in game: {game_data}")
            if winner_name not in [p1_name, p2_name]:
                raise ValueError(
                    f"Winner is not one of the players in game: {game_data}"
                )

            date_played = (
                int(time.time())
                if use_current_time_for_batch
                else game_data.get("date_played", None)
            )
            cursor.execute(
                "INSERT INTO games (p1, p2, doubles, winner, archived, season, date_played) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (p1_name, p2_name, 0, winner_name, 0, season, date_played),
            )

            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p1_name,))
            p1_elo_row = cursor.fetchone()
            cursor.execute("SELECT ELO FROM players WHERE username = ?", (p2_name,))
            p2_elo_row = cursor.fetchone()

            if not p1_elo_row or not p2_elo_row:
                raise ValueError(f"Player not found for ELO update: {game_data}")

            p1_elo_before, p2_elo_before = p1_elo_row[0], p2_elo_row[0]
            k1, k2 = get_k(p1_name, cursor), get_k(p2_name, cursor)
            exp_p1, exp_p2 = expected(p1_elo_before, p2_elo_before), expected(
                p2_elo_before, p1_elo_before
            )

            if winner_name == p1_name:
                p1_elo_after, p2_elo_after = p1_elo_before + k1 * (
                    1 - exp_p1
                ), p2_elo_before + k2 * (0 - exp_p2)
            else:
                p1_elo_after, p2_elo_after = p1_elo_before + k1 * (
                    0 - exp_p1
                ), p2_elo_before + k2 * (1 - exp_p2)

            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p1_elo_after), p1_name),
            )
            cursor.execute(
                "UPDATE players SET ELO = ? WHERE username = ?",
                (round(p2_elo_after), p2_name),
            )
            processed_games_count += 1

        conn.commit()
        return (
            jsonify({"message": f"Successfully added {processed_games_count} games."}),
            201,
        )
    except ValueError as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 400
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in add_multiple_games_route: {e}")
        return (
            jsonify({"error": "A database error occurred processing the batch."}),
            500,
        )
    finally:
        if conn:
            conn.close()


# --- Delete (Hard Delete) a Game Route ---
@app.route("/api/game/<int:game_id>", methods=["DELETE"])
@app.route("/game/<int:game_id>", methods=["DELETE"])
def delete_game_route(game_id):
    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM games WHERE id = ?", (game_id,))
        game = cursor.fetchone()
        if not game:
            return jsonify({"error": "Game not found."}), 404

        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()
        print(f"Game with ID {game_id} has been permanently deleted.")

        recalculate_all_elos()  # This handles its own connection

        return (
            jsonify(
                {
                    "message": f"Game {game_id} permanently deleted and all ELOs recalculated."
                }
            ),
            200,
        )
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in delete_game_route: {e}")
        return jsonify({"error": "Database operation failed during delete."}), 500
    except Exception as e:
        print(f"Unexpected error in delete_game_route: {e}")
        return (
            jsonify({"error": "An internal server error occurred during delete."}),
            500,
        )
    finally:
        if conn:
            conn.close()


# --- Update/Edit a Game Route ---
@app.route("/api/game/<int:game_id>", methods=["PUT"])
@app.route("/game/<int:game_id>", methods=["PUT"])
def update_game_route(game_id):
    data = request.get_json()

    required_fields = ["p1", "p2", "winner", "season"]
    if not all(field in data for field in required_fields):
        return (
            jsonify({"error": "Missing required fields (p1, p2, winner, season)"}),
            400,
        )

    p1_name = data["p1"]
    p2_name = data["p2"]
    winner_name = data["winner"]

    try:
        season = int(data["season"])
    except ValueError:
        return jsonify({"error": "Season must be a valid number."}), 400
    if season <= 0:
        return jsonify({"error": "Season must be a positive number."}), 400

    if p1_name == p2_name:
        return jsonify({"error": "Player 1 and Player 2 cannot be the same"}), 400
    if winner_name not in [p1_name, p2_name]:
        return jsonify({"error": "Winner must be one of the players"}), 400

    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM games WHERE id = ?", (game_id,))
        game = cursor.fetchone()
        if not game:
            return jsonify({"error": "Game not found."}), 404

        cursor.execute(
            "UPDATE games SET p1 = ?, p2 = ?, winner = ?, season = ? WHERE id = ?",
            (p1_name, p2_name, winner_name, season, game_id),
        )
        conn.commit()
        print(f"Game with ID {game_id} has been updated.")

        recalculate_all_elos()  # This handles its own connection

        return (
            jsonify(
                {
                    "message": f"Game {game_id} updated successfully and all ELOs recalculated."
                }
            ),
            200,
        )
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in update_game_route: {e}")
        return jsonify({"error": "Database operation failed during update."}), 500
    except Exception as e:
        print(f"Unexpected error in update_game_route: {e}")
        return (
            jsonify({"error": "An internal server error occurred during update."}),
            500,
        )
    finally:
        if conn:
            conn.close()


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


# Optional: Admin Route for ELO Recalculation
@app.route("/admin/recalculate_elos", methods=["POST"])
def trigger_recalculate_elos():
    print("Admin request to recalculate all ELOs.")
    recalculate_all_elos()
    return jsonify({"message": "Full ELO recalculation initiated."}), 200


if __name__ == "__main__":
    # The global call to recalculate_all_elos() from user's original code:
    # This will run every time the Flask development server reloads.
    # For a production environment, or if recalculation is slow,
    # it's better to trigger this via an explicit admin action (like the route above).
    recalculate_all_elos()
    app.run(host="0.0.0.0", port=3000, debug=True)
