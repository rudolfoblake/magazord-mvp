import { GoogleGenerativeAI, Tool, ChatSession } from "@google/generative-ai";
import { MCPManager } from "./mcp.js";
import { SYSTEM_PROMPT } from "./prompts.js";
import dotenv from "dotenv";

dotenv.config();

export class GeminiManager {
  private genAI: GoogleGenerativeAI;
  private model: any;
  private mcpManager: MCPManager;
  private chatSession: ChatSession | null = null;

  constructor(mcpManager: MCPManager) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("GEMINI_API_KEY is not set in environment variables");
    }
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.mcpManager = mcpManager;

    this.model = this.createModel("gemini-3.5-flash");
  }

  private createModel(modelName: string) {
    return this.genAI.getGenerativeModel({
      model: modelName,
      systemInstruction: SYSTEM_PROMPT,
      generationConfig: {
        temperature: 0,
      },
    });
  }

  async chat(userMessage: string) {
    // 1. Get available tools from MCP
    const mcpTools = await this.mcpManager.listTools();
    
    // 2. Map MCP tools to Gemini tool format
    const geminiTools: Tool[] = [
      {
        functionDeclarations: mcpTools.map((tool) => ({
          name: tool.name,
          description: tool.description,
          parameters: tool.inputSchema as any,
        })),
      },
    ];

    if (!this.chatSession) {
      this.chatSession = this.model.startChat({
        tools: geminiTools,
      });
    }

    // 3. Send message to Gemini
    let result = await this.chatSession.sendMessage(userMessage);
    let response = result.response;

    // 4. Handle tool calls (loop until no more calls)
    while (response.functionCalls()?.length) {
      const toolCalls = response.functionCalls();
      const toolResults = [];

      for (const call of toolCalls) {
        console.log(`\n[MCP] Calling tool: ${call.name} with args:`, call.args);
        
        try {
          const mcpResult = await this.mcpManager.callTool(call.name, call.args);
          toolResults.push({
            functionResponse: {
              name: call.name,
              response: mcpResult,
            },
          });
        } catch (error: any) {
          toolResults.push({
            functionResponse: {
              name: call.name,
              response: { error: error.message },
            },
          });
        }
      }

      // Send tool results back to Gemini
      result = await this.chatSession.sendMessage(toolResults);
      response = result.response;
    }

    return response.text();
  }
}
