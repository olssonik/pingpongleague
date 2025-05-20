import { useState } from "react";
import { Game } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";

interface RecentGamesProps {
  games: Game[] | undefined;
  isLoading: boolean;
}

const RecentGames: React.FC<RecentGamesProps> = ({ games, isLoading }) => {
  const [newGames, setNewGames] = useState([
    { p1: "", p2: "", winner: "", doubles: false },
  ]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState({
    p1: "",
    p2: "",
    winner: "",
    doubles: false,
  });

  const handleRowChange = (index: number, field: string, value: string | boolean) => {
    const updated = [...newGames];
    updated[index] = { ...updated[index], [field]: value };
    setNewGames(updated);
  };

  const addRow = () => {
    setNewGames([...newGames, { p1: "", p2: "", winner: "", doubles: false }]);
  };

  const removeRow = (index: number) => {
    const updated = [...newGames];
    updated.splice(index, 1);
    setNewGames(updated);
  };

  const handleAddGames = (e: React.FormEvent) => {
    e.preventDefault();
    const mockGames: Game[] = newGames.map((row, idx) => ({
      id: Math.floor(Math.random() * 10000) + idx,
      players: [row.p1, row.p2],
      winner: row.winner,
      doubles: row.doubles ? 1 : 0,
      date: Date.now(),
    }));
    console.log("Mock batch of new games:", mockGames);
  };

  const handleDeleteClick = (id: number) => {
    console.log("Delete game with ID:", id);
  };

  const handleEditClick = (game: Game) => {
    setEditingId(game.id);
    setEditData({
      p1: game.players[0],
      p2: game.players[1],
      winner: game.winner,
      doubles: game.doubles === 1,
    });
  };

  const handleEditChange = (field: string, value: string | boolean) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  const handleEditSave = () => {
    if (editingId === null) return;
    const updatedGame: Game = {
      id: editingId,
      players: [editData.p1, editData.p2],
      winner: editData.winner,
      doubles: editData.doubles ? 1 : 0,
      date: Date.now(),
    };
    console.log("Updated game:", updatedGame);
    setEditingId(null);
  };

  return (
    <div>
      {/* Add Multiple Games */}
      <form
        onSubmit={handleAddGames}
        className="mb-6 p-4 bg-white rounded-xl shadow-md"
      >
        <table className="w-full text-sm mb-4">
          <thead>
            <tr>
              <th className="px-2 py-2">Player 1</th>
              <th className="px-2 py-2">Player 2</th>
              <th className="px-2 py-2">Winner</th>
              <th className="px-2 py-2">Doubles?</th>
              <th className="px-2 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {newGames.map((row, index) => (
              <tr key={index}>
                <td className="px-2 py-1">
                  <input
                    value={row.p1}
                    required
                    onChange={(e) =>
                      handleRowChange(index, "p1", e.target.value)
                    }
                    className="border px-2 py-1 rounded w-full"
                  />
                </td>
                <td className="px-2 py-1">
                  <input
                    value={row.p2}
                    required
                    onChange={(e) =>
                      handleRowChange(index, "p2", e.target.value)
                    }
                    className="border px-2 py-1 rounded w-full"
                  />
                </td>
                <td className="px-2 py-1">
                  <input
                    value={row.winner}
                    required
                    onChange={(e) =>
                      handleRowChange(index, "winner", e.target.value)
                    }
                    className="border px-2 py-1 rounded w-full"
                  />
                </td>
                <td className="px-2 py-1 text-center">
                  <input
                    type="checkbox"
                    checked={row.doubles}
                    onChange={(e) =>
                      handleRowChange(index, "doubles", e.target.checked)
                    }
                  />
                </td>
                <td className="px-2 py-1 text-center">
                  <button
                    type="button"
                    onClick={() => removeRow(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ❌
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex justify-between">
          <button
            type="button"
            onClick={addRow}
            className="bg-gray-200 text-sm px-3 py-1 rounded hover:bg-gray-300"
          >
            + Add Row
          </button>
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Submit Games
          </button>
        </div>
      </form>

      {/* Recent Games Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">
                  #
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">
                  Players
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">
                  Winner
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-500">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array(3)
                  .fill(0)
                  .map((_, i) => (
                    <tr key={i} className="border-b border-slate-100">
                      <td className="px-6 py-4">
                        <Skeleton className="h-4 w-4" />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-2">
                          <Skeleton className="h-8 w-8 rounded-full" />
                          <Skeleton className="h-4 w-4" />
                          <Skeleton className="h-8 w-8 rounded-full" />
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Skeleton className="h-6 w-16 rounded-full" />
                      </td>
                      <td className="px-6 py-4">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      <td className="px-6 py-4">
                        <Skeleton className="h-4 w-4" />
                      </td>
                    </tr>
                  ))
              ) : games && games.length > 0 ? (
                [...games]
                  .sort((a, b) => b.id - a.id)
                  .map((game, index) => (
                    <tr
                      key={game.id}
                      className="border-b border-slate-100 hover:bg-slate-50"
                    >
                      <td className="px-6 py-4 text-sm text-slate-500">
                        {game.id}
                      </td>
                      <td className="px-6 py-4">
                        {editingId === game.id ? (
                          <div className="flex items-center space-x-2">
                            <input
                              value={editData.p1}
                              onChange={(e) =>
                                handleEditChange("p1", e.target.value)
                              }
                              className="border px-2 py-1 rounded w-20"
                            />
                            <span className="text-sm text-slate-800">vs</span>
                            <input
                              value={editData.p2}
                              onChange={(e) =>
                                handleEditChange("p2", e.target.value)
                              }
                              className="border px-2 py-1 rounded w-20"
                            />
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2">
                            <span className="inline-flex items-center text-sm font-semibold">
                              {game.players[0]}
                            </span>
                            <span className="text-sm text-slate-800">vs</span>
                            <span className="inline-flex items-center text-sm font-semibold">
                              {game.players[1]}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {editingId === game.id ? (
                          <input
                            value={editData.winner}
                            onChange={(e) =>
                              handleEditChange("winner", e.target.value)
                            }
                            className="border px-2 py-1 rounded"
                          />
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {game.winner}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-500">
                        {game.date || "Unknown"}
                      </td>
                      <td className="px-6 py-4 text-sm space-x-2">
                        {editingId === game.id ? (
                          <button
                            className="text-green-600 hover:text-green-800"
                            onClick={handleEditSave}
                          >
                            ✅
                          </button>
                        ) : (
                          <button
                            className="text-blue-500 hover:text-blue-700"
                            onClick={() => handleEditClick(game)}
                          >
                            ✏️
                          </button>
                        )}
                        <button
                          className="text-red-500 hover:text-red-700"
                          onClick={() => handleDeleteClick(game.id)}
                        >
                          ❌
                        </button>
                      </td>
                    </tr>
                  ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-10 text-center">
                    <i className="fas fa-table-tennis-paddle-ball text-slate-300 text-4xl mb-3"></i>
                    <p className="text-slate-500">No games recorded yet.</p>
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

export default RecentGames;
