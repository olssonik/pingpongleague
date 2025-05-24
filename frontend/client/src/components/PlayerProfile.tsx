import { useState, useEffect } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PlayerWithStats, Game } from "@/lib/api";
import PlayerStats from "./PlayerStats";
import GamesList from "./GamesList";

interface PlayerProfileProps {
  player: PlayerWithStats;
  playerGames: Game[];
  otherPlayers: PlayerWithStats[];
}

export default function PlayerProfile({ player, playerGames, otherPlayers }: PlayerProfileProps) {
  const [compareUsername, setCompareUsername] = useState<string>("");
  const [headToHead, setHeadToHead] = useState<{ player1Wins: number; player2Wins: number }>({ player1Wins: 0, player2Wins: 0 });
  const comparePlayer = otherPlayers.find(p => p.username === compareUsername);

  const filterGames = (games: Game[], username: string) => {
    return games.filter(game => game.players.includes(username));
  };
  
  // Calculate head-to-head stats when a player is selected for comparison
  useEffect(() => {
    if (comparePlayer) {
      // Find games where both players participated
      const matchups = playerGames.filter(game => 
        game.players.includes(player.username) && 
        game.players.includes(comparePlayer.username)
      );
      
      // Count wins for each player
      const player1Wins = matchups.filter(game => game.winner === player.username).length;
      const player2Wins = matchups.filter(game => game.winner === comparePlayer.username).length;
      
      setHeadToHead({ player1Wins, player2Wins });
    }
  }, [compareUsername, player, comparePlayer, playerGames]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6">
        <div className="flex items-center mb-4 md:mb-0">
          <div className="bg-primary text-white rounded-full w-16 h-16 flex items-center justify-center text-2xl font-semibold mr-4">
            {player.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-800">{player.username}</h2>
            <div className="text-slate-500">
              Rank #{player.rank} • ELO: <span className="font-mono font-semibold text-primary">{player.elo}</span>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Select value={compareUsername} onValueChange={setCompareUsername}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Compare with..." />
            </SelectTrigger>
            <SelectContent>
              {otherPlayers.map(p => (
                <SelectItem key={p.username} value={p.username}>
                  {p.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <PlayerStats player={player} />
          
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Match History</h3>
            <GamesList games={filterGames(playerGames, player.username)} isDetailed={true} />
          </div>
        </div>

        {comparePlayer && (
          <div className="bg-slate-50 p-6 rounded-lg border border-slate-200">
            <div className="flex items-center mb-4">
              <div className="bg-primary text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-semibold mr-3">
                {comparePlayer.username.charAt(0).toUpperCase()}
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">{comparePlayer.username}</h3>
                <div className="text-slate-500">
                  Rank #{comparePlayer.rank} • ELO: <span className="font-mono font-semibold text-primary">{comparePlayer.elo}</span>
                </div>
              </div>
            </div>
            
            <PlayerStats player={comparePlayer} />
            
            <div className="mt-6 p-4 bg-white rounded-lg border border-slate-200">
              <h4 className="text-md font-semibold text-slate-800 mb-2">Head-to-Head</h4>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-primary">{player.username}</div>
                  <div className="text-3xl font-bold mt-2">{headToHead.player1Wins}</div>
                  <div className="text-sm text-slate-500">Wins</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-primary">{comparePlayer.username}</div>
                  <div className="text-3xl font-bold mt-2">{headToHead.player2Wins}</div>
                  <div className="text-sm text-slate-500">Wins</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
