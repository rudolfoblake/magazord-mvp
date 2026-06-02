import inquirer from "inquirer";
import { MCPManager } from "./mcp.js";
import { GeminiManager } from "./gemini.js";
import dotenv from "dotenv";

dotenv.config();

function wrapText(text: string, maxWidth: number) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const wrapped: string[] = [];

  for (const line of lines) {
    if (!line.trim()) {
      wrapped.push("");
      continue;
    }

    const indentMatch = line.match(/^(\s+)/);
    const indent = indentMatch ? indentMatch[1] : "";
    const content = line.slice(indent.length);

    const words = content.split(/\s+/).filter(Boolean);
    let current = indent;

    for (const word of words) {
      const next = (current.trim().length ? current + " " : current) + word;
      if (next.length > maxWidth && current.trim().length) {
        wrapped.push(current);
        current = indent + word;
      } else {
        current = next;
      }
    }

    wrapped.push(current);
  }

  return wrapped.join("\n");
}

function formatAnswer(answer: string) {
  const columns = typeof process.stdout.columns === "number" ? process.stdout.columns : 100;
  const maxWidth = Math.max(60, Math.min(columns, 120));

  let text = answer.replace(/\r\n/g, "\n");

  text = text.replace(/^\s*---+\s*$/gm, "-----------------------------------------");

  text = text.replace(/^\s*```[a-zA-Z0-9_-]*\s*$/gm, "[CODE_BLOCK_START]");
  text = text.replace(/^\s*```\s*$/gm, "[CODE_BLOCK_END]");

  const lines = text.split("\n");
  let inCode = false;
  const out: string[] = [];

  for (let line of lines) {
    if (line === "[CODE_BLOCK_START]") {
      inCode = true;
      continue;
    }

    if (line === "[CODE_BLOCK_END]") {
      inCode = false;
      continue;
    }

    if (inCode) {
      out.push("    " + line);
      continue;
    }

    line = line.replace(/\*\*(.+?)\*\*/g, "$1");

    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const title = headingMatch[2].trim();
      out.push("");
      out.push(title.toUpperCase());
      out.push("-----------------------------------------");
      continue;
    }

    line = line.replace(/^(\s*)[*-]\s+/g, "$1• ");

    out.push(line);
  }

  const compact = out
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  return wrapText(compact, maxWidth);
}

async function main() {
  console.log("-----------------------------------------");
  console.log("🚀 Ecommerce BI Copilot - MCP MVP");
  console.log("-----------------------------------------");

  const mcpManager = new MCPManager();
  
  try {
    await mcpManager.connect();
    const geminiManager = new GeminiManager(mcpManager);

    console.log("\nOlá! Eu sou seu assistente de BI. Como posso ajudar hoje?");
    console.log("(Digite 'sair' para encerrar)\n");

    while (true) {
      const { question } = await inquirer.prompt([
        {
          type: "input",
          name: "question",
          message: "Pergunta:",
        },
      ]);

      if (question.toLowerCase() === "sair" || question.toLowerCase() === "exit") {
        break;
      }

      if (!question.trim()) continue;

      console.log("\nThinking...");
      
      try {
        const answer = await geminiManager.chat(question);
        console.log("\n-----------------------------------------");
        console.log(formatAnswer(answer));
        console.log("-----------------------------------------\n");
      } catch (error: any) {
        console.error("\n❌ Erro ao processar pergunta:", error.message);
      }
    }

  } catch (error: any) {
    console.error("\n❌ Erro fatal:", error.message);
  } finally {
    if (mcpManager) {
      try {
        await mcpManager.disconnect();
      } catch (e) {
        console.warn("\n⚠️  Erro ao desconectar do MCP Server");
      }
    }
    process.exit(0);
  }
}

main();
