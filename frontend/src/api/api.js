// Change URL when deploying
const FLASK_API_URL = "http://127.0.0.1:5000";

const handleApiResponse = async (response, errorMessage) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(`${errorMessage} Status: ${response.status}. Details: ${errorData.message || response.statusText}`);
  }
  return response.json();
};

export const getAllPlayers = async () => {
  try {
    const response = await fetch(`${FLASK_API_URL}/api/players`);
    return await handleApiResponse(response, "Error fetching players.");
  } catch (error) {
    console.error("Failed to fetch all players:", error);
    throw error;
  }
};

export const getPlayerStatsForSeason = async (playerId, season) => {
  try {
    const response = await fetch(`${FLASK_API_URL}/api/player_stats/${playerId}/${season}`);
    return await handleApiResponse(response, `Error fetching stats for ${playerId} in ${season}.`);
  } catch (error) {
    console.error(`Failed to fetch player stats for ${playerId} in ${season}:`, error);
    throw error;
  }
};

// Uncommenting if I add contract data in the future
/*
export const getPlayerContracts = async (playerId) => {
  try {
    const response = await fetch(`${FLASK_API_URL}/api/player_contracts/${playerId}`);
    // Handle 404 specifically for contracts as it might be common
    if (response.status === 404) {
      return null; // Return null if no contract is found
    }
    return await handleApiResponse(response, `Error fetching contract for ${playerId}.`);
  } catch (error) {
    console.error(`Failed to fetch player contract for ${playerId}:`, error);
    throw error;
  }
};
*/

export const getAllPlayerStatsForSeason = async (season) => {
  try {
    const response = await fetch(`${FLASK_API_URL}/api/season_stats/${season}`);
    if (response.status === 404) {
      return []; // Return empty array if no data for the season
    }
    return await handleApiResponse(response, `Error fetching all player stats for season ${season}.`);
  } catch (error) {
    console.error(`Failed to fetch all player stats for season ${season}:`, error);
    throw error;
  }
};