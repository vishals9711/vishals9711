import axios, { AxiosResponse } from 'axios';

interface WakaTimeStats {
  data: {
    languages: Array<{
      name: string;
      total_seconds: number;
      percent: number;
    }>;
    total_seconds: number;
  };
}

const apiClient = axios.create({
  baseURL: 'https://wakatime.com/api/v1',
});

export async function initializeWakaTime(): Promise<void> {
  if (!process.env.WAKATIME_API_KEY) {
    console.log('WakaTime API key not provided, WakaTime features will be disabled');
    return;
  }

  const encodedApiKey = Buffer.from(process.env.WAKATIME_API_KEY).toString('base64');
  apiClient.defaults.headers.common['Authorization'] = `Basic ${encodedApiKey}`;
}

export async function getStats(range: string): Promise<any> {
  if (!process.env.WAKATIME_API_KEY) {
    throw new Error('WakaTime API key not provided');
  }
  return apiClient.get(`/users/current/stats/${range}`);
}

// Initialize WakaTime on module load
initializeWakaTime();
