import { Game } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { getInitials } from "@/lib/utils";

interface RecentGamesProps {
  games: Game[] | undefined;
  isLoading: boolean;
}

const RecentGames: React.FC<RecentGamesProps> = ({ games, isLoading }) => {
  return (
    <div>
      <h2 className="text-xl font-bold text-slate-800 mb-4">Recent Games</h2>
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">#</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">Players</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">Winner</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">Date</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                // Loading skeleton rows
                Array(3).fill(0).map((_, i) => (
                  <tr key={i} className="border-b border-slate-100">
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-4" />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Skeleton className="h-8 w-8 rounded-full" />
                        <Skeleton className="h-4 w-4" />
                        <Skeleton className="h-8 w-8 rounded-full" />
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-6 w-16 rounded-full" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-24" />
                    </td>
                  </tr>
                ))
              ) : games && games.length > 0 ? (
                games.map((game, index) => (
                  <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-6 py-4 text-sm text-slate-500">{index + 1}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center text-sm font-semibold">
                          {game.players[0]}
                        </span>
                        <span className="text-sm text-slate-800">vs</span>
                        <span className="inline-flex items-center text-sm font-semibold">
                          {game.players[1]}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {game.winner}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-500">{game.date || "Unknown"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-10 text-center">
                    <i className="fas fa-table-tennis-paddle-ball text-slate-300 text-4xl mb-3"></i>
                    <p className="text-slate-500">No games recorded yet.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RecentGames;
