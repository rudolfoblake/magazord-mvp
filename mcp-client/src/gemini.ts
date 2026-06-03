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
    let response: any;
    let attempts = 0;
    const maxAttempts = 3;

    while (attempts < maxAttempts) {
      try {
        let result = await this.chatSession!.sendMessage(userMessage);
        response = result.response;
        break;
      } catch (error: any) {
        attempts++;
        console.error(`\n[Gemini] Erro na chamada (tentativa ${attempts}/${maxAttempts}): ${error.message}`);
        
        if (attempts >= maxAttempts) {
          return "Desculpe, o serviço de inteligência artificial (Gemini) está temporariamente indisponível após várias tentativas. Por favor, tente novamente em instantes.";
        }
        
        // Aguarda 1 segundo antes de tentar novamente
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    // 4. Handle tool calls (loop until no more calls)
    while (response.functionCalls()?.length) {
      const toolCalls = response.functionCalls();
      if (!toolCalls) break;

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

      // Send tool results back to Gemini with retry
      let toolAttempts = 0;
      while (toolAttempts < maxAttempts) {
        try {
          const result = await this.chatSession!.sendMessage(toolResults);
          response = result.response;
          break;
        } catch (error: any) {
          toolAttempts++;
          console.error(`\n[Gemini] Erro ao enviar resultados (tentativa ${toolAttempts}/${maxAttempts}): ${error.message}`);
          
          if (toolAttempts >= maxAttempts) {
            return "Desculpe, o serviço de inteligência artificial (Gemini) falhou ao processar os dados das ferramentas após várias tentativas.";
          }
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }

    return response.text();
  }
}
