// src/App.jsx
import React, { useState } from 'react';
import Header from './components/Header.jsx'; 
import Footer from './components/Footer.jsx'; 
import PlayerList from './components/PlayerList.jsx'; 
import PlayerDetail from './components/PlayerDetail.jsx'; 

const DEFAULT_SEASON = 2025; // Default is current season

const App = () => {
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(DEFAULT_SEASON);

  const handleSelectPlayer = (playerId) => {
    setSelectedPlayerId(playerId);
  };

  const handleSeasonChange = (season) => {
    setSelectedSeason(parseInt(season)); // Parse input as int
  };

  return (
    <div className="app-container">
      <Header />
      <div className="main-layout-content">
        <aside className="sidebar"> 
          <PlayerList onSelectPlayer={handleSelectPlayer} selectedPlayerId={selectedPlayerId} />
          <div className="season-selector">
            <h3>Select Season:</h3>
            <input
              type="number"
              value={selectedSeason}
              onChange={(e) => handleSeasonChange(e.target.value)} // Pass event target value
              min="1900" 
              max="2025" 
              className="season-input"
            />
          </div>
        </aside>
        <main className="main-content-area"> 
          <PlayerDetail playerId={selectedPlayerId} selectedSeason={selectedSeason} />
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default App;
