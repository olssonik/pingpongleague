import { Link } from "wouter";
import { Player } from "@/lib/api";
import PlayerBadges from "./PlayerBadges";

interface PlayerCardProps {
  player: Player;
  rank: number;
  wins: number;
  losses: number;
  games: number;
}

export default function PlayerCard({ player, rank, wins, losses, games }: PlayerCardProps) {
  const winRate = games > 0 ? Math.round((wins / games) * 100) : 0;
  const initial = player.username.charAt(0).toUpperCase();

  return (
    <Link href={`/players/${player.username}`}>
      <div className="bg-slate-50 rounded-lg p-4 mb-4 border border-slate-200 hover:shadow-md transition-shadow hover-scale cursor-pointer">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="bg-primary text-white rounded-full w-10 h-10 flex items-center justify-center text-lg font-semibold">
              {initial}
            </div>
            <div className="ml-3">
              <h3 className="font-semibold text-slate-800">{player.username}</h3>
              <div className="text-xs text-slate-500">Rank #{rank}</div>
              <div className="mt-1">
                <PlayerBadges achievements={player.achievements || []} size="small" maxDisplay={2} />
              </div>
            </div>
          </div>
          <div className="text-2xl font-mono font-bold text-primary">{player.elo}</div>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <div className="bg-slate-100 p-2 rounded">
            <div className="text-xs text-slate-500">Win/Loss</div>
            <div className="font-medium">{wins}/{losses}</div>
          </div>
          <div className="bg-slate-100 p-2 rounded">
            <div className="text-xs text-slate-500">Win Rate</div>
            <div className="font-medium">{winRate}%</div>
          </div>
          <div className="bg-slate-100 p-2 rounded">
            <div className="text-xs text-slate-500">Games</div>
            <div className="font-medium">{games}</div>
          </div>
        </div>
      </div>
    </Link>
  );
}
