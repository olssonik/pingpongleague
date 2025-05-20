import sqlite3

DB_PATH = "./core.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    return conn, cursor


def get_k(games_played):
    return 16 if games_played > 30 else 32


def expected(score_a, score_b):
    return 1 / (1 + 10 ** ((score_b - score_a) / 400))


def update_elo(winner_elo, loser_elo, winner_games, loser_games):
    K_w = get_k(winner_games)
    K_l = get_k(loser_games)

    exp_win = expected(winner_elo, loser_elo)
    exp_lose = expected(loser_elo, winner_elo)

    new_winner_elo = winner_elo + K_w * (1 - exp_win)
    new_loser_elo = loser_elo + K_l * (0 - exp_lose)

    return new_winner_elo, new_loser_elo

class EloManager:
    def __init__(self):
        slef.all_games
