import { usePingPongData } from "@/hooks/usePingPongData";
import PlayerCards from "@/components/PlayerCards";
import { Skeleton } from "@/components/ui/skeleton";

const Players = () => {
  const { data, isLoading, error } = usePingPongData();

  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl text-red-500 mb-2">Error loading data</h2>
        <p className="text-slate-600">{(error as Error).message}</p>
      </div>
    );
  }

  return (
    <>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Players</h1>
        <p className="text-slate-500">View all players and their stats</p>
      </div>
      
      {isLoading ? (
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <Skeleton className="h-8 w-48 mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-16 rounded-lg" />
            <Skeleton className="h-16 rounded-lg" />
            <Skeleton className="h-16 rounded-lg" />
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">League Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Total Players</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.totalPlayers}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Avg. ELO</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.avgElo}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Highest Win Streak</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.highestStreak}</div>
            </div>
          </div>
        </div>
      )}

      <PlayerCards
        playerStats={data?.playerStats}
        isLoading={isLoading}
      />
    </>
  );
};

export default Players;