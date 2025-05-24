import { PlayerWithStats } from "@/lib/api";

interface PlayerStatsProps {
  player: PlayerWithStats;
}

export default function PlayerStats({ player }: PlayerStatsProps) {
  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-50 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-primary">{player.wins}</div>
          <div className="text-slate-500 text-sm">Wins</div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-danger">{player.losses}</div>
          <div className="text-slate-500 text-sm">Losses</div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-slate-700">{player.winRate}%</div>
          <div className="text-slate-500 text-sm">Win Rate</div>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-slate-700">{player.gamesPlayed}</div>
          <div className="text-slate-500 text-sm">Games Played</div>
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Performance</h3>
        <div className="h-16 bg-slate-100 rounded-lg overflow-hidden relative">
          <div 
            className="absolute inset-0 bg-primary/20 flex items-center justify-center"
            style={{ width: `${player.winRate}%` }}
          >
            <div className="absolute w-2 h-full bg-primary right-0"></div>
          </div>
          <div className="absolute inset-0 flex items-center justify-center text-primary font-semibold">
            {player.winRate}% Win Rate
          </div>
        </div>
      </div>
    </div>
  );
}
