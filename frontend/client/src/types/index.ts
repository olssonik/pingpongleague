export interface Player {
  username: string;
  elo: number;
}

export interface Game {
  players: string[];
  winner: string;
  date?: string;
}

export interface PlayerStats extends Player {
  gamesPlayed: number;
  wins: number;
  losses: number;
  currentStreak: number;
  winRatio: number;
}

export interface LeagueStats {
  totalPlayers: number;
  totalGames: number;
  avgElo: number;
  highestStreak: number;
  gamesThisWeek: number;
  activePlayers: number;
}

export interface PingPongData {
  players: Player[];
  games: Game[];
  playerStats: PlayerStats[];
  leaderboard: Player[];
  topPlayer: Player;
  stats: LeagueStats;
}

export interface ApiResponse {
  players: Player[];
  games: Game[];
}
