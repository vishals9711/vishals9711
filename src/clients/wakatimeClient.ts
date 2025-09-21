const WAKATIME_BASE_URL = 'https://wakatime.com/api/v1';

interface WakaTimeLanguage {
  name: string | null;
  total_seconds: number;
  percent: number;
  digital: string;
  decimal: string;
  text: string;
  hours: number;
  minutes: number;
  seconds?: number;
}

interface WakaTimeStatsData {
  total_seconds: number;
  languages: WakaTimeLanguage[];
  human_readable_total: string;
  is_cached: boolean;
  username: string;
  is_including_today: boolean;
  human_readable_range: string;
  is_coding_activity_visible: boolean;
  is_language_usage_visible: boolean;
  is_editor_usage_visible: boolean;
  is_category_usage_visible: boolean;
  is_os_usage_visible: boolean;
}

interface WakaTimeStatsResponse {
  data: WakaTimeStatsData;
}

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

  const result: WakaTimeStatsResponse = await response.json();
  return result.data;
}
