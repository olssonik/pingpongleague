// API interfaces for type safety

export interface Player {
  username: string;
  elo: number;
}

export interface Game {
  id: number;
  players: string[];
  winner: string;
  date: string | null;
}

export interface PlayerWithStats extends Player {
  wins: number;
  losses: number;
  winRate: number;
  gamesPlayed: number;
  rank: number;
}

export interface APIResponse {
  games: Game[];
  players: Player[];
}

export const fetchData = async (): Promise<APIResponse> => {
  const response = await fetch("/api/get_data");
  if (!response.ok) {
    throw new Error("Failed to fetch data");
  }
  return response.json();
};
