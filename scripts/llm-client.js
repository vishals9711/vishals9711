import { GoogleGenerativeAI } from "@google/generative-ai";

class LlmClient {
  constructor(apiKey) {
    this.apiKey = apiKey; // API key for the LLM service
    this.genAI = new GoogleGenerativeAI(this.apiKey);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
  }

  async generateText(prompt, options = {}) {
    if (!this.apiKey) {
      console.warn("LLM_API_KEY is not set. Using static fallback for LLM features.");
      return `(LLM Fallback: Could not generate text for: ${prompt.substring(0, 50)}...)`;
    }

    console.log("Calling Google Gemini API with prompt:", prompt);

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      return text;
    } catch (error) {
      console.error("Error communicating with Google Gemini API:", error);
      return `(LLM Fallback: Could not generate text for: ${prompt.substring(0, 50)}...)`;
    }
  }
}

export default LlmClient;
