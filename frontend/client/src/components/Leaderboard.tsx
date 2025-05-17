import { Player } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { getInitials } from "@/lib/utils";

interface LeaderboardProps {
  leaderboard: Player[] | undefined;
  isLoading: boolean;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ leaderboard, isLoading }) => {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden h-full">
      <div className="px-6 py-4 bg-slate-800 text-white">
        <h2 className="text-xl font-bold">Leaderboard</h2>
      </div>
      <div className="p-4">
        <div className="overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-slate-500">Rank</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-slate-500">Player</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-slate-500">ELO</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                // Loading skeleton rows
                Array(3).fill(0).map((_, i) => (
                  <tr key={i} className="border-b border-slate-100">
                    <td className="px-4 py-4">
                      <div className="flex items-center">
                        <Skeleton className="w-6 h-6 rounded-full" />
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <Skeleton className="h-4 w-16" />
                    </td>
                    <td className="px-4 py-4 text-right">
                      <Skeleton className="h-4 w-10 ml-auto" />
                    </td>
                  </tr>
                ))
              ) : leaderboard && leaderboard.length > 0 ? (
                leaderboard.map((player, index) => (
                  <tr key={player.username} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-4 text-sm font-medium text-slate-700">
                      <div className="flex items-center">
                        <span className={`w-6 h-6 rounded-full ${
                          index === 0 
                            ? "bg-[#22c55e]" 
                            : "bg-slate-400"
                        } text-white flex items-center justify-center text-xs font-bold`}>
                          {index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-sm text-slate-700">{player.username}</td>
                    <td className="px-4 py-4 text-sm font-semibold text-right">{player.elo}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-4 py-4 text-center text-sm text-slate-500">
                    No players found
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

export default Leaderboard;
