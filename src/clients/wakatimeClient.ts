import { WakaTimeStatsData, WakaTimeStatsResponse } from '../types';

const WAKATIME_BASE_URL = 'https://wakatime.com/api/v1';

function getAuthHeader(): string {
  if (!process.env.WAKATIME_API_KEY) {
    throw new Error('WakaTime API key not provided');
  }

  const encodedApiKey = Buffer.from(process.env.WAKATIME_API_KEY).toString(
    'base64'
  );
  return `Basic ${encodedApiKey}`;
}

export async function getStats(range: string): Promise<WakaTimeStatsData> {
  const response = await fetch(
    `${WAKATIME_BASE_URL}/users/current/stats/${range}`,
    {
      headers: {
        Authorization: getAuthHeader(),
        Accept: 'application/json',
      },
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `WakaTime API error: ${response.status} ${response.statusText} - ${errorText}`
    );
  }

  const result = (await response.json()) as WakaTimeStatsResponse;
  return result.data;
}
