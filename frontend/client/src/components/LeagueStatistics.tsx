import { LeagueStats, Player } from "@/types";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface LeagueStatisticsProps {
  topPlayer: Player | undefined;
  stats: LeagueStats | undefined;
  isLoading: boolean;
}

const LeagueStatistics: React.FC<LeagueStatisticsProps> = ({
  topPlayer,
  stats,
  isLoading
}) => {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden mb-8">
      <div className="px-6 py-4 bg-slate-800 text-white">
        <h2 className="text-xl font-bold">League Statistics</h2>
      </div>
      <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Top Player Card */}
        <div className="col-span-1 md:col-span-1 bg-gradient-to-br from-[#f97316] to-amber-400 rounded-lg shadow p-6 text-white">
          <div className="text-center">
            <h3 className="text-lg font-semibold mb-2">Top Player</h3>
            <div className="h-24 w-24 bg-white rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-[#f97316] text-3xl font-bold">
                <i className="fas fa-crown"></i>
              </span>
            </div>
            {isLoading ? (
              <>
                <Skeleton className="h-8 w-32 mx-auto mb-1 bg-white/20" />
                <Skeleton className="h-5 w-24 mx-auto bg-white/20" />
              </>
            ) : (
              <>
                <h4 className="text-2xl font-bold mb-1">{topPlayer?.username}</h4>
                <div className="text-white/90 text-sm">
                  ELO Rating: <span className="font-semibold">{topPlayer?.elo}</span>
                </div>
              </>
            )}
          </div>
        </div>
        
        {/* League Stats */}
        <div className="col-span-1 md:col-span-2 grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatCard 
            title="Total Players" 
            value={stats?.totalPlayers} 
            isLoading={isLoading} 
          />
          <StatCard 
            title="Total Games" 
            value={stats?.totalGames} 
            isLoading={isLoading} 
          />
          <StatCard 
            title="Avg. ELO" 
            value={stats?.avgElo} 
            isLoading={isLoading} 
          />
          <StatCard 
            title="Highest Win Streak" 
            value={stats?.highestStreak} 
            isLoading={isLoading} 
          />
          <StatCard 
            title="Games This Week" 
            value={stats?.gamesThisWeek} 
            isLoading={isLoading} 
          />
          <StatCard 
            title="Active Players" 
            value={stats?.activePlayers} 
            isLoading={isLoading} 
          />
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: number | undefined;
  isLoading: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, isLoading }) => {
  return (
    <div className="bg-slate-50 p-4 rounded-lg shadow">
      <div className="text-sm text-slate-500 mb-1">{title}</div>
      {isLoading ? (
        <Skeleton className="h-8 w-12 bg-slate-200" />
      ) : (
        <div className="text-2xl font-bold text-slate-800">{value}</div>
      )}
    </div>
  );
};

export default LeagueStatistics;
