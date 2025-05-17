import { usePingPongData } from "@/hooks/usePingPongData";
import LeagueStatistics from "@/components/LeagueStatistics";
import Leaderboard from "@/components/Leaderboard";
import PlayerCards from "@/components/PlayerCards";
import RecentGames from "@/components/RecentGames";

const Dashboard = () => {
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
      <LeagueStatistics
        topPlayer={data?.topPlayer}
        stats={data?.stats}
        isLoading={isLoading}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 order-2 lg:order-1">
          <Leaderboard
            leaderboard={data?.leaderboard}
            isLoading={isLoading}
          />
        </div>

        <div className="lg:col-span-2 order-1 lg:order-2">
          <PlayerCards
            playerStats={data?.playerStats}
            isLoading={isLoading}
          />

          <RecentGames
            games={data?.games}
            isLoading={isLoading}
          />
        </div>
      </div>
    </>
  );
};

export default Dashboard;
