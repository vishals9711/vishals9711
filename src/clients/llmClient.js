import { GoogleGenerativeAI } from '@google/generative-ai';

if (!process.env.LLM_API_KEY) {
  throw new Error('LLM_API_KEY environment variable is required');
}

const genAI = new GoogleGenerativeAI(process.env.LLM_API_KEY);

export async function generateBio(data) {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
  const prompt = `Based on the following data, generate a dynamic, engaging one-sentence bio for a GitHub profile. Make it personal, enthusiastic, and showcase the developer's passion for coding. Include their top language and coding hours. Respond ONLY with a JSON object with a single key: 'bio'. Do not include any markdown formatting or code blocks.

    Data: ${JSON.stringify(data)}`;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = await response.text();
  
  // Clean the response to extract JSON
  let cleanedText = text.trim();
  
  // Remove markdown code blocks if present
  if (cleanedText.startsWith('```json')) {
    cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
  } else if (cleanedText.startsWith('```')) {
    cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '');
  }
  
  // Try to find JSON object in the response
  const jsonMatch = cleanedText.match(/\{.*\}/s);
  if (jsonMatch) {
    cleanedText = jsonMatch[0];
  }
  
  return JSON.parse(cleanedText);
}

export async function generateProjectDescription(data) {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
  const prompt = `Based on the following repository information, generate an engaging, professional project description. Make it sound interesting and highlight what makes this project special. Return ONLY a JSON object with a single key 'description' containing the description text.

    Repository Data: ${JSON.stringify(data)}

    Guidelines:
    - Make it engaging and professional
    - Highlight the technology stack
    - Mention what makes it unique or interesting
    - Keep it concise but informative
    - Don't use generic phrases like "amazing project"

    Respond ONLY with JSON, no markdown formatting.`;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = await response.text();
  
  // Clean the response to extract JSON
  let cleanedText = text.trim();
  
  // Remove markdown code blocks if present
  if (cleanedText.startsWith('```json')) {
    cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
  } else if (cleanedText.startsWith('```')) {
    cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '');
  }
  
  // Try to find JSON object in the response
  const jsonMatch = cleanedText.match(/\{.*\}/s);
  if (jsonMatch) {
    cleanedText = jsonMatch[0];
  }
  
  return JSON.parse(cleanedText);
}

export async function generateTechStack(data) {
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
  const prompt = `Based on the following GitHub repository language data, generate an enhanced tech stack. Analyze the languages and suggest related technologies, frameworks, and tools that would typically be used together. Return ONLY a JSON object with a single key 'techStack' containing an array of technology names.

    Language Data: ${JSON.stringify(data)}

    Examples of enhanced tech stack:
    - If JavaScript is present, consider adding React, Node.js, Express
    - If Python is present, consider adding Django, Flask, FastAPI
    - If TypeScript is present, consider adding Angular, NestJS
    - Include popular frameworks, databases, and tools that complement the languages

    Respond ONLY with JSON, no markdown formatting.`;

  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = await response.text();
  
  // Clean the response to extract JSON
  let cleanedText = text.trim();
  
  // Remove markdown code blocks if present
  if (cleanedText.startsWith('```json')) {
    cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
  } else if (cleanedText.startsWith('```')) {
    cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '');
  }
  
  // Try to find JSON object in the response
  const jsonMatch = cleanedText.match(/\{.*\}/s);
  if (jsonMatch) {
    cleanedText = jsonMatch[0];
  }
  
  return JSON.parse(cleanedText);
}
