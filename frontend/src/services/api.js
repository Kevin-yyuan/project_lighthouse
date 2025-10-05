import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * Fetches projects from the API with optional filters.
 * @param {object} filters - An object containing filter keys and values.
 * @returns {Promise<Array>} - A promise that resolves to an array of project objects.
 */
export const getProjects = async (filters = {}) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/projects`, {
      params: filters,
    });
    // Defensively ensure the response is an array.
    if (Array.isArray(response.data)) {
      return response.data;
    } else {
      console.error("API did not return an array:", response.data);
      return []; // Return empty array if the response is not an array
    }
  } catch (error) {
    console.error("Error fetching projects:", error);
    // In a real app, you might want to handle this more gracefully
    // e.g., show a notification to the user.
    return []; // Return empty array on network error
  }
};
