import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import Pagination from "@/components/Pagination";
import { Game } from "@/lib/api";

export default function Games() {
  const [searchTerm, setSearchTerm] = useState("");
  const [playerFilter, setPlayerFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState<"latest" | "oldest">("latest");
  const [currentPage, setCurrentPage] = useState(1);
  const gamesPerPage = 10;

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
  const playersArray = Array.isArray(players) ? players : Object.values(players);

  // Filter games based on search term and player filter
  const filteredGames = games.filter((game: Game) => {
    const matchesSearch =
      game.id.toString().includes(searchTerm) ||
      game.players.some(player => player.toLowerCase().includes(searchTerm.toLowerCase())) ||
      game.winner.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesPlayer = playerFilter === "all" ||
      game.players.includes(playerFilter);

    return matchesSearch && matchesPlayer;
  });

  // Sort games based on selected option
  const sortedGames = [...filteredGames].sort((a: Game, b: Game) => {
    const idA = typeof a.id === 'number' ? a.id : parseInt(a.id);
    const idB = typeof b.id === 'number' ? b.id : parseInt(b.id);
    return sortOrder === "latest" ? idB - idA : idA - idB;
  });

  // Paginate games
  const indexOfLastGame = currentPage * gamesPerPage;
  const indexOfFirstGame = indexOfLastGame - gamesPerPage;
  const currentGames = sortedGames.slice(indexOfFirstGame, indexOfLastGame);

  // Format date for display
  const formatDate = (date: string | null) => {
    if (!date) return "None";
    return new Date(date).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <h2 className="text-xl font-semibold text-slate-800 mb-4 md:mb-0">All Games</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            type="text"
            placeholder="Search games"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full md:w-auto"
          />
          <Select value={playerFilter} onValueChange={setPlayerFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Players" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Players</SelectItem>
              {playersArray.map((player: any) => (
                <SelectItem key={player.username} value={player.username}>
                  {player.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sortOrder} onValueChange={(value: string) => setSortOrder(value as "latest" | "oldest")}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Sort Order" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="latest">Latest First</SelectItem>
              <SelectItem value="oldest">Oldest First</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              <th className="px-6 py-3 rounded-tl-lg">Game ID</th>
              <th className="px-6 py-3">Players</th>
              <th className="px-6 py-3">Winner</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {currentGames.map((game: Game) => (
              <tr key={game.id} className="hover:bg-slate-50 cursor-pointer">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-semibold text-slate-700">#{game.id}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        {game.players[0].charAt(0).toUpperCase()}
                      </div>
                      <div className="ml-2 font-medium text-slate-700">{game.players[0]}</div>
                    </div>
                    <span className="text-slate-400">vs</span>
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-8 w-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        {game.players[1].charAt(0).toUpperCase()}
                      </div>
                      <div className="ml-2 font-medium text-slate-700">{game.players[1]}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-success font-medium">{game.winner}</span>
                </td>

              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredGames.length === 0 && (
        <div className="text-center py-8 text-slate-500">
          No games found matching your criteria.
        </div>
      )}

      {filteredGames.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={Math.ceil(filteredGames.length / gamesPerPage)}
          onPageChange={setCurrentPage}
        />
      )}
    </div>
  );
}
