import { PlayerStats } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";
import { getInitials } from "@/lib/utils";
import { Link } from "wouter";

interface PlayerCardsProps {
  playerStats: PlayerStats[] | undefined;
  isLoading: boolean;
}

const PlayerCards: React.FC<PlayerCardsProps> = ({ playerStats, isLoading }) => {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Player Cards</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {isLoading ? (
          // Loading skeleton
          Array(2).fill(0).map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-md overflow-hidden border-t-4 border-slate-300">
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <Skeleton className="h-14 w-14 rounded-full mr-4" />
                  <div>
                    <Skeleton className="h-5 w-20 mb-1" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <Skeleton className="h-16 rounded-lg" />
                  <Skeleton className="h-16 rounded-lg" />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Skeleton className="h-10 w-10 mr-4" />
                    <Skeleton className="h-10 w-10" />
                  </div>
                  <Skeleton className="h-10 w-16" />
                </div>
              </div>
            </div>
          ))
        ) : playerStats && playerStats.length > 0 ? (
          playerStats.map((player, index) => (
            <Link key={player.username} href={`/player/${player.username}`}>
              <div 
                className={`bg-white rounded-xl shadow-md overflow-hidden border-t-4 ${
                  index % 2 === 0 ? "border-[#22c55e]" : "border-[#f97316]"
                } cursor-pointer transition-transform hover:translate-y-[-4px] hover:shadow-lg`}
              >
                <div className="p-6">
                  <div className="flex items-center mb-4">
                    <div className="bg-slate-200 h-14 w-14 rounded-full flex items-center justify-center text-slate-600 text-xl font-bold mr-4">
                      <span>{getInitials(player.username)}</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-slate-800">{player.username}</h3>
                      <p className="text-sm text-slate-500">Joined 2023</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-2 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">ELO Rating</div>
                      <div className="text-lg font-bold text-slate-800">{player.elo}</div>
                    </div>
                    <div className="text-center p-2 bg-slate-50 rounded-lg">
                      <div className="text-xs text-slate-500 mb-1">Win Streak</div>
                      <div className="text-lg font-bold text-slate-800">{player.currentStreak}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex flex-col items-center mr-4">
                        <span className="text-sm font-semibold text-green-600">{player.wins}</span>
                        <span className="text-xs text-slate-500">Wins</span>
                      </div>
                      <div className="flex flex-col items-center">
                        <span className="text-sm font-semibold text-red-500">{player.losses}</span>
                        <span className="text-xs text-slate-500">Losses</span>
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-xs text-slate-500 mb-1">W/L Ratio</div>
                      <div className="text-sm font-bold text-slate-800">{player.winRatio}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))
        ) : (
          <div className="col-span-full text-center p-8 bg-white rounded-xl shadow">
            <p className="text-slate-500">No players found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerCards;
