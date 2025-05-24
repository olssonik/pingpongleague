import { useState } from "react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import PlayerCard from "@/components/PlayerCard";
import GamesList from "@/components/GamesList";
import Leaderboard from "@/components/Leaderboard";
import Pagination from "@/components/Pagination";
import { Card } from "@/components/ui/card";
import { calculatePlayerStats } from "@/lib/utils";

export default function Dashboard() {
  const [gamesPage, setGamesPage] = useState(1);
  const gamesPerPage = 5;

  const { data, isLoading, error } = useQuery({
    queryKey: ["/api/get_data"],
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-pulse text-primary text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center text-danger">
          <h2 className="text-xl font-bold mb-2">Error Loading Data</h2>
          <p>Could not load data from server. Please try again later.</p>
        </div>
      </Card>
    );
  }

  const { games, players } = data;
  
  // Process players data to include wins, losses, etc.
  const playersWithStats = calculatePlayerStats(players, games);
  
  // Sort players by ELO for the leaderboard
  const sortedPlayers = [...playersWithStats].sort((a, b) => b.elo - a.elo);
  
  // Get top 3 players for the sidebar
  const topPlayers = sortedPlayers.slice(0, 3);
  
  // Get recent games for the dashboard
  const recentGames = [...games].sort((a, b) => {
    const idA = typeof a.id === 'number' ? a.id : parseInt(a.id);
    const idB = typeof b.id === 'number' ? b.id : parseInt(b.id);
    return idB - idA;
  }).slice(0, 5);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Left Column - Top Players */}
      <div className="lg:col-span-1 order-2 lg:order-1">
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-slate-800">Top Players</h2>
            <Link href="/players">
              <a className="text-primary text-sm font-medium hover:underline">
                View All
              </a>
            </Link>
          </div>

          {topPlayers.map((player, index) => (
            <PlayerCard
              key={player.username}
              player={player}
              rank={index + 1}
              wins={player.wins}
              losses={player.losses}
              games={player.gamesPlayed}
            />
          ))}
        </div>
        
        {/* Recent Games - Moved to bottom on larger screens */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-slate-800">Recent Games</h2>
            <Link href="/games">
              <a className="text-primary text-sm font-medium hover:underline">
                View All Games
              </a>
            </Link>
          </div>

          <GamesList games={recentGames} />
        </div>
      </div>

      {/* Right Column - Leaderboard (now more prominent) */}
      <div className="lg:col-span-2 order-1 lg:order-2">
        {/* Leaderboard - Moved to top and made larger */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-slate-800">Leaderboard</h2>
            <div className="text-slate-600 text-sm">
              Player rankings based on performance
            </div>
          </div>
          <Leaderboard players={playersWithStats} />
        </div>
      </div>
    </div>
  );
}
