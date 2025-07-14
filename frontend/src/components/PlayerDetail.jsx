import React, { useState, useEffect } from 'react';
import { getPlayerStatsForSeason, getAllPlayerStatsForSeason } from '../api/api.js';
import ScatterPlot from './ScatterPlot.jsx'; 

const PlayerDetail = ({ playerId, selectedSeason }) => {
  const [playerStats, setPlayerStats] = useState(null);
  const [allPlayersStats, setAllPlayersStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStatForPlot, setSelectedStatForPlot] = useState(null);
  const [selectedStatLabel, setSelectedStatLabel] = useState(null);

  // Map of statistic keys to their UI-friendly labels
  const statLabels = {
    'games_played': 'Games Played',
    'at_bats': 'At Bats',
    'runs': 'Runs',
    'hits': 'Hits',
    'home_runs': 'Home Runs',
    'rbi': 'RBI',
    'obp': 'On-Base Percentage (OBP)',
    'slg': 'Slugging Percentage (SLG)',
    'ops': 'On-Base Plus Slugging (OPS)',
    'war': 'Wins Above Replacement (WAR)',
    'doubles': 'Doubles',
    'triples': 'Triples',
    'walks': 'Walks',
    'strikeouts': 'Strikeouts',
    'sb': 'Stolen Bases',
    'cs': 'Caught Stealing',
    'ops_plus': 'OPS+',
    'roba': 'rOBA',
    'rbat_plus': 'Rbat+',
    'tb': 'Total Bases',
    'gidp': 'GIDP',
    'hbp': 'Hit By Pitch',
    'sh': 'Sacrifice Hits',
    'sf': 'Sacrifice Flies',
    'ibb': 'Intentional Walks',
  };

  // Handling a click on a stat item
  const handleStatClick = (statKey) => {
    // If the same stat is clicked, close the plot
    if (selectedStatForPlot === statKey) {
      setSelectedStatForPlot(null);
      setSelectedStatLabel(null);
    } else {
      setSelectedStatForPlot(statKey);
      setSelectedStatLabel(statLabels[statKey] || statKey); // Use label from map, fallback to key
    }
  };

  // UseEffect to fetch player's individual stats and all players' stats for the season
  useEffect(() => {
    if (!playerId) {
      setPlayerStats(null);
      //setPlayerContract(null); Update when contracts are implemented
      setAllPlayersStats([]); // Reset all players stats
      setLoading(false);
      return;
    }

    const fetchDetailData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch individual player stats
        const stats = await getPlayerStatsForSeason(playerId, selectedSeason);
        setPlayerStats(stats);

        // Fetch contract data (even if not displayed, it's good to have the function ready)
        //const contract = await getPlayerContracts(playerId);
        //setPlayerContract(contract); 
        
        //More contract data handling when implemented ^^

        // Fetch all player stats for the selected season for the scatterplot
        const allStats = await getAllPlayerStatsForSeason(selectedSeason);
        setAllPlayersStats(allStats);

      } catch (err) {
        console.error("Error fetching player details or all season stats:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetailData();
  }, [playerId, selectedSeason]); // Re-run effect when playerId or selectedSeason changes

  if (!playerId) {
    return <div className="info-message">Please select a player from the sidebar to view details.</div>;
  }

  if (loading) {
    return <div className="loading-message">Loading player details...</div>;
  }

  if (error) {
    return (
      <div className="error-message" role="alert">
        <strong>Error!</strong>
        <span> {error}</span>
      </div>
    );
  }

  // Render Player Details
  return (
    <div className="player-detail-container">
      <h2 className="detail-heading">Player Details</h2>

      <div className="section-card">
        <h3 className="section-title">Performance Stats for {selectedSeason} Season (Click a stat to plot!)</h3>
        {playerStats ? (
          <div className="stats-grid">
            <div className="stat-item" onClick={() => handleStatClick('games_played')}>
              <span>Games Played:</span> <strong>{playerStats.games_played || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('at_bats')}>
              <span>At Bats:</span> <strong>{playerStats.at_bats || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('runs')}>
              <span>Runs:</span> <strong>{playerStats.runs || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('hits')}>
              <span>Hits:</span> <strong>{playerStats.hits || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('home_runs')}>
              <span>HR:</span> <strong>{playerStats.home_runs || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('rbi')}>
              <span>RBI:</span> <strong>{playerStats.rbi || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('obp')}>
              <span>OBP:</span> <strong>{parseFloat(playerStats.obp || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('slg')}>
              <span>SLG:</span> <strong>{parseFloat(playerStats.slg || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('ops')}>
              <span>OPS:</span> <strong>{parseFloat(playerStats.ops || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('war')}>
              <span>WAR:</span> <strong>{parseFloat(playerStats.war || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('doubles')}>
              <span>2B:</span> <strong>{playerStats.doubles || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('triples')}>
              <span>3B:</span> <strong>{playerStats.triples || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('walks')}>
              <span>BB:</span> <strong>{playerStats.walks || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('strikeouts')}>
              <span>SO:</span> <strong>{playerStats.strikeouts || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('sb')}>
              <span>SB:</span> <strong>{playerStats.sb || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('cs')}>
              <span>CS:</span> <strong>{playerStats.cs || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('ops_plus')}>
              <span>OPS+:</span> <strong>{parseFloat(playerStats.ops_plus || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('roba')}>
              <span>rOBA:</span> <strong>{parseFloat(playerStats.roba || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('rbat_plus')}>
              <span>Rbat+:</span> <strong>{parseFloat(playerStats.rbat_plus || 0)}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('tb')}>
              <span>TB:</span> <strong>{playerStats.tb || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('gidp')}>
              <span>GIDP:</span> <strong>{playerStats.gidp || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('hbp')}>
              <span>HBP:</span> <strong>{playerStats.hbp || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('sh')}>
              <span>SH:</span> <strong>{playerStats.sh || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('sf')}>
              <span>SF:</span> <strong>{playerStats.sf || 'N/A'}</strong>
            </div>
            <div className="stat-item" onClick={() => handleStatClick('ibb')}>
              <span>IBB:</span> <strong>{playerStats.ibb || 'N/A'}</strong>
            </div>
          </div>
        ) : (
          <div className="info-message">No performance stats available for this season.</div>
        )}
      </div>

      {/* Scatterplot Section, conditionally rendered */}
      {selectedStatForPlot && allPlayersStats.length > 0 && (
        <div className="section-card scatterplot-section">
          <h3 className="section-title">
            {selectedStatLabel} Distribution for {selectedSeason} Season
            <button className="close-plot-button" onClick={() => handleStatClick(selectedStatForPlot)}>
              &times; Close Plot
            </button>
          </h3>
          <ScatterPlot
            data={allPlayersStats}
            statisticKey={selectedStatForPlot}
            statisticLabel={selectedStatLabel}
            selectedPlayerId={playerId}
            chartTitle={`${selectedStatLabel} Distribution - ${selectedSeason} Season`}
          />
        </div>
      )}
    </div>
  );
};

export default PlayerDetail;
