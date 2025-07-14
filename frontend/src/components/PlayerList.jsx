import React, { useState, useEffect } from 'react';
import { getAllPlayers } from '../api/api.js';

const PlayerList = ({ onSelectPlayer, selectedPlayerId }) => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayersData = async () => {
      try {
        const data = await getAllPlayers();
        setPlayers(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPlayersData();
  }, []);

  // Prepare options for the select dropdown
  const playerOptions = players.map(p => ({
    label: p.player_name,
    value: p.player_id
  }));

  // Find the selected player's name for display in the dropdown
  const currentSelectedLabel = playerOptions.find(opt => opt.value === selectedPlayerId)?.label || '';

  return (
    <div className="player-list-sidebar">
      <h3 className="sidebar-heading">Select Player:</h3>
      {loading && <p className="loading-message">Loading players...</p>}
      {error && (
        <div className="error-message" role="alert">
          <strong>Error!</strong>
          <span> {error}</span>
        </div>
      )}
      {!loading && !error && players.length === 0 && (
        <p className="no-players-message">No players found. Check your Flask API.</p>
      )}
      {!loading && !error && players.length > 0 && (
        <select
          className="player-select-dropdown"
          onChange={(e) => onSelectPlayer(e.target.value)}
          value={selectedPlayerId || ''} // Set value to control the select component
        >
          <option value="">-- Select a player --</option>
          {playerOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      )}
      {selectedPlayerId && (
        <p className="selected-player-info">Selected: <strong>{currentSelectedLabel}</strong></p>
      )}
    </div>
  );
};

export default PlayerList;
