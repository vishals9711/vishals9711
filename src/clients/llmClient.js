import { GoogleGenerativeAI } from '@google/generative-ai';

if (!process.env.LLM_API_KEY) {
  throw new Error('LLM_API_KEY environment variable is required');
}

const genAI = new GoogleGenerativeAI(process.env.LLM_API_KEY);

export async function generateBio(data) {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
  const prompt = `Based on the following data, generate a dynamic, one-sentence bio. Respond ONLY with a JSON object with a single key: 'bio'.\n
    Data: ${JSON.stringify(data)}`;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = await response.text();
  return JSON.parse(text);
}
