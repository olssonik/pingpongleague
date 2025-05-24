import { useState } from "react";
import { Link } from "wouter";
import { PlayerWithStats } from "@/lib/api";

interface LeaderboardProps {
  players: PlayerWithStats[];
}

type SortOption = "elo" | "winRate" | "gamesPlayed";

export default function Leaderboard({ players }: LeaderboardProps) {
  const [sortBy, setSortBy] = useState<SortOption>("elo");

  const sortedPlayers = [...players].sort((a, b) => {
    switch (sortBy) {
      case "elo":
        return b.elo - a.elo;
      case "winRate":
        return b.winRate - a.winRate;
      case "gamesPlayed":
        return b.gamesPlayed - a.gamesPlayed;
      default:
        return b.elo - a.elo;
    }
  });
function getWinRate(wins: number, losses: number, percentage: boolean = true): string {
  const total = wins + losses;
  if (total === 0) return percentage ? "0.0%" : "0.0";
  const rate = (wins / total) * 100;
  return percentage ? `${rate.toFixed(1)}%` : rate.toFixed(1);
}
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-slate-800"></h2>
        <div>
          <select
            className="text-sm border-slate-300 rounded-md p-1"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
          >
            <option value="elo">Sort by: ELO</option>
            <option value="winRate">Sort by: Win Rate</option>
            <option value="gamesPlayed">Sort by: Games Played</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-slate-50 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
              <th className="px-6 py-3 rounded-tl-lg">Rank</th>
              <th className="px-6 py-3">Player</th>
              <th className="px-6 py-3 text-right">ELO</th>
              <th className="px-6 py-3 text-right">Win/Loss</th>
              <th className="px-6 py-3 text-right">Win Rate</th>
              <th className="px-6 py-3 text-right rounded-tr-lg">Games</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {sortedPlayers.map((player, index) => (
              <tr
                key={player.username}
                className="hover:bg-slate-50 cursor-pointer"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link href={`/players/${player.username}`}>
                    <div className="flex items-center">
                      <span
                        className={`${index < 1 ? "bg-primary" : "bg-slate-500"} text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-semibold`}
                      >
                        {index + 1}
                      </span>
                    </div>
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link href={`/players/${player.username}`}>
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-primary text-white rounded-full flex items-center justify-center text-lg font-semibold">
                        {player.username.charAt(0).toUpperCase()}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-slate-900">
                          {player.username}
                        </div>
                      </div>
                    </div>
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-lg font-mono font-semibold text-primary">
                  {player.elo}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  {player.wins}/{player.losses}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
  {getWinRate(player.wins, player.losses, true)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-slate-700">
                  {player.gamesPlayed}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
