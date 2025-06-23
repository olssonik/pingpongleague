from flask import Flask, jsonify, request
import json  # Kept as per user's original imports
import sqlite3
from flask_cors import CORS
import time
import subprocess  # NEW: For running external scripts
import os  # NEW: For path operations if needed

app = Flask(__name__)
CORS(app)

# --- Configuration ---
K = 32  # User's original K-factor for ELO calculation
db = "./game_database.db"  # User's original database path
DEFAULT_ELO = 480  # Centralized default ELO
SCRIPT_PATH = "./scripts/deploy_db.sh"  # Path to your deployment script


# --- Helper Function to Trigger Deployment Script ---
def trigger_deploy_script():
    """
    Executes the deploy_db.sh script.
    """
    print(f"Attempting to run deployment script: {SCRIPT_PATH}")
    try:
        # Ensure the script path is correct and the script is executable
        # For robustness, you might want to use an absolute path or resolve it
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # full_script_path = os.path.join(script_dir, SCRIPT_PATH.lstrip('./'))

        # Check if script exists and is executable
        if not os.path.exists(SCRIPT_PATH):
            print(f"Error: Deployment script not found at {SCRIPT_PATH}")
            return False, f"Script not found at {SCRIPT_PATH}"
        if not os.access(SCRIPT_PATH, os.X_OK):
            print(
                f"Error: Deployment script at {SCRIPT_PATH} is not executable. Run 'chmod +x {SCRIPT_PATH}'."
            )
            return False, f"Script at {SCRIPT_PATH} is not executable."

        # Using shell=False is generally safer if you construct the command list directly
        # If SCRIPT_PATH can contain spaces or special characters, and you use shell=True, be very careful.
        # For a simple script path like "./scripts/deploy_db.sh", shell=True is often used for convenience.
        # For this case, since it's a fixed path, shell=True should be okay, but be aware.
        result = subprocess.run(
            [SCRIPT_PATH],
            capture_output=True,
            text=True,
            check=False,  # Set to True if you want it to raise CalledProcessError on non-zero exit codes
            shell=False,  # Safer: explicitly list command and args. If shell=True, command is a string.
            # If shell=False, command must be a list like ['/bin/sh', SCRIPT_PATH] or just [SCRIPT_PATH] if it has a shebang
        )

        if result.returncode == 0:
            print("Deployment script executed successfully.")
            if result.stdout:
                print("Script STDOUT:")
                print(result.stdout)
            return True, result.stdout
        else:
            print(f"Deployment script failed with error code {result.returncode}.")
            if result.stdout:
                print("Script STDOUT on error:")
                print(result.stdout)
            if result.stderr:
                print("Script STDERR:")
                print(result.stderr)
            return False, (
                result.stderr
                if result.stderr
                else f"Script failed with code {result.returncode}"
            )

    except FileNotFoundError:
        print(
            f"Error: The script {SCRIPT_PATH} was not found. Make sure the path is correct."
        )
        return False, f"Script {SCRIPT_PATH} not found."
    except PermissionError:
        print(f"Error: Permission denied when trying to execute {SCRIPT_PATH}.")
        return False, f"Permission denied for script {SCRIPT_PATH}."
    except Exception as e:
        print(f"An unexpected error occurred while running deployment script: {e}")
        return False, str(e)


# --- User's Original ELO Helper Functions (UNCHANGED) ---
def expected(score_a, score_b):
    return 1 / (1 + 10 ** ((score_b - score_a) / 400))


def update_elo(winner_elo, loser_elo):  # Kept as is
    exp_win = expected(winner_elo, loser_elo)
    exp_lose = expected(loser_elo, winner_elo)
    return (winner_elo + K * (1 - exp_win), loser_elo + K * (0 - exp_lose))


def get_k(username, cursor):
    cursor.execute(
        "SELECT COUNT(*) FROM games WHERE p1 = ? OR p2 = ?", (username, username)
    )
    count_row = cursor.fetchone()
    count = count_row[0] if count_row else 0
    return 16 if count > 30 else 32


# --- REVERTED Recalculate All ELOs Function (to match user's provided logic) ---
def recalculate_all_elos():
    print("Recalculating all ELOs using locked K-factor logic...")
    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Reset all player ELOs to the default before recalculating
        cursor.execute("UPDATE players SET ELO = ?", (DEFAULT_ELO,))

        # Fetch all games in chronological order
        cursor.execute("SELECT p1, p2, winner FROM games ORDER BY id ASC")
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


# --- Add Player Route (MODIFIED to trigger script) ---
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

        # Trigger deployment script
        script_success, script_output = trigger_deploy_script()
        if not script_success:
            print(
                f"Warning: Deployment script failed after adding player: {script_output}"
            )
            # Decide if this should be a hard error for the user or just a logged warning
            # For now, we'll still return success for the player addition.

        return (
            jsonify(
                {
                    "message": "Player added successfully."
                    + (
                        " Deployment script triggered."
                        if script_success
                        else " Deployment script failed."
                    ),
                    "player": {
                        "id": new_player_id,
                        "username": username,
                        "description": description,
                        "ELO": elo,
                        "achievements": achievements,
                    },
                    "script_output": (
                        script_output if not script_success else None
                    ),  # Optionally include script output on failure
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


# --- Add Single Game Route (MODIFIED to trigger script) ---
@app.route("/add_game", methods=["POST"])
@app.route("/api/add_game", methods=["POST"])
def add_game_route():
    data = request.get_json()
    required_fields = ["p1", "p2", "winner", "season"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required game data"}), 400

    p1_name, p2_name, winner_name = data["p1"], data["p2"], data["winner"]
    season = data.get("season")
    try:
        season = int(season) if season is not None else None
    except ValueError:
        return jsonify({"error": "Season must be a valid number."}), 400
    if season is None:
        return jsonify({"error": "Season is required."}), 400

    date_played = data.get("date_played", None)
    doubles = data.get("doubles", 0)
    archived = data.get("archived", 0)

    if p1_name == p2_name:
        return jsonify({"error": "Players cannot be the same"}), 400
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

        p1_elo_row = cursor.execute(
            "SELECT ELO FROM players WHERE username = ?", (p1_name,)
        ).fetchone()
        p2_elo_row = cursor.execute(
            "SELECT ELO FROM players WHERE username = ?", (p2_name,)
        ).fetchone()
        if not p1_elo_row or not p2_elo_row:
            conn.rollback()
            return (
                jsonify({"error": "Player not found for ELO update. Game not added."}),
                500,
            )

        p1_elo_b, p2_elo_b = p1_elo_row[0], p2_elo_row[0]
        k1, k2 = get_k(p1_name, cursor), get_k(p2_name, cursor)
        exp_p1, exp_p2 = expected(p1_elo_b, p2_elo_b), expected(p2_elo_b, p1_elo_b)
        if winner_name == p1_name:
            p1_elo_a, p2_elo_a = p1_elo_b + k1 * (1 - exp_p1), p2_elo_b + k2 * (
                0 - exp_p2
            )
        else:
            p1_elo_a, p2_elo_a = p1_elo_b + k1 * (0 - exp_p1), p2_elo_b + k2 * (
                1 - exp_p2
            )
        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(p1_elo_a), p1_name)
        )
        cursor.execute(
            "UPDATE players SET ELO = ? WHERE username = ?", (round(p2_elo_a), p2_name)
        )
        conn.commit()

        script_success, script_output = trigger_deploy_script()
        if not script_success:
            print(
                f"Warning: Deployment script failed after adding game: {script_output}"
            )

        return (
            jsonify(
                {
                    "message": "Game added, ELOs updated."
                    + (
                        " Deployment script triggered."
                        if script_success
                        else " Deployment script failed."
                    )
                }
            ),
            201,
        )
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in add_game_route: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        if conn:
            conn.close()


# --- Add Multiple Games Route (MODIFIED to trigger script) ---
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
            p1_name, p2_name = game_data.get("p1"), game_data.get("p2")
            winner_name, season_str = game_data.get("winner"), str(
                game_data.get("season")
            )
            try:
                season = int(season_str)
            except ValueError:
                raise ValueError(f"Invalid season in game: {game_data}")
            if season <= 0:
                raise ValueError(f"Season must be positive: {game_data}")
            if not all([p1_name, p2_name, winner_name]):
                raise ValueError(f"Missing data: {game_data}")
            if p1_name == p2_name:
                raise ValueError(f"Players same: {game_data}")
            if winner_name not in [p1_name, p2_name]:
                raise ValueError(f"Winner invalid: {game_data}")

            date_played = (
                int(time.time())
                if use_current_time_for_batch
                else game_data.get("date_played", None)
            )
            cursor.execute(
                "INSERT INTO games (p1, p2, doubles, winner, archived, season, date_played) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (p1_name, p2_name, 0, winner_name, 0, season, date_played),
            )
            p1r, p2r = (
                cursor.execute(
                    "SELECT ELO FROM players WHERE username=?", (p1_name,)
                ).fetchone(),
                cursor.execute(
                    "SELECT ELO FROM players WHERE username=?", (p2_name,)
                ).fetchone(),
            )
            if not p1r or not p2r:
                raise ValueError(f"Player not found for ELO: {game_data}")
            p1eb, p2eb = p1r[0], p2r[0]
            k1, k2 = get_k(p1_name, cursor), get_k(p2_name, cursor)
            e1, e2 = expected(p1eb, p2eb), expected(p2eb, p1eb)
            if winner_name == p1_name:
                p1ea, p2ea = p1eb + k1 * (1 - e1), p2eb + k2 * (0 - e2)
            else:
                p1ea, p2ea = p1eb + k1 * (0 - e1), p2eb + k2 * (1 - e2)
            cursor.execute(
                "UPDATE players SET ELO=? WHERE username=?", (round(p1ea), p1_name)
            )
            cursor.execute(
                "UPDATE players SET ELO=? WHERE username=?", (round(p2ea), p2_name)
            )
            processed_games_count += 1
        conn.commit()

        script_success, script_output = trigger_deploy_script()
        if not script_success:
            print(
                f"Warning: Deployment script failed after adding multiple games: {script_output}"
            )

        return (
            jsonify(
                {
                    "message": f"Added {processed_games_count} games, ELOs updated."
                    + (
                        " Deployment script triggered."
                        if script_success
                        else " Deployment script failed."
                    )
                }
            ),
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
# This route calls recalculate_all_elos(), which will handle its own script trigger if you add it there.
# Or, if deploy script should run specifically after delete, call trigger_deploy_script() here too.
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

        recalculate_all_elos()
        # If you want to trigger deploy script specifically after a delete and recalc:
        script_success, script_output = trigger_deploy_script()
        if not script_success:
            print(f"Warning: Deploy script failed after delete: {script_output}")

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
    finally:
        if conn:
            conn.close()


# --- Update/Edit a Game Route ---
# This route calls recalculate_all_elos().
@app.route("/api/game/<int:game_id>", methods=["PUT"])
@app.route("/game/<int:game_id>", methods=["PUT"])
def update_game_route(game_id):
    data = request.get_json()
    required_fields = ["p1", "p2", "winner", "season"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    p1_name, p2_name, winner_name = data["p1"], data["p2"], data["winner"]
    try:
        season = int(data["season"])
    except ValueError:
        return jsonify({"error": "Season must be a valid number."}), 400
    if season <= 0:
        return jsonify({"error": "Season must be a positive number."}), 400
    if p1_name == p2_name:
        return jsonify({"error": "Players cannot be the same"}), 400
    if winner_name not in [p1_name, p2_name]:
        return jsonify({"error": "Winner must be one of the players"}), 400

    conn = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM games WHERE id = ?", (game_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Game not found."}), 404

        cursor.execute(
            "UPDATE games SET p1 = ?, p2 = ?, winner = ?, season = ? WHERE id = ?",
            (p1_name, p2_name, winner_name, season, game_id),
        )
        conn.commit()
        print(f"Game with ID {game_id} has been updated.")
        recalculate_all_elos()
        # If you want to trigger deploy script specifically after an edit and recalc:
        # script_success, script_output = trigger_deploy_script()
        # if not script_success: print(f"Warning: Deploy script failed after edit: {script_output}")

        return jsonify({"message": f"Game {game_id} updated, ELOs recalculated."}), 200
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in update_game_route: {e}")
        return jsonify({"error": "Database operation failed during update."}), 500
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
    tr = cursor.fetchone()
    if not tr:
        conn.close()
        return jsonify({"error": "Tournament not found"}), 404
    if not tr[1] and not tr[3]:
        conn.close()
        return jsonify({"message": "Tournament has not started yet"})
    cursor.execute(
        "SELECT player_one, player_two, winner, finished, round FROM tournament_games WHERE tournament_id = ? ORDER BY round ASC, id ASC",
        (tournament_id,),
    )
    gd, rs = {}, cursor.fetchall()
    for grd in gd:
        r_num = grd[4]
        rs.setdefault(r_num, []).append([grd[0], grd[1], grd[2], bool(grd[3])])
    rsl = [rs[rn] for rn in sorted(rs.keys())]
    conn.close()
    return (
        jsonify({"name": tr[0], "active": bool(tr[1]), "winner": tr[2], "rounds": rsl}),
        200,
    )


# Optional: Admin Route for ELO Recalculation
@app.route("/admin/recalculate_elos", methods=["POST"])
def trigger_recalculate_elos():
    print("Admin request to recalculate all ELOs.")
    recalculate_all_elos()
    return jsonify({"message": "Full ELO recalculation initiated."}), 200


# Admin Route to VACUUM Database
@app.route("/admin/vacuum_db", methods=["POST"])
def vacuum_db_route():
    print("Admin request to VACUUM the database.")
    conn = None
    try:
        conn = sqlite3.connect(db)
        conn.execute("VACUUM")
        conn.commit()
        message = "Database VACUUM operation completed successfully."
        print(message)
        return jsonify({"message": message}), 200
    except sqlite3.Error as e:
        message = f"Database error during VACUUM: {e}"
        print(message)
        return jsonify({"error": message}), 500
    finally:
        if conn:
            conn.close()


# Global call to recalculate ELOs from user's original code.
# This runs on every Flask dev server reload. Consider moving to an admin-triggered route.
recalculate_all_elos()

app.run(host="0.0.0.0", port=3000, debug=True)
