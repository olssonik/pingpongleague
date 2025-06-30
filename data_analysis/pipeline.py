"""
Ping Pong League Analysis Pipeline
A modular system for analyzing ping pong match results with Elo ratings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import networkx as nx

plt.style.use('seaborn-v0_8')

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


class MatchCountCalculator(StatCalculator):
    """Calculates match counts for each player."""

    def __init__(self):
        self._last_results: Dict[str, any] = {}

    def get_name(self) -> str:
        return "MatchCount"

    def calculate(self, matches: List[MatchResult]) -> Dict[str, any]:
        """Calculate match counts for each player."""
        player_counts: Dict[str, int] = {}

        for match in matches:
            if not match.doubles:  # Only count singles matches
                player_counts[match.p1] = player_counts.get(match.p1, 0) + 1
                player_counts[match.p2] = player_counts.get(match.p2, 0) + 1

        results = {'player_counts': player_counts}
        self._last_results = results  # Store results for later use
        return results

    def print_match_counts(self) -> None:
        """Print players ordered by number of matches."""
        if not self._last_results:
            print("No match count data available. Run calculate() first.")
            return

        player_counts = self._last_results['player_counts']
        sorted_players = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)

        print("\n" + "=" * 40)
        print("PLAYERS BY MATCH COUNT")
        print("=" * 40)

        for rank, (player, count) in enumerate(sorted_players, 1):
            print(f"{rank:2d}. {player:<20} {count:3d} matches")


class NetworkAnalyzer(StatCalculator):
    """Analyzes player interaction networks based on match frequency."""

    def __init__(self):
        self.match_counts: Dict[Tuple[str, str], int] = {}
        self.graph: nx.Graph = nx.Graph()

    def get_name(self) -> str:
        return "Network"

    def calculate(self, matches: List[MatchResult]) -> Dict[str, any]:
        """Calculate network statistics from match results."""
        self.match_counts.clear()
        self.graph.clear()

        # Count matches between each pair of players
        for match in matches:
            if not match.doubles:  # Only process singles matches
                # Create sorted tuple to ensure consistent pairing
                players = tuple(sorted([match.p1, match.p2]))
                self.match_counts[players] = self.match_counts.get(players, 0) + 1

        # Build network graph
        for (p1, p2), count in self.match_counts.items():
            self.graph.add_edge(p1, p2, weight=count)

        # Calculate network statistics
        centrality = nx.degree_centrality(self.graph)
        betweenness = nx.betweenness_centrality(self.graph)

        return {
            'match_counts': self.match_counts.copy(),
            'graph': self.graph.copy(),
            'centrality': centrality,
            'betweenness': betweenness,
            'total_players': len(self.graph.nodes()),
            'total_edges': len(self.graph.edges())
        }

    def plot_network(
            self,
            save_path: Optional[str] = None,
            min_matches: int = 1,
            node_size_multiplier: float = 1000.0,
            edge_width_multiplier: float = 5.0,
            layout: str = 'spring'
    ) -> None:
        """Plot the player network graph.

        Args:
            save_path: Optional path to save the plot
            min_matches: Minimum number of matches to show an edge
            node_size_multiplier: Multiplier for node sizes
            edge_width_multiplier: Multiplier for edge widths
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai')
        """
        if not self.graph.nodes():
            print("No network data available. Run calculate() first.")
            return

        plt.figure(figsize=(14, 10))

        # Filter edges by minimum matches
        filtered_graph = self.graph.copy()
        edges_to_remove = [
            (u, v) for u, v, d in filtered_graph.edges(data=True)
            if d['weight'] < min_matches
        ]
        filtered_graph.remove_edges_from(edges_to_remove)

        # Remove isolated nodes
        isolated_nodes = list(nx.isolates(filtered_graph))
        filtered_graph.remove_nodes_from(isolated_nodes)

        if not filtered_graph.nodes():
            print(f"No edges with >= {min_matches} matches found.")
            return

        # Choose layout
        layout_functions = {
            'spring': nx.spring_layout,
            'circular': nx.circular_layout,
            'kamada_kawai': nx.kamada_kawai_layout
        }

        if layout not in layout_functions:
            layout = 'spring'
            pos = layout_functions[layout](filtered_graph, k=2, iterations=50)

        else:
            pos = layout_functions[layout](filtered_graph)

        # Calculate node sizes based on degree centrality
        centrality = nx.degree_centrality(filtered_graph)
        node_sizes = [centrality.get(node, 0) * node_size_multiplier + 100 for node in filtered_graph.nodes()]

        # Calculate edge widths based on match counts
        edge_weights = [filtered_graph[u][v]['weight'] for u, v in filtered_graph.edges()]
        max_weight = max(edge_weights) if edge_weights else 1
        edge_widths = [w / max_weight * edge_width_multiplier + 0.5 for w in edge_weights]

        # Draw the network
        nx.draw_networkx_nodes(
            filtered_graph, pos,
            node_size=node_sizes,
            node_color='lightblue',
            alpha=0.8
        )

        nx.draw_networkx_edges(
            filtered_graph, pos,
            width=edge_widths,
            alpha=0.6,
            edge_color='gray'
        )

        nx.draw_networkx_labels(
            filtered_graph, pos,
            font_size=10,
            font_weight='bold'
        )

        # Add edge labels showing match counts
        edge_labels = nx.get_edge_attributes(filtered_graph, 'weight')
        nx.draw_networkx_edge_labels(
            filtered_graph, pos, edge_labels,
            font_size=8, alpha=0.7
        )

        plt.title(f'Player Network Graph (min {min_matches} matches)\n'
                  f'Node size = centrality, Edge width = match frequency',
                  fontsize=14)
        plt.axis('off')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

    def print_network_stats(self) -> None:
        """Print network statistics summary."""
        if not self.graph.nodes():
            print("No network data available. Run calculate() first.")
            return

        print("\n" + "=" * 50)
        print("NETWORK ANALYSIS SUMMARY")
        print("=" * 50)

        print(f"Total players: {len(self.graph.nodes())}")
        print(f"Total player pairs: {len(self.graph.edges())}")

        # Most frequent matchups
        sorted_matches = sorted(self.match_counts.items(), key=lambda x: x[1], reverse=True)
        print(f"\nMost frequent matchups:")
        print("-" * 30)
        for i, ((p1, p2), count) in enumerate(sorted_matches[:10]):
            print(f"{i + 1:2d}. {p1} vs {p2}: {count} matches")

        # Network connectivity
        if nx.is_connected(self.graph):
            diameter = nx.diameter(self.graph)
            avg_path_length = nx.average_shortest_path_length(self.graph)
            print(f"\nNetwork connectivity:")
            print("-" * 30)
            print(f"Network diameter: {diameter}")
            print(f"Average path length: {avg_path_length:.2f}")
        else:
            components = list(nx.connected_components(self.graph))
            print(f"\nNetwork has {len(components)} disconnected components")

        # Most central players
        centrality = nx.degree_centrality(self.graph)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        print(f"\nMost connected players:")
        print("-" * 30)
        for i, (player, cent) in enumerate(sorted_centrality[:10]):
            print(f"{i + 1:2d}. {player}: {cent:.3f}")


class EloCalculator(StatCalculator):
    """Calculates and tracks Elo ratings over time."""

    def __init__(self, initial_rating: float = 1200.0, k_factor: float = 32.0):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings_history: Dict[str, List[Tuple[Optional[datetime], float, int]]] = {}
        self.current_ratings: Dict[str, float] = {}
        self.match_indices: List[int] = []  # Track all match indices

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

    def _initialize_player(self, player: str, date: Optional[datetime] = None, match_index: int = 0) -> None:
        """Initialize a new player's rating."""
        if player not in self.current_ratings:
            self.current_ratings[player] = self.initial_rating
            self.ratings_history[player] = [(date, self.initial_rating, match_index)]

    def calculate(self, matches: List[MatchResult]) -> Dict[str, any]:
        """Calculate Elo ratings from match results."""
        self.current_ratings.clear()
        self.ratings_history.clear()
        self.match_indices.clear()

        # Separate matches with and without dates
        dated_matches = [m for m in matches if m.date_played is not None]
        undated_matches = [m for m in matches if m.date_played is None]

        # Process undated matches first to establish initial ratings
        for match in undated_matches:
            if not match.doubles:  # Only process singles matches for now
                self._initialize_player(match.p1, match_index=match.index)
                self._initialize_player(match.p2, match_index=match.index)

                winner_rating = self.current_ratings[match.winner]
                loser = match.p1 if match.winner == match.p2 else match.p2
                loser_rating = self.current_ratings[loser]

                new_winner_rating, new_loser_rating = self._update_rating(
                    winner_rating, loser_rating
                )

                self.current_ratings[match.winner] = new_winner_rating
                self.current_ratings[loser] = new_loser_rating

                # Add to history with match index
                self.ratings_history[match.winner].append((None, new_winner_rating, match.index))
                self.ratings_history[loser].append((None, new_loser_rating, match.index))
                self.match_indices.append(match.index)

        # Sort dated matches by date
        dated_matches.sort(key=lambda x: x.date_played)

        # Process dated matches
        for match in dated_matches:
            if not match.doubles:  # Only process singles matches for now
                self._initialize_player(match.p1, match.date_played, match.index)
                self._initialize_player(match.p2, match.date_played, match.index)

                winner_rating = self.current_ratings[match.winner]
                loser = match.p1 if match.winner == match.p2 else match.p2
                loser_rating = self.current_ratings[loser]

                new_winner_rating, new_loser_rating = self._update_rating(
                    winner_rating, loser_rating
                )

                self.current_ratings[match.winner] = new_winner_rating
                self.current_ratings[loser] = new_loser_rating

                # Add to history with dates and match index
                self.ratings_history[match.winner].append((match.date_played, new_winner_rating, match.index))
                self.ratings_history[loser].append((match.date_played, new_loser_rating, match.index))
                self.match_indices.append(match.index)

        return {
            'current_ratings': self.current_ratings.copy(),
            'ratings_history': self.ratings_history.copy()
        }

    def plot_ratings_over_time(self, save_path: Optional[str] = None, use_index: bool = True) -> None:
        """Plot Elo ratings over time for all players.

        Args:
            save_path: Optional path to save the plot
            use_index: If True, plot by match index instead of dates
        """
        plt.figure(figsize=(12, 8))

        # Define a varied color palette
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#9edae5',
            '#393b79', '#637939', '#8c6d31', '#843c39', '#7b4173'
        ]

        if use_index:
            # Plot by match index
            if not self.match_indices:
                print("No match data found to plot.")
                return

            max_index = max(self.match_indices)

            for i, (player, history) in enumerate(self.ratings_history.items()):
                indices = [entry[2] for entry in history]  # Use actual match indices
                ratings = [entry[1] for entry in history]

                if indices:
                    # Use color from palette, cycling if more players than colors
                    color = colors[i % len(colors)]

                    # Plot the main line
                    plt.step(indices, ratings, label=player, linewidth=2, color=color)

                    # Add diamond marker for first game
                    plt.plot(indices[0], ratings[0], marker='D', markersize=8, color=color,
                            markeredgecolor='black', markeredgewidth=1, zorder=5)

                    peak_rating = max(ratings)
                    peak_index_pos = ratings.index(peak_rating)
                    peak_index = indices[peak_index_pos]

                    plt.plot(peak_index, peak_rating, marker='*', markersize=12, color='gold',
                             markeredgecolor='black', markeredgewidth=1, zorder=6)
                    plt.text(peak_index, peak_rating, f'   {peak_rating:.0f}',
                             verticalalignment='center', fontsize=9, color='gold',
                             weight='bold', zorder=7)

                    # Add horizontal line from last game to end of chart
                    last_index = indices[-1]
                    last_rating = ratings[-1]

                    # if last_index < max_index:
                    #     plt.plot([last_index, max_index], [last_rating, last_rating],
                    #             color=color, linestyle='-', linewidth=2)

                    # Add diamond marker at max index with current Elo label
                    plt.plot(last_index, last_rating, marker='D', markersize=8, color=color,
                            markeredgecolor='black', markeredgewidth=1, zorder=5)
                    plt.text(last_index, last_rating, f'   {last_rating:.0f}',
                            verticalalignment='center', fontsize=9, color=color,
                            weight='bold', zorder=6)

            plt.xlabel('Match Index')
            plt.ylabel('Elo Rating')
            plt.title('Ping Pong Elo Ratings by Match Index')

        else:
            # Original date-based plotting
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
                    plt.plot(dates, ratings, marker='o', label=player, linewidth=2, color=color)

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
            plt.xticks(rotation=45)

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')


class DataLoader:
    """Handles loading and parsing match data."""

    @staticmethod
    def load_from_database(
            db_path: str,
            table_name: str = "games",
            season_filter: Optional[int] = None,
            include_archived: bool = True,
            thursday_friday_afternoon_only: bool = False,
            afternoon_start_hour: int = 12
    ) -> List[MatchResult]:
        """Load match results from SQLite database.

        Args:
            db_path: Path to SQLite database
            table_name: Name of the table containing match data
            season_filter: Filter for specific season (None for all seasons)
            include_archived: Whether to include archived matches
            thursday_friday_afternoon_only: If True, only include matches on Thu/Fri afternoons
            afternoon_start_hour: Hour (24-hour format) when afternoon starts (default: 12)
        """
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

            # Convert date column from unix timestamp, handling null values
            df['date_played'] = pd.to_datetime(df['date_played'], unit='s', errors='coerce')

            # Apply Thursday/Friday afternoon filter if requested
            if thursday_friday_afternoon_only:
                # Filter out rows with null dates first
                original_count = len(df)
                df = df.dropna(subset=['date_played'])

                if len(df) < original_count:
                    print(f"Dropped {original_count - len(df)} matches without dates for day/time filtering")

                # Extract day of week (0=Monday, 3=Thursday, 4=Friday) and hour
                df['day_of_week'] = df['date_played'].dt.dayofweek
                df['hour'] = df['date_played'].dt.hour

                # Filter for Thursday (3) or Friday (4) afternoons
                thursday_friday_mask = df['day_of_week'].isin([3, 4])
                afternoon_mask = df['hour'] >= afternoon_start_hour
                df = df[thursday_friday_mask & afternoon_mask]

                # Drop the temporary columns
                df = df.drop(['day_of_week', 'hour'], axis=1)

                print(f"Filtered to {len(df)} matches on Thursday/Friday afternoons")

            # Debug: Print column names if there's an issue
            print(f"Available columns: {list(df.columns)}")

            # Map common column name variations
            column_mapping = {
                'index': ['Index', 'index', 'id', 'ID', 'match_id'],
                'date_played': ['date_played', 'date', 'match_date'],
                'p1': ['p1', 'player1', 'player_1'],
                'p2': ['p2', 'player2', 'player_2'],
                'doubles': ['doubles', 'is_doubles', 'double'],
                'winner': ['winner', 'winning_player'],
                'archived': ['archived', 'is_archived'],
                'season': ['season', 'season_id']
            }

            # Find actual column names
            actual_columns = {}
            for field, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        actual_columns[field] = name
                        break
                if field not in actual_columns:
                    raise ValueError(f"Could not find column for '{field}'. Available columns: {list(df.columns)}")

            matches = []
            for _, row in df.iterrows():
                match = MatchResult(
                    index=int(row[actual_columns['index']]),
                    date_played=row['date_played'] if pd.notna(row['date_played']) else None,
                    p1=str(row[actual_columns['p1']]),
                    p2=str(row[actual_columns['p2']]),
                    doubles=bool(row[actual_columns['doubles']]),
                    winner=str(row[actual_columns['winner']]),
                    archived=bool(row[actual_columns['archived']]),
                    season=int(row[actual_columns['season']])
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
            thursday_friday_afternoon_only: bool = False,
            afternoon_start_hour: int = 12,
            **kwargs
    ) -> None:
        """Load match data from database, file, or DataFrame."""
        if source_type == "database" and isinstance(source, str):
            self.matches = DataLoader.load_from_database(
                source, table_name, season_filter, include_archived,
                thursday_friday_afternoon_only, afternoon_start_hour
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

            print("\n" + "="*60)
            print("DATABASE INFORMATION")
            print("="*60)

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
                print(f"Season {season['season']:2d}: {season['games']:3d} matches "
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

        print("\n" + "="*50)
        print("PING PONG LEAGUE ANALYSIS SUMMARY")
        print("="*50)

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
    elo_calc = EloCalculator(initial_rating=400, k_factor=32.0)
    analyzer.add_calculator(elo_calc)

    network_analyzer = NetworkAnalyzer()
    analyzer.add_calculator(network_analyzer)

    match_counter = MatchCountCalculator()
    analyzer.add_calculator(match_counter)

    # Example usage with your database
    db_path = "../backend/game_database.db"

    try:
        # Print database information
        analyzer.print_database_info(db_path)

        # Load data from database (all seasons, including archived)
        analyzer.load_data(
            db_path,
            source_type="database",
            thursday_friday_afternoon_only=False,
        )

        # Or load specific season only
        # analyzer.load_data(db_path, source_type="database", season_filter=3, include_archived=False)

        # Run analysis
        results = analyzer.run_analysis()

        # Print summary
        analyzer.print_summary()

        match_counter.print_match_counts()

        # Plot Elo ratings over time
        elo_calc.plot_ratings_over_time('elo_ratings_timeline.png')

        network_analyzer.print_network_stats()
        network_analyzer.plot_network('player_network.png', min_matches=1)

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure your database file exists and has the correct table structure.")


if __name__ == "__main__":
    main()
