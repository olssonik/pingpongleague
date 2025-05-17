import { usePingPongData } from "@/hooks/usePingPongData";
import { useRoute } from "wouter";
import { Skeleton } from "@/components/ui/skeleton";
import { getInitials } from "@/lib/utils";
import { Game, PlayerStats } from "@/types";

const PlayerDetail = () => {
  const [, params] = useRoute<{ username: string }>("/player/:username");
  const username = params?.username;
  const { data, isLoading, error } = usePingPongData();

  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl text-red-500 mb-2">Error loading data</h2>
        <p className="text-slate-600">{(error as Error).message}</p>
      </div>
    );
  }

  // Find player and their games
  const player = data?.playerStats.find(p => p.username === username);
  const playerGames = data?.games.filter(game => 
    game.players.includes(username || '')
  );

  return (
    <>
      {isLoading ? (
        <div className="mb-8">
          <Skeleton className="h-10 w-48 mb-2" />
          <Skeleton className="h-6 w-64" />
        </div>
      ) : !player ? (
        <div className="text-center py-12">
          <h2 className="text-xl text-orange-500 mb-2">Player not found</h2>
          <p className="text-slate-600">The player '{username}' does not exist</p>
        </div>
      ) : (
        <>
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-slate-800 mb-2">{player.username}</h1>
            <p className="text-slate-500">Player statistics and game history</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            {/* Player Card */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-md overflow-hidden border-t-4 border-[#22c55e]">
                <div className="p-6">
                  <div className="flex items-center mb-6">
                    <div className="bg-slate-200 h-20 w-20 rounded-full flex items-center justify-center text-slate-600 text-2xl font-bold mr-4">
                      <span>{getInitials(player.username)}</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-800">{player.username}</h3>
                      <p className="text-sm text-slate-500">Joined 2023</p>
                    </div>
                  </div>
                  
                  <div className="mb-6">
                    <div className="text-center p-4 bg-slate-50 rounded-lg mb-4">
                      <div className="text-sm text-slate-500 mb-1">ELO Rating</div>
                      <div className="text-3xl font-bold text-slate-800">{player.elo}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-xs text-green-600 mb-1">Wins</div>
                      <div className="text-xl font-bold text-green-700">{player.wins}</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                      <div className="text-xs text-red-500 mb-1">Losses</div>
                      <div className="text-xl font-bold text-red-600">{player.losses}</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Win Streak</div>
                      <div className="text-lg font-bold text-slate-800">{player.currentStreak}</div>
                    </div>
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Win Rate</div>
                      <div className="text-lg font-bold text-slate-800">{player.winRatio}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Player Games History */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-md overflow-hidden h-full">
                <div className="px-6 py-4 bg-slate-800 text-white">
                  <h2 className="text-lg font-bold">Game History</h2>
                </div>
                <div className="p-4">
                  {playerGames && playerGames.length > 0 ? (
                    <div className="overflow-hidden">
                      <table className="min-w-full">
                        <thead>
                          <tr className="bg-slate-50 border-b border-slate-200">
                            <th className="px-4 py-3 text-left text-sm font-semibold text-slate-500">Opponent</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-slate-500">Result</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-slate-500">Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {playerGames.map((game, index) => {
                            const opponent = game.players.find(p => p !== username) || '';
                            const result = game.winner === username ? 'Win' : 'Loss';
                            
                            return (
                              <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                                <td className="px-4 py-4 text-sm text-slate-700">{opponent}</td>
                                <td className="px-4 py-4">
                                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                                    result === 'Win' 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-red-100 text-red-800'
                                  }`}>
                                    {result}
                                  </span>
                                </td>
                                <td className="px-4 py-4 text-sm text-slate-500">{game.date || 'Unknown'}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500">No games found for this player</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Performance Chart Section - Placeholder */}
          <div className="bg-white rounded-xl shadow-md overflow-hidden mb-8">
            <div className="px-6 py-4 bg-slate-800 text-white">
              <h2 className="text-lg font-bold">Performance Stats</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-500 mb-1">Games Played</div>
                  <div className="text-2xl font-bold text-slate-800">{player.gamesPlayed}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-500 mb-1">Highest Win Streak</div>
                  <div className="text-2xl font-bold text-slate-800">{player.currentStreak}</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg">
                  <div className="text-sm text-slate-500 mb-1">League Position</div>
                  <div className="text-2xl font-bold text-slate-800">
                    #{data?.leaderboard.findIndex(p => p.username === player.username) !== undefined 
                      ? (data?.leaderboard.findIndex(p => p.username === player.username) || 0) + 1 
                      : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default PlayerDetail;