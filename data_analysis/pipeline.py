"""
Ping Pong League Analysis Pipeline
A modular system for analyzing ping pong match results with Elo ratings.
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime


@dataclass
class MatchResult:
    """Data class representing a single match result."""
    index: int
    date_played: Optional[datetime]
    p1: str
    p2: str
    doubles: bool
    winner: str
    archived: bool
    season: int


class StatCalculator(ABC):
    """Abstract base class for all statistics calculators."""

    @abstractmethod
    def calculate(self, matches: List[MatchResult]) -> Dict[str, any]:
        """Calculate statistics from match results."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this statistic."""
        pass


class EloCalculator(StatCalculator):
    """Calculates and tracks Elo ratings over time."""

    def __init__(self, initial_rating: float = 500.0, k_factor: float = 32.0):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings_history: Dict[str, List[Tuple[Optional[datetime], float]]] = {}
        self.current_ratings: Dict[str, float] = {}

    def get_name(self) -> str:
        return "Elo"

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate expected score for player A against player B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def _update_rating(self, winner_rating: float, loser_rating: float) -> Tuple[float, float]:
        """Update ratings after a match."""
        expected_winner = self._expected_score(winner_rating, loser_rating)
        expected_loser = self._expected_score(loser_rating, winner_rating)

        new_winner_rating = winner_rating + self.k_factor * (1 - expected_winner)
        new_loser_rating = loser_rating + self.k_factor * (0 - expected_loser)

        return new_winner_rating, new_loser_rating

    def _initialize_player(self, player: str, date: Optional[datetime] = None) -> None:
        """Initialize a new player's rating."""
        if player not in self.current_ratings:
            self.current_ratings[player] = self.initial_rating
            self.ratings_history[player] = [(date, self.initial_rating)]

    def calculate(self, matches: List[MatchResult]) -> Dict[str, any]:
        """Calculate Elo ratings from match results."""
        self.current_ratings.clear()
        self.ratings_history.clear()

        # Separate matches with and without dates
        dated_matches = [m for m in matches if m.date_played is not None]
        undated_matches = [m for m in matches if m.date_played is None]

        # Process undated matches first to establish initial ratings
        for match in undated_matches:
            if not match.doubles:  # Only process singles matches for now
                self._initialize_player(match.p1)
                self._initialize_player(match.p2)

                winner_rating = self.current_ratings[match.winner]
                loser = match.p1 if match.winner == match.p2 else match.p2
                loser_rating = self.current_ratings[loser]

                new_winner_rating, new_loser_rating = self._update_rating(
                    winner_rating, loser_rating
                )

                self.current_ratings[match.winner] = new_winner_rating
                self.current_ratings[loser] = new_loser_rating

                # Add to history without dates
                self.ratings_history[match.winner].append((None, new_winner_rating))
                self.ratings_history[loser].append((None, new_loser_rating))

        # Sort dated matches by date
        dated_matches.sort(key=lambda x: x.date_played)

        # Process dated matches
        for match in dated_matches:
            if not match.doubles:  # Only process singles matches for now
                self._initialize_player(match.p1, match.date_played)
                self._initialize_player(match.p2, match.date_played)

                winner_rating = self.current_ratings[match.winner]
                loser = match.p1 if match.winner == match.p2 else match.p2
                loser_rating = self.current_ratings[loser]

                new_winner_rating, new_loser_rating = self._update_rating(
                    winner_rating, loser_rating
                )

                self.current_ratings[match.winner] = new_winner_rating
                self.current_ratings[loser] = new_loser_rating

                # Add to history with dates
                self.ratings_history[match.winner].append((match.date_played, new_winner_rating))
                self.ratings_history[loser].append((match.date_played, new_loser_rating))

        return {
            'current_ratings': self.current_ratings.copy(),
            'ratings_history': self.ratings_history.copy()
        }

    def plot_ratings_over_time(self, save_path: Optional[str] = None) -> None:
        """Plot Elo ratings over time for all players."""
        plt.figure(figsize=(12, 8))

        # Define a varied color palette
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#9edae5',
            '#393b79', '#637939', '#8c6d31', '#843c39', '#7b4173'
        ]

        # Get the latest date across all players for horizontal line extension
        all_dates = []
        for history in self.ratings_history.values():
            dates = [entry[0] for entry in history if entry[0] is not None]
            all_dates.extend(dates)

        if not all_dates:
            print("No dated matches found to plot.")
            return

        max_date = max(all_dates)

        for i, (player, history) in enumerate(self.ratings_history.items()):
            dates = [entry[0] for entry in history if entry[0] is not None]
            ratings = [entry[1] for entry in history if entry[0] is not None]

            if dates:  # Only plot if there are dated matches
                # Use color from palette, cycling if more players than colors
                color = colors[i % len(colors)]

                # Plot the main line
                plt.plot(dates, ratings, label=player, linewidth=2, color=color)

                # Add diamond marker for first game
                plt.plot(dates[0], ratings[0], marker='D', markersize=8, color=color,
                         markeredgecolor='black', markeredgewidth=1, zorder=5)

                # Add horizontal line from last game to end of chart
                last_date = dates[-1]
                last_rating = ratings[-1]

                if last_date < max_date:
                    plt.plot([last_date, max_date], [last_rating, last_rating],
                             color=color, linestyle='-', linewidth=2)

                # Add diamond marker at max date with current Elo label
                plt.plot(max_date, last_rating, marker='D', markersize=8, color=color,
                         markeredgecolor='black', markeredgewidth=1, zorder=5)
                plt.text(max_date, last_rating, f'   {last_rating:.0f}',
                         verticalalignment='center', fontsize=9, color=color,
                         weight='bold', zorder=6)

        plt.xlabel('Date')
        plt.ylabel('Elo Rating')
        plt.title('Ping Pong Elo Ratings Over Time')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        # plt.show()


class DataLoader:
    """Handles loading and parsing match data."""

    @staticmethod
    def load_from_database(
            db_path: str,
            table_name: str = "games",
            season_filter: Optional[int] = None,
            include_archived: bool = True
    ) -> List[MatchResult]:
        """Load match results from SQLite database."""
        query = f"SELECT * FROM {table_name}"
        conditions = []

        if not include_archived:
            conditions.append("archived = 0")

        if season_filter is not None:
            conditions.append(f"season = {season_filter}")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date_played ASC, \"id\" ASC"

        try:
            with sqlite3.connect(db_path) as conn:
                df = pd.read_sql_query(query, conn)

            # Convert date column, handling null values
            df['date_played'] = pd.to_datetime(df['date_played'], unit='s', errors='coerce')

            matches = []
            for _, row in df.iterrows():
                match = MatchResult(
                    index=int(row['id']),
                    date_played=row['date_played'] if pd.notna(row['date_played']) else None,
                    p1=str(row['p1']),
                    p2=str(row['p2']),
                    doubles=bool(row['doubles']),
                    winner=str(row['winner']),
                    archived=bool(row['archived']),
                    season=int(row['season'])
                )
                matches.append(match)

            return matches

        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        except Exception as e:
            raise ValueError(f"Error loading data: {e}")

    @staticmethod
    def load_from_csv(file_path: str, date_format: str = '%Y-%m-%d') -> List[MatchResult]:
        """Load match results from CSV file."""
        df = pd.read_csv(file_path)

        # Convert date column, handling null values
        df['date_played'] = pd.to_datetime(df['date_played'], format=date_format, errors='coerce')

        matches = []
        for _, row in df.iterrows():
            match = MatchResult(
                index=int(row['id']),
                date_played=row['date_played'] if pd.notna(row['date_played']) else None,
                p1=str(row['p1']),
                p2=str(row['p2']),
                doubles=bool(row['doubles']),
                winner=str(row['winner']),
                archived=bool(row['archived']),
                season=int(row['season'])
            )
            matches.append(match)

        return matches

    @staticmethod
    def load_from_dataframe(df: pd.DataFrame) -> List[MatchResult]:
        """Load match results from pandas DataFrame."""
        matches = []
        for _, row in df.iterrows():
            match = MatchResult(
                index=int(row['id']),
                date_played=row['date_played'] if pd.notna(row['date_played']) else None,
                p1=str(row['p1']),
                p2=str(row['p2']),
                doubles=bool(row['doubles']),
                winner=str(row['winner']),
                archived=bool(row['archived']),
                season=int(row['season'])
            )
            matches.append(match)

        return matches

    @staticmethod
    def get_database_info(db_path: str, table_name: str = "games") -> Dict[str, any]:
        """Get information about the database structure and contents."""
        try:
            with sqlite3.connect(db_path) as conn:
                # Get table schema
                schema_query = f"PRAGMA table_info({table_name})"
                schema_df = pd.read_sql_query(schema_query, conn)

                # Get basic stats
                stats_query = f"""
                SELECT 
                    COUNT(*) as total_matches,
                    COUNT(date_played) as matches_with_dates,
                    COUNT(*) - COUNT(date_played) as matches_without_dates,
                    COUNT(DISTINCT p1) + COUNT(DISTINCT p2) - COUNT(DISTINCT CASE WHEN p1 = p2 THEN p1 END) as unique_players,
                    COUNT(DISTINCT season) as seasons,
                    SUM(doubles) as doubles_matches,
                    SUM(archived) as archived_matches
                FROM {table_name}
                """
                stats_df = pd.read_sql_query(stats_query, conn)

                # Get season breakdown
                season_query = f"""
                SELECT 
                    season,
                    COUNT(*) as matches,
                    COUNT(date_played) as dated_matches
                FROM {table_name}
                GROUP BY season
                ORDER BY season
                """
                season_df = pd.read_sql_query(season_query, conn)

                return {
                    'schema': schema_df.to_dict('records'),
                    'stats': stats_df.iloc[0].to_dict(),
                    'season_breakdown': season_df.to_dict('records')
                }

        except sqlite3.Error as e:
            raise ValueError(f"Database error: {e}")
        except Exception as e:
            raise ValueError(f"Error getting database info: {e}")


class PingPongAnalyzer:
    """Main analyzer class that coordinates all statistics calculations."""

    def __init__(self):
        self.calculators: List[StatCalculator] = []
        self.matches: List[MatchResult] = []
        self.results: Dict[str, any] = {}

    def add_calculator(self, calculator: StatCalculator) -> None:
        """Add a statistics calculator to the pipeline."""
        self.calculators.append(calculator)

    def load_data(
            self,
            source: Union[str, pd.DataFrame],
            source_type: str = "database",
            table_name: str = "games",
            season_filter: Optional[int] = None,
            include_archived: bool = True,
            **kwargs
    ) -> None:
        """Load match data from database, file, or DataFrame."""
        if source_type == "database" and isinstance(source, str):
            self.matches = DataLoader.load_from_database(
                source, table_name, season_filter, include_archived
            )
        elif source_type == "csv" and isinstance(source, str):
            self.matches = DataLoader.load_from_csv(source, **kwargs)
        elif isinstance(source, pd.DataFrame):
            self.matches = DataLoader.load_from_dataframe(source)
        else:
            raise ValueError(
                "Invalid source type. Use 'database' for SQLite files, "
                "'csv' for CSV files, or pass a pandas DataFrame"
            )

    def get_database_info(self, db_path: str, table_name: str = "games") -> Dict[str, any]:
        """Get information about the database structure and contents."""
        return DataLoader.get_database_info(db_path, table_name)

    def print_database_info(self, db_path: str, table_name: str = "games") -> None:
        """Print detailed information about the database."""
        try:
            info = self.get_database_info(db_path, table_name)

            print("\n" + "=" * 60)
            print("DATABASE INFORMATION")
            print("=" * 60)

            # Schema
            print(f"\nTable: {table_name}")
            print("-" * 30)
            for col in info['schema']:
                print(f"{col['name']:<15} {col['type']:<10} {'NULL' if col['notnull'] == 0 else 'NOT NULL'}")

            # Stats
            stats = info['stats']
            print(f"\nDatabase Statistics:")
            print("-" * 30)
            print(f"Total matches: {stats['total_matches']}")
            print(f"Matches with dates: {stats['matches_with_dates']}")
            print(f"Matches without dates: {stats['matches_without_dates']}")
            print(f"Unique players: {stats['unique_players']}")
            print(f"Doubles matches: {stats['doubles_matches']}")
            print(f"Archived matches: {stats['archived_matches']}")
            print(f"Number of seasons: {stats['seasons']}")

            # Season breakdown
            print(f"\nSeason Breakdown:")
            print("-" * 30)
            for season in info['season_breakdown']:
                print(f"Season {season['season']:2d}: {season['matches']:3d} matches "
                      f"({season['dated_matches']:3d} with dates)")

        except Exception as e:
            print(f"Error getting database info: {e}")

    def run_analysis(self) -> Dict[str, any]:
        """Run all registered calculators on the loaded data."""
        if not self.matches:
            raise ValueError("No data loaded. Call load_data() first.")

        self.results.clear()

        for calculator in self.calculators:
            calc_name = calculator.get_name()
            print(f"Running {calc_name} analysis...")
            self.results[calc_name] = calculator.calculate(self.matches)

        return self.results

    def get_results(self) -> Dict[str, any]:
        """Get the results of the last analysis run."""
        return self.results.copy()

    def print_summary(self) -> None:
        """Print a summary of the current analysis results."""
        if not self.results:
            print("No analysis results available. Run run_analysis() first.")
            return

        print("\n" + "=" * 50)
        print("PING PONG LEAGUE ANALYSIS SUMMARY")
        print("=" * 50)

        print(f"Total matches processed: {len(self.matches)}")
        dated_matches = sum(1 for m in self.matches if m.date_played is not None)
        print(f"Matches with dates: {dated_matches}")
        print(f"Matches without dates: {len(self.matches) - dated_matches}")

        if 'Elo' in self.results:
            elo_results = self.results['Elo']
            current_ratings = elo_results['current_ratings']

            print(f"\nCurrent Elo Ratings:")
            print("-" * 30)
            sorted_players = sorted(current_ratings.items(), key=lambda x: x[1], reverse=True)
            for rank, (player, rating) in enumerate(sorted_players, 1):
                print(f"{rank:2d}. {player:<15} {rating:6.0f}")


# Example usage
def main():
    """Example of how to use the ping pong analysis pipeline with database."""
    # Initialize the analyzer
    analyzer = PingPongAnalyzer()

    # Add Elo calculator
    elo_calc = EloCalculator(initial_rating=400.0, k_factor=32.0)
    analyzer.add_calculator(elo_calc)

    # Example usage with your database
    db_path = "../backend/game_database.db"
    assert os.path.exists(db_path)

    try:
        # Print database information
        analyzer.print_database_info(db_path)

        # Load data from database (all seasons, including archived)
        analyzer.load_data(db_path, source_type="database")

        # Or load specific season only
        # analyzer.load_data(db_path, source_type="database", season_filter=3, include_archived=False)

        # Run analysis
        results = analyzer.run_analysis()

        # Print summary
        analyzer.print_summary()

        # Plot Elo ratings over time
        elo_calc.plot_ratings_over_time('elo_ratings_timeline.png')

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure your database file exists and has the correct table structure.")


if __name__ == "__main__":
    main()
