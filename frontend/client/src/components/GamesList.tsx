import { Link } from "wouter";
import { Game } from "@/lib/api";

interface GamesListProps {
  games: Game[];
  isDetailed?: boolean;
}

export default function GamesList({ games, isDetailed = false }: GamesListProps) {
  // --- FIX IS HERE ---
  const formatDate = (date: number | null) => { // Changed type from string to number
    if (!date) return "No Date"; // Handle null or zero timestamp
    // Multiply by 1000 to convert seconds (from backend) to milliseconds (for JS Date)
    return new Date(date * 1000).toLocaleDateString("en-GB"); // Using en-GB for DD/MM/YYYY format
  };

  // For the detailed view, we need to determine the current player's username
  // We assume all games in the filtered list include the current player
  let currentPlayerUsername = "";
  if (isDetailed && games.length > 0) {
    // Simple approach: check which player appears in all games
    const playerCounts: Record<string, number> = {};

    // Count appearances of each player
    games.forEach(game => {
      game.players.forEach(player => {
        playerCounts[player] = (playerCounts[player] || 0) + 1;
      });
    });

    // Find the player who appears in all or most games
    const totalGames = games.length;
    for (const [player, count] of Object.entries(playerCounts)) {
      if (count >= totalGames * 0.8) { // Player appears in at least 80% of games
        currentPlayerUsername = player;
        break;
      }
    }

    // Fallback: just use the first player from the first game if no common player found
    if (!currentPlayerUsername && games[0]?.players?.length > 0) {
      currentPlayerUsername = games[0].players[0];
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr className="bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
            <th className="px-6 py-3 rounded-tl-lg">Game</th>
            <th className="px-6 py-3">{isDetailed ? "Opponent" : "Players"}</th>
            <th className="px-6 py-3">{isDetailed ? "Result" : "Winner"}</th>
            <th className="px-6 py-3 rounded-tr-lg">Date</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-slate-200">
          {games.map((game) => (
            <tr
              key={game.id}
              className="hover:bg-slate-50 cursor-pointer"
              onClick={() => {/* Will implement game details view in future */ }}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="font-semibold text-slate-700">#{game.id}</span>
              </td>
              {isDetailed ? (
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {game.players.length > 1 && (
                      <>
                        <div className="flex-shrink-0 h-8 w-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-semibold">
                          {game.players.find(p => p !== currentPlayerUsername)?.charAt(0).toUpperCase()}
                        </div>
                        <div className="ml-3 font-medium text-slate-700">
                          {game.players.find(p => p !== currentPlayerUsername)}
                        </div>
                      </>
                    )}
                  </div>
                </td>
              ) : (
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-slate-700">{game.players[0]}</span>
                    <span className="text-slate-400">vs</span>
                    <span className="font-medium text-slate-700">{game.players[1]}</span>
                  </div>
                </td>
              )}
              <td className="px-6 py-4 whitespace-nowrap">
                {/* --- FIX IS HERE (for detailed view result) --- */}
                {isDetailed ? (
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${game.winner === currentPlayerUsername ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                    {game.winner === currentPlayerUsername ? 'Win' : 'Loss'}
                  </span>
                ) : (
                  <span className="text-success font-medium">{game.winner}</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-slate-500">
                {formatDate(game.date)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
