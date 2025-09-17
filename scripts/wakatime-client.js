import fetch from 'node-fetch';

class WakatimeClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = "https://wakatime.com/api/v1";
    this.headers = {
      Authorization: `Basic ${Buffer.from(apiKey).toString('base64')}`,
      "Content-Type": "application/json",
    };
  }

  async _makeRequest(endpoint, params = {}) {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

    try {
      const response = await fetch(url.toString(), {
        headers: this.headers,
        timeout: 30000, // 30 seconds timeout
      });

      if (response.status === 429) {
        const retryAfter = response.headers.get("Retry-After") || "unknown";
        throw new Error(`Wakatime API rate limit exceeded. Retry after: ${retryAfter} seconds`);
      }

      if (response.status === 401) {
        throw new Error("Wakatime API authentication failed. Check your API key.");
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Wakatime API request failed for endpoint ${endpoint}:`, error);
      throw error;
    }
  }

  async fetchCodingStats(range = "last_7_days") {
    const endpoint = `/users/current/summaries`;
    const params = { range };

    try {
      const responseData = await this._makeRequest(endpoint, params);

      if (!responseData.data) {
        console.warn("No data found in Wakatime response");
        return this._getEmptyStats();
      }

      let totalSeconds = 0;
      const languagesData = {};
      const editorsData = {};
      const osData = {};

      for (const dayData of responseData.data) {
        if (!dayData.grand_total) continue;

        totalSeconds += dayData.grand_total.total_seconds;

        for (const lang of dayData.languages || []) {
          const langName = lang.name;
          const langSeconds = lang.total_seconds;
          languagesData[langName] = (languagesData[langName] || 0) + langSeconds;
        }

        for (const editor of dayData.editors || []) {
          const editorName = editor.name;
          const editorSeconds = editor.total_seconds;
          editorsData[editorName] = (editorsData[editorName] || 0) + editorSeconds;
        }

        for (const os of dayData.operating_systems || []) {
          const osName = os.name;
          const osSeconds = os.total_seconds;
          osData[osName] = (osData[osName] || 0) + osSeconds;
        }
      }

      const languages = Object.entries(languagesData).map(([name, total_seconds]) => ({
        name,
        total_seconds,
        percentage: totalSeconds > 0 ? parseFloat(((total_seconds / totalSeconds) * 100).toFixed(2)) : 0,
      }));
      languages.sort((a, b) => b.total_seconds - a.total_seconds);

      const editors = Object.entries(editorsData).map(([name, total_seconds]) => ({
        name,
        total_seconds,
      }));
      editors.sort((a, b) => b.total_seconds - a.total_seconds);

      const operatingSystems = Object.entries(osData).map(([name, total_seconds]) => ({
        name,
        total_seconds,
      }));
      operatingSystems.sort((a, b) => b.total_seconds - a.total_seconds);

      return {
        total_seconds: totalSeconds,
        languages,
        editors,
        operating_systems: operatingSystems,
      };
    } catch (error) {
      console.error("Failed to fetch coding stats:", error);
      throw error;
    }
  }

  _getEmptyStats() {
    return {
      total_seconds: 0,
      languages: [],
      editors: [],
      operating_systems: [],
    };
  }
}

export default WakatimeClient;
