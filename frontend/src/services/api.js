import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5001/api';

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
    return []; // Return empty array on network error
  }
};

/**
 * Sends a question to the chatbot API endpoint.
 * @param {string} question - The user's question.
 * @returns {Promise<object>} - A promise that resolves to the chatbot's response object.
 */
export const askChatbot = async (question) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ask`, {
      question: question,
    });
    // Return the full response object for enhanced chatbot features
    return response.data;
  } catch (error) {
    console.error("Error asking chatbot:", error);
    return {
      type: "text",
      answer: "Sorry, there was an error connecting to the chatbot."
    };
  }
};
