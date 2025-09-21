import { GoogleGenAI } from '@google/genai';
import {
  BioData,
  BioResponse,
  ProjectData,
  ProjectResponse,
  TechStackData,
  TechStackResponse,
} from '../types/index.js';

// Support both old and new environment variable names
const apiKey = process.env.LLM_API_KEY || process.env.GOOGLE_API_KEY;
if (!apiKey) {
  throw new Error(
    'LLM_API_KEY or GOOGLE_API_KEY environment variable is required'
  );
}

const genAI = new GoogleGenAI({ apiKey });
const MODEL_NAME = 'gemini-2.5-flash';

export async function generateBio(data: BioData): Promise<BioResponse> {
  const prompt = `Based on the following data, generate a dynamic, engaging one-sentence bio for a GitHub profile. Make it personal, enthusiastic, and showcase the developer's passion for coding. Include their top language and coding hours.

    Data: ${JSON.stringify(data)}`;

  const result = await genAI.models.generateContent({
    contents: prompt,
    model: MODEL_NAME,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: 'object',
        properties: {
          bio: {
            type: 'string',
            description:
              'A dynamic, engaging one-sentence bio for a GitHub profile',
          },
        },
        required: ['bio'],
      },
    },
  });

  return JSON.parse(result.text || '');
}

export async function generateProjectDescription(
  data: ProjectData
): Promise<ProjectResponse> {
  const prompt = `Based on the following repository information, generate an engaging, professional project description. Make it sound interesting and highlight what makes this project special.

    Repository Data: ${JSON.stringify(data)}

    Guidelines:
    - Make it engaging and professional
    - Highlight the technology stack
    - Mention what makes it unique or interesting
    - Keep it concise but informative
    - Don't use generic phrases like "amazing project"`;

  const result = await genAI.models.generateContent({
    model: MODEL_NAME,
    contents: prompt,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: 'object',
        properties: {
          description: {
            type: 'string',
            description: 'An engaging, professional project description',
          },
        },
        required: ['description'],
      },
    },
  });

  return JSON.parse(result.text || '');
}

export async function generateTechStack(
  data: TechStackData
): Promise<TechStackResponse> {
  const prompt = `Based on the following GitHub repository language data, generate an enhanced tech stack. Analyze the languages and suggest related technologies, frameworks, and tools that would typically be used together.

    Language Data: ${JSON.stringify(data)}

    Examples of enhanced tech stack:
    - If JavaScript is present, consider adding React, Node.js, Express
    - If Python is present, consider adding Django, Flask, FastAPI
    - If TypeScript is present, consider adding Angular, NestJS
    - Include popular frameworks, databases, and tools that complement the languages`;

  const result = await genAI.models.generateContent({
    model: MODEL_NAME,
    contents: prompt,
    config: {
      responseMimeType: 'application/json',
      responseSchema: {
        type: 'object',
        properties: {
          techStack: {
            type: 'array',
            items: {
              type: 'string',
            },
            description:
              'Array of technology names that complement the detected languages',
          },
        },
        required: ['techStack'],
      },
    },
  });

  return JSON.parse(result.text || '');
}
