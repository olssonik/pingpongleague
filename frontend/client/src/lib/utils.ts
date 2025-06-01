import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Player, Game, PlayerWithStats } from "./api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function calculatePlayerStats(players: Player[] | Record<string, Player>, games: Game[]): PlayerWithStats[] {
  // Handle both array and object formats from the backend
  const playersArray = Array.isArray(players) 
    ? players 
    : Object.values(players);
    
  return playersArray.map(player => {
    const playerGames = games.filter(game => game.players.includes(player.username));
    const wins = games.filter(game => game.winner === player.username).length;
    const losses = playerGames.length - wins;
    const winRate = playerGames.length > 0 ? Math.round((wins / playerGames.length) * 100) : 0;

    return {
      ...player,
      wins,
      losses,
      winRate,
      gamesPlayed: playerGames.length,
      rank: 0, // Will be set after sorting
      achievements: player.achievements || [],
    };
  })
  .sort((a, b) => b.elo - a.elo)
  .map((player, index) => ({
    ...player,
    rank: index + 1,
  }));
}

export function getRandomEloChange(): number {
  return Math.floor(Math.random() * 20) + 20; // Random ELO change between 20-39
}
