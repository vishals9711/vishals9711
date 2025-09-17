import axios from 'axios';

if (!process.env.WAKATIME_API_KEY) {
  throw new Error('WAKATIME_API_KEY environment variable is required');
}

const WAKATIME_API_KEY = process.env.WAKATIME_API_KEY;
const encodedApiKey = Buffer.from(WAKATIME_API_KEY).toString('base64');

const apiClient = axios.create({
  baseURL: 'https://wakatime.com/api/v1',
  headers: {
    Authorization: `Basic ${encodedApiKey}`,
  },
});

export async function getStats(range) {
  return apiClient.get(`/users/current/stats/${range}`);
}
