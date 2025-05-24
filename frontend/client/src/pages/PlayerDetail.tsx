import { useQuery } from "@tanstack/react-query";
import { useParams, useLocation } from "wouter";
import { Card } from "@/components/ui/card";
import PlayerProfile from "@/components/PlayerProfile";
import { calculatePlayerStats } from "@/lib/utils";

export default function PlayerDetail() {
  const { username } = useParams();
  const [, setLocation] = useLocation();

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
  
  // Find the selected player
  const player = playersWithStats.find(p => p.username === username);
  
  if (!player) {
    setLocation("/players");
    return null;
  }
  
  // Filter games for the player
  const playerGames = games.filter((game: any) => 
    game.players.includes(player.username)
  );
  
  // Get other players for comparison
  const otherPlayers = playersWithStats.filter(p => p.username !== player.username);

  return (
    <PlayerProfile 
      player={player}
      playerGames={playerGames}
      otherPlayers={otherPlayers}
    />
  );
}
