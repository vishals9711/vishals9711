import axios from 'axios';
const apiClient = axios.create({
    baseURL: 'https://wakatime.com/api/v1',
});
export async function initializeWakaTime() {
    if (!process.env.WAKATIME_API_KEY) {
        console.log('WakaTime API key not provided, WakaTime features will be disabled');
        return;
    }
    const encodedApiKey = Buffer.from(process.env.WAKATIME_API_KEY).toString('base64');
    apiClient.defaults.headers.common['Authorization'] = `Basic ${encodedApiKey}`;
}
export async function getStats(range) {
    if (!process.env.WAKATIME_API_KEY) {
        throw new Error('WakaTime API key not provided');
    }
    return apiClient.get(`/users/current/stats/${range}`);
}
initializeWakaTime();
//# sourceMappingURL=wakatimeClient.js.map