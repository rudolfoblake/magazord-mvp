import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import dotenv from "dotenv";

dotenv.config();

export class MCPManager {
  private client: Client;
  private transport: StreamableHTTPClientTransport;
  
  // Circuit Breaker State
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failureCount = 0;
  private lastFailureTime: number | null = null;
  private readonly failureThreshold = 3;
  private readonly resetTimeout = 30000; // 30 seconds

  constructor() {
    const serverUrl = process.env.MCP_SERVER_URL || "http://mcp-server:8000/mcp";

    console.log(`[MCP] Connecting to server via HTTP`);
    console.log(`[MCP] URL: ${serverUrl}`);

    this.transport = new StreamableHTTPClientTransport(new URL(serverUrl));

    this.client = new Client(
      {
        name: "ecommerce-bi-client",
        version: "1.0.0",
      },
      {
        capabilities: {},
      }
    );
  }

  private checkCircuit() {
    if (this.state === 'OPEN') {
      const now = Date.now();
      if (this.lastFailureTime && now - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN';
        console.log("[Circuit Breaker] Transitioning to HALF_OPEN - Testing connection...");
        return;
      }
      throw new Error("Circuit Breaker is OPEN. Server calls are suspended temporarily.");
    }
  }

  private recordSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
    this.lastFailureTime = null;
  }

  private recordFailure(error: any) {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      console.error(`[Circuit Breaker] OPENed due to ${this.failureCount} failures. Last error: ${error.message}`);
    }
  }

  async connect() {
    try {
      await this.client.connect(this.transport);
      this.recordSuccess();
      console.log("Connected to MCP Server");
    } catch (error) {
      this.recordFailure(error);
      throw error;
    }
  }

  async listTools() {
    this.checkCircuit();
    try {
      const response = await this.client.listTools();
      this.recordSuccess();
      return response.tools;
    } catch (error) {
      this.recordFailure(error);
      throw error;
    }
  }

  async callTool(name: string, args: any) {
    this.checkCircuit();
    try {
      const result = await this.client.callTool({
        name,
        arguments: args,
      });
      this.recordSuccess();
      return result;
    } catch (error) {
      this.recordFailure(error);
      throw error;
    }
  }

  async disconnect() {
    await this.transport.close();
  }
}
