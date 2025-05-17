import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { ApiResponse, Game, Player, PlayerStats, LeagueStats, PingPongData } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getInitials(name: string): string {
  return name.charAt(0).toUpperCase();
}

export function calculatePlayerStats(data: ApiResponse): PingPongData {
  const { players, games } = data;

  // Calculate additional player stats
  const playerStats = players.map(player => {
    const gamesPlayed = games.filter(game => 
      game.players.includes(player.username)
    );
    
    const wins = gamesPlayed.filter(game => 
      game.winner === player.username
    ).length;
    
    const losses = gamesPlayed.length - wins;
    
    // Calculate win streak
    let currentStreak = 0;
    const playerGames = [...gamesPlayed].sort((a, b) => {
      if (!a.date || !b.date) return 0;
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    });
    
    for (const game of playerGames) {
      if (game.winner === player.username) {
        currentStreak++;
      } else {
        break;
      }
    }
    
    const winRatio = gamesPlayed.length > 0 
      ? Math.round((wins / gamesPlayed.length) * 100) 
      : 0;
    
    return {
      ...player,
      gamesPlayed: gamesPlayed.length,
      wins,
      losses,
      currentStreak,
      winRatio
    };
  });

  // Sort leaderboard by ELO
  const leaderboard = [...players].sort((a, b) => b.elo - a.elo);
  
  // Get top player
  const topPlayer = leaderboard[0];
  
  // Calculate overall stats
  const stats: LeagueStats = {
    totalPlayers: players.length,
    totalGames: games.length,
    avgElo: Math.round(players.reduce((sum, player) => sum + player.elo, 0) / players.length),
    highestStreak: Math.max(...playerStats.map(player => player.currentStreak)),
    gamesThisWeek: games.length, // Simplified for mock
    activePlayers: players.length // Simplified for mock
  };

  return {
    players,
    games,
    playerStats,
    leaderboard,
    topPlayer,
    stats
  };
}
