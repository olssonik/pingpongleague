import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Ensure this file contains all necessary styles, including modal styles

const API_URL = "http://localhost:3000";

// --- Edit Modal Component ---
const GameEditModal = ({ game, players, onClose, onSave, isApiInProgress }) => {
  // Added isApiInProgress prop
  // State for the form fields within the modal, initialized with the game being edited
  const [updatedP1, setUpdatedP1] = useState(game.players[0]);
  const [updatedP2, setUpdatedP2] = useState(game.players[1]);
  const [updatedWinner, setUpdatedWinner] = useState(game.winner);
  const [updatedSeason, setUpdatedSeason] = useState(String(game.season || "")); // Ensure season is a string for input

  useEffect(() => {
    // Update modal form if the game prop changes
    setUpdatedP1(game.players[0]);
    setUpdatedP2(game.players[1]);
    setUpdatedWinner(game.winner);
    setUpdatedSeason(String(game.season || ""));
  }, [game]);

  const handleSave = (e) => {
    e.preventDefault();
    if (!updatedP1 || !updatedP2 || !updatedWinner || !updatedSeason) {
      alert("All fields (Player 1, Player 2, Winner, Season) are required.");
      return;
    }
    if (updatedP1 === updatedP2) {
      alert("Player 1 and Player 2 cannot be the same.");
      return;
    }
    if (updatedWinner !== updatedP1 && updatedWinner !== updatedP2) {
      alert("Winner must be either Player 1 or Player 2.");
      return;
    }
    const seasonNumber = parseInt(updatedSeason, 10);
    if (isNaN(seasonNumber) || seasonNumber <= 0) {
      alert("Please enter a valid positive number for the season.");
      return;
    }

    onSave({
      id: game.id,
      p1: updatedP1,
      p2: updatedP2,
      winner: updatedWinner,
      season: seasonNumber,
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Edit Game #{game.id}</h2>
        <form onSubmit={handleSave}>
          <div className="form-group">
            <label htmlFor={`edit-p1-${game.id}`}>Player 1</label>
            <select
              id={`edit-p1-${game.id}`}
              value={updatedP1}
              onChange={(e) => setUpdatedP1(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Player 1</option>
              {players.map((p) => (
                <option
                  key={`${p.username}-edit-p1-${game.id}`}
                  value={p.username}
                >
                  {p.username}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor={`edit-p2-${game.id}`}>Player 2</label>
            <select
              id={`edit-p2-${game.id}`}
              value={updatedP2}
              onChange={(e) => setUpdatedP2(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Player 2</option>
              {players.map((p) => (
                <option
                  key={`${p.username}-edit-p2-${game.id}`}
                  value={p.username}
                >
                  {p.username}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor={`edit-winner-${game.id}`}>Winner</label>
            <select
              id={`edit-winner-${game.id}`}
              value={updatedWinner}
              onChange={(e) => setUpdatedWinner(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Winner</option>
              {[updatedP1, updatedP2].filter(Boolean).map((pName) => (
                <option key={`${pName}-edit-winner-${game.id}`} value={pName}>
                  {pName}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor={`edit-season-${game.id}`}>Season</label>
            <input
              id={`edit-season-${game.id}`}
              type="number"
              value={updatedSeason}
              onChange={(e) => setUpdatedSeason(e.target.value)}
              placeholder="Enter season number"
              required
              min="1"
              disabled={isApiInProgress}
            />
          </div>
          <div className="modal-actions">
            <button
              type="submit"
              className="save-button"
              disabled={isApiInProgress}
            >
              {isApiInProgress ? "Saving..." : "Save Changes"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="cancel-button"
              disabled={isApiInProgress}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Main Admin Page Component ---
function AdminPage() {
  const [players, setPlayers] = useState([]);
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true); // For initial data load
  const [isApiInProgress, setIsApiInProgress] = useState(false); // NEW: For disabling buttons during API calls

  // State for multi-game queue
  const [stagedGames, setStagedGames] = useState([]);
  const [p1, setP1] = useState("");
  const [p2, setP2] = useState("");
  const [winner, setWinner] = useState("");
  const [gameSeason, setGameSeason] = useState("2");
  const [useCurrentTimeForBatch, setUseCurrentTimeForBatch] = useState(true);

  // State for "Add Player" form
  const [newUsername, setNewUsername] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newAchievements, setNewAchievements] = useState("");
  const [newPlayerElo, setNewPlayerElo] = useState("400");

  // State for Edit Modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [gameToEdit, setGameToEdit] = useState(null);

  const fetchData = async () => {
    setLoading(true); // This is for the initial page load or full refresh
    // setIsApiInProgress(true); // Not for fetchData, as it's a GET and might run in background
    try {
      const response = await axios.get(`${API_URL}/get_data`);
      setPlayers(response.data.players || []);
      setGames((response.data.games || []).sort((a, b) => b.id - a.id));
    } catch (error) {
      console.error("Error fetching data:", error);
      alert("Could not fetch data from the server.");
    } finally {
      setLoading(false);
      // setIsApiInProgress(false); // Not for fetchData
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // --- Edit Game Handlers ---
  const handleOpenEditModal = (game) => {
    if (isApiInProgress) return; // Don't open modal if another API call is running
    setGameToEdit(game);
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    if (isApiInProgress) return; // Prevent closing if API call from modal is running (though save button would be disabled)
    setIsEditModalOpen(false);
    setGameToEdit(null);
  };

  const handleSaveGameChanges = async (updatedGameData) => {
    if (!gameToEdit || isApiInProgress) return;
    setIsApiInProgress(true);
    try {
      const payload = {
        p1: updatedGameData.p1,
        p2: updatedGameData.p2,
        winner: updatedGameData.winner,
        season: updatedGameData.season,
      };
      await axios.put(`${API_URL}/api/game/${gameToEdit.id}`, payload);
      alert(
        `Game #${gameToEdit.id} updated successfully. ELOs will be recalculated.`,
      );
      handleCloseEditModal(); // Close modal first
      fetchData(); // Then refresh data
    } catch (error) {
      console.error(`Error updating game #${gameToEdit.id}:`, error);
      alert(
        `Failed to update game. Server says: ${error.response?.data?.error || "Unknown error"}`,
      );
    } finally {
      setIsApiInProgress(false);
    }
  };

  // --- Delete Game Handler ---
  const handleDeleteGame = async (gameId) => {
    if (isApiInProgress) return;
    const isConfirmed = window.confirm(
      `Are you sure you want to PERMANENTLY DELETE Game #${gameId}? This action cannot be undone and will trigger a full ELO recalculation.`,
    );
    if (isConfirmed) {
      setIsApiInProgress(true);
      try {
        await axios.delete(`${API_URL}/api/game/${gameId}`);
        alert(`Game #${gameId} permanently deleted. ELOs have been updated.`);
        fetchData();
      } catch (error) {
        console.error(`Error deleting game #${gameId}:`, error);
        alert(
          `Failed to delete game. Server says: ${error.response?.data?.error || "Unknown error"}`,
        );
      } finally {
        setIsApiInProgress(false);
      }
    }
  };

  // --- Add Player Handler ---
  const handleAddPlayer = async (e) => {
    e.preventDefault();
    if (isApiInProgress) return;
    if (!newUsername.trim()) {
      alert("Username is required.");
      return;
    }
    const startingElo = parseInt(newPlayerElo, 10);
    if (isNaN(startingElo)) {
      alert("Please enter a valid number for starting ELO.");
      return;
    }
    setIsApiInProgress(true);
    const newPlayer = {
      username: newUsername.trim(),
      description: newDescription.trim(),
      achievements: newAchievements.trim(),
      ELO: startingElo,
    };
    try {
      await axios.post(`${API_URL}/add_player`, newPlayer);
      alert(
        `Player '${newPlayer.username}' added successfully with ELO ${startingElo}!`,
      );
      setNewUsername("");
      setNewDescription("");
      setNewAchievements("");
      setNewPlayerElo("400");
      fetchData();
    } catch (error) {
      console.error("Error adding player:", error);
      alert(
        `Failed to add player. Server says: ${error.response?.data?.error || "Unknown error"}`,
      );
    } finally {
      setIsApiInProgress(false);
    }
  };

  // --- Add Game to Queue Handler (Local state change, not an API call) ---
  const handleAddGameToQueue = (e) => {
    e.preventDefault();
    if (isApiInProgress) return; // Prevent queue modification during other API calls
    if (!p1 || !p2 || !winner || !gameSeason) {
      alert(
        "Please fill out all fields for the game (Player 1, Player 2, Winner, Season).",
      );
      return;
    }
    if (p1 === p2) {
      alert("Player 1 and Player 2 cannot be the same.");
      return;
    }
    const newGameForQueue = {
      p1,
      p2,
      winner,
      season: parseInt(gameSeason, 10),
    };
    setStagedGames([...stagedGames, newGameForQueue]);
    setP1("");
    setP2("");
    setWinner("");
  };

  const handleRemoveFromQueue = (indexToRemove) => {
    if (isApiInProgress) return; // Prevent queue modification during other API calls
    setStagedGames(stagedGames.filter((_, index) => index !== indexToRemove));
  };

  // --- Submit All Staged Games Handler ---
  const handleSubmitAllGames = async () => {
    if (isApiInProgress) return;
    if (stagedGames.length === 0) {
      alert("No games in the queue to submit.");
      return;
    }
    setIsApiInProgress(true);
    try {
      await axios.post(`${API_URL}/add_multiple_games`, {
        games: stagedGames,
        use_current_time: useCurrentTimeForBatch,
      });
      alert(`Successfully added ${stagedGames.length} games!`);
      setStagedGames([]);
      setGameSeason("");
      fetchData();
    } catch (error) {
      console.error("Error adding multiple games:", error);
      alert(
        `Failed to add games. Server says: ${error.response?.data?.error || "Unknown error"}`,
      );
    } finally {
      setIsApiInProgress(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <h1>Loading admin data...</h1>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>🏓 Ping Pong League Admin</h1>

      {/* Add New Player Form */}
      <div className="admin-section">
        <h2>Add New Player</h2>
        <form onSubmit={handleAddPlayer}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="Enter unique username"
              required
              disabled={isApiInProgress}
            />
          </div>
          <div className="form-group">
            <label htmlFor="newPlayerElo">Starting ELO</label>
            <input
              id="newPlayerElo"
              type="number"
              value={newPlayerElo}
              onChange={(e) => setNewPlayerElo(e.target.value)}
              placeholder="e.g., 400"
              required
              min="0"
              disabled={isApiInProgress}
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description (Optional)</label>
            <input
              id="description"
              type="text"
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              placeholder="e.g., Right-handed attacker"
              disabled={isApiInProgress}
            />
          </div>
          <div className="form-group">
            <label htmlFor="achievements">Achievements (Optional)</label>
            <textarea
              id="achievements"
              value={newAchievements}
              onChange={(e) => setNewAchievements(e.target.value)}
              placeholder="e.g., Season 1 Champion"
              rows="3"
              disabled={isApiInProgress}
            ></textarea>
          </div>
          <button type="submit" disabled={isApiInProgress}>
            {isApiInProgress ? "Processing..." : "Add Player"}
          </button>
        </form>
      </div>

      {/* Add Games to Queue Form */}
      <div className="admin-section">
        <h2>Add Games to Queue</h2>
        <form onSubmit={handleAddGameToQueue}>
          <div className="form-group">
            <label htmlFor="gameSeason">Season for this Game</label>
            <input
              id="gameSeason"
              type="number"
              value={gameSeason}
              onChange={(e) => setGameSeason(e.target.value)}
              placeholder="Enter season number"
              required
              min="1"
              disabled={isApiInProgress}
            />
          </div>
          <div className="form-group">
            <label>Player 1</label>
            <select
              value={p1}
              onChange={(e) => setP1(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Player 1</option>
              {players.map((p) => (
                <option key={p.username + "-p1-queue"} value={p.username}>
                  {p.username} (ELO: {p.elo})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Player 2</label>
            <select
              value={p2}
              onChange={(e) => setP2(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Player 2</option>
              {players.map((p) => (
                <option key={p.username + "-p2-queue"} value={p.username}>
                  {p.username} (ELO: {p.elo})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Winner</label>
            <select
              value={winner}
              onChange={(e) => setWinner(e.target.value)}
              required
              disabled={isApiInProgress}
            >
              <option value="">Select Winner</option>
              {p1 && <option value={p1}>{p1}</option>}
              {p2 && <option value={p2}>{p2}</option>}
            </select>
          </div>
          <button
            type="submit"
            className="add-to-queue-button"
            disabled={isApiInProgress}
          >
            {isApiInProgress ? "Processing..." : "Add Game to Queue"}
          </button>
        </form>
      </div>

      {/* Staged Games Queue Display */}
      {stagedGames.length > 0 && (
        <div className="admin-section">
          <h2>Game Queue ({stagedGames.length} games)</h2>
          <div className="form-group-inline">
            <input
              type="checkbox"
              id="useCurrentTimeForBatch"
              checked={useCurrentTimeForBatch}
              onChange={(e) => setUseCurrentTimeForBatch(e.target.checked)}
              disabled={isApiInProgress}
            />
            <label htmlFor="useCurrentTimeForBatch">
              Add Current Timestamp to All Games in Batch
            </label>
          </div>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Season</th>
                <th>Player 1</th>
                <th>Player 2</th>
                <th>Winner</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {stagedGames.map((game, index) => (
                <tr key={index}>
                  <td>{index + 1}</td>
                  <td>S{game.season}</td>
                  <td>{game.p1}</td>
                  <td>{game.p2}</td>
                  <td>
                    <strong>{game.winner}</strong>
                  </td>
                  <td>
                    <button
                      onClick={() => handleRemoveFromQueue(index)}
                      className="remove-button"
                      disabled={isApiInProgress}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button
            onClick={handleSubmitAllGames}
            className="submit-all-button"
            disabled={isApiInProgress || stagedGames.length === 0}
          >
            {isApiInProgress ? "Submitting..." : "Submit All Queued Games"}
          </button>
        </div>
      )}

      {/* Recent Games List */}
      <div className="admin-section">
        <h2>
          Recent Games (Showing latest first - {games.length} games total)
        </h2>
        {games.length === 0 && !loading && <p>No non-archived games found.</p>}
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Season</th>
              <th>Players</th>
              <th>Winner</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game) => (
              <tr key={game.id}>
                <td>{game.id}</td>
                <td>S{game.season || "?"}</td>
                <td>{game.players.join(" vs ")}</td>
                <td>{game.winner}</td>
                <td>
                  {game.date
                    ? new Date(game.date * 1000).toLocaleDateString()
                    : "No Date"}
                </td>
                <td className="actions-cell">
                  <button
                    className="edit-button"
                    onClick={() => handleOpenEditModal(game)}
                    disabled={isApiInProgress}
                  >
                    Edit
                  </button>
                  <button
                    className="delete-button"
                    onClick={() => handleDeleteGame(game.id)}
                    disabled={isApiInProgress}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Edit Modal */}
      {isEditModalOpen && gameToEdit && (
        <GameEditModal
          game={gameToEdit}
          players={players}
          onClose={handleCloseEditModal}
          onSave={handleSaveGameChanges}
          isApiInProgress={isApiInProgress} // Pass state to modal
        />
      )}
    </div>
  );
}

export default AdminPage;
