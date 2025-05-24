import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import PlayerCard from "@/components/PlayerCard";
import { calculatePlayerStats } from "@/lib/utils";

type SortOption = "elo" | "winRate" | "gamesPlayed" | "alphabetical";

export default function Players() {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("elo");

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
  
  // Filter players based on search term
  const filteredPlayers = playersWithStats.filter(player => 
    player.username.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Sort players based on selected option
  const sortedPlayers = [...filteredPlayers].sort((a, b) => {
    switch (sortBy) {
      case "elo":
        return b.elo - a.elo;
      case "winRate":
        return b.winRate - a.winRate;
      case "gamesPlayed":
        return b.gamesPlayed - a.gamesPlayed;
      case "alphabetical":
        return a.username.localeCompare(b.username);
      default:
        return b.elo - a.elo;
    }
  });

  return (
    <div>
      <Card className="mb-8">
        <CardContent className="p-6">
          <h1 className="text-2xl font-bold text-slate-800 mb-6">Players</h1>
          
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-grow">
              <Input
                placeholder="Search players..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <div>
              <Select value={sortBy} onValueChange={(value: string) => setSortBy(value as SortOption)}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="elo">Sort by ELO</SelectItem>
                  <SelectItem value="winRate">Sort by Win Rate</SelectItem>
                  <SelectItem value="gamesPlayed">Sort by Games Played</SelectItem>
                  <SelectItem value="alphabetical">Sort Alphabetically</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedPlayers.map((player, index) => (
              <PlayerCard
                key={player.username}
                player={player}
                rank={playersWithStats.findIndex(p => p.username === player.username) + 1}
                wins={player.wins}
                losses={player.losses}
                games={player.gamesPlayed}
              />
            ))}
          </div>
          
          {filteredPlayers.length === 0 && (
            <div className="text-center py-8 text-slate-500">
              No players found matching "{searchTerm}"
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
