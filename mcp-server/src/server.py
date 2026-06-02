from mcp.server.fastmcp import FastMCP
import os
import json
import logging
import sys
import time
from functools import wraps
from src.tools.sales_tools import register_sales_tools
from src.tools.analytics_tools import register_analytics_tools
from src.services.cache_service import cache_service

# Configuração de log estruturado para stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("mcp_telemetry")

host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
port = int(os.getenv("MCP_HTTP_PORT", "8000"))
mcp = FastMCP("Ecommerce BI Copilot", host=host, port=port)

def tool_telemetry(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = f.__name__
        
        # Atributos de log estruturado
        log_data = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "tool": tool_name,
            "arguments": {k: v for k, v in kwargs.items() if k != 'self'},
            "cache_hit": False, # Valor padrão, pode ser atualizado se houver comunicação entre decorators
            "success": False
        }

        try:
            # Capturar se foi cache hit do contexto do wrapper (se possível)
            result = f(*args, **kwargs)
            
            # Detecção simples de cache hit baseada no fato de que o mcp_cache 
            # já loga o HIT antes de retornar. Para um log estruturado unificado:
            if isinstance(result, dict) and "_cache_hit" in result:
                log_data["cache_hit"] = result.pop("_cache_hit")

            duration_ms = (time.time() - start_time) * 1000
            log_data.update({
                "execution_time_ms": round(duration_ms, 2),
                "success": True
            })
            
            print(json.dumps(log_data), flush=True)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_data.update({
                "execution_time_ms": round(duration_ms, 2),
                "success": False,
                "error_message": str(e)
            })
            print(json.dumps(log_data), flush=True)
            raise
    return wrapper

# Registra as ferramentas organizadas por domínio
register_sales_tools(mcp, tool_telemetry)
register_analytics_tools(mcp, tool_telemetry)
