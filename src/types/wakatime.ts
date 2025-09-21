export interface WakaTimeLanguage {
  name: string;
  total_seconds: number;
  percent: number;
  digital: string;
  decimal: string;
  text: string;
  hours: number;
  minutes: number;
  seconds?: number;
}

export interface WakaTimeStatsData {
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

export interface WakaTimeStatsResponse {
  data: WakaTimeStatsData;
}
