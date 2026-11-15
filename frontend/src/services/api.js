
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

// Reusable function for communicating with Flask
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const result = await response.json();

  if (!response.ok) {
    const error = new Error(
      result.error ||
      result.optimization?.message ||
      'Something went wrong.'
    );

    error.data = result;
    throw error;
  }

  return result;
}

// Retrieve registered households
export function getHouseholds() {
  return apiRequest('/households');
}

// Register a new household
export function createHousehold(data) {
  return apiRequest('/households', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Retrieve household consumption records
export function getConsumption(householdId) {
  return apiRequest(`/consumption/${householdId}`);
}

// Add a daily consumption record
export function addConsumption(data) {
  return apiRequest('/consumption', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Retrieve household analytics
export function getAnalytics(householdId) {
  return apiRequest(`/analytics/${householdId}`);
}

// Predict water consumption using KNN
export function predictConsumption(data) {
  return apiRequest('/predict', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Predict and optimize water allocation
export function recommendConsumption(data) {
  return apiRequest('/recommend', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
