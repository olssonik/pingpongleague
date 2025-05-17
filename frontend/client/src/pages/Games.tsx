import { usePingPongData } from "@/hooks/usePingPongData";
import RecentGames from "@/components/RecentGames";
import { Skeleton } from "@/components/ui/skeleton";

const Games = () => {
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
        <h1 className="text-2xl font-bold text-slate-800">Games</h1>
        <p className="text-slate-500">View all table tennis matches</p>
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
          <h2 className="text-lg font-semibold mb-4">Games Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Total Games</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.totalGames}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Games This Week</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.gamesThisWeek}</div>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <div className="text-sm text-slate-500 mb-1">Active Players</div>
              <div className="text-2xl font-bold text-slate-800">{data?.stats.activePlayers}</div>
            </div>
          </div>
        </div>
      )}

      <RecentGames
        games={data?.games}
        isLoading={isLoading}
      />
    </>
  );
};

export default Games;