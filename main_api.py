import asyncio
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from log.rmma_logger import get_logger
from rmma2.agent_manager import AgentManager, get_agent_all
import json
from prompt.prompt_manager import PromptManager
from schemas.agent import AgentInfo
from services.rmma_service import RmmaService

# from main import async_content_generation, stream_run_agent

app = FastAPI(
    title="RMMA = Rakuten Mobile Marketing Agent API",
    description="楽天モバイルのマーケティング投稿を生成・実行するAPIです．",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 全てのオリジンを許可（開発用）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    agent_name: str
    prompt: str

def log(logger, method, request_url, user_agent):
    logger.info(f"[{method}]{request_url}[user_agent]{user_agent}")

@app.get("/", summary="APIのヘルスチェック")
async def read_root():
    """
    APIサーバが正常に動作しているか確認するためのエンドポイントです．
    """
    return {"status": "ok", "message": "RMMA API is running!"}


@app.post("/agent", summary="エージェントの応答をストリーミングで返す")
async def run_agent_stream(agent_request: AgentRequest, request: Request):
        """
        エージェントの実行プロセスをリアルタイムでクライアントにストリーミングします。
        """
        if not agent_request.agent_name:
            raise HTTPException(status_code=400, detail="agent_name can't be None")

        if not agent_request.prompt:
            raise HTTPException(status_code=400, detail="prompt can't be None")

        logger = get_logger("rmma")
        user_agent = request.headers.get("User-Agent", "Unknown")
        method = request.method
        request_url = str(request.url)
        log(logger, method, request_url, user_agent)
        
        agent_manager = AgentManager(agent_request.agent_name)
        return StreamingResponse(
            agent_manager.run_stream_agent(agent_request.prompt),
            media_type="text/plain"
        )

@app.get("/agent/lists", summary="利用可能なエージェントのリストを返す")
def get_agent_list(request: Request):
    logger = get_logger()
    log(
        logger,
        request.method,
        str(request.url),
        request.headers.get("User-Agent", "Unknown")
    )

    agents = get_agent_all()

    return {
        "status": "success",
        "result": json.dumps(agents, ensure_ascii=False)
    }
@app.get("/agent/{agent_name}", summary="指定されたエージェントの詳細情報を返す")
def get_agent_detail(agent_name: str, request: Request):
    logger = get_logger()
    log(
        logger,
        request.method,
        str(request.url),
        request.headers.get("User-Agent", "Unknown")
    )

    try:
        rmma_service = RmmaService()
        agent_info = rmma_service.get_agent_detail(agent_name)
        
        return {
            "status": "success",
            "agent_name": agent_name,
            "result": json.dumps(agent_info, ensure_ascii=False)
        }

    except Exception as e:
        logger.erro(f"Error occured: {e}")
        raise HTTPException(status_code=500, detail=f"内部エラー: {str(e)}")

@app.post('/agent/{agent_name}', summary="agentの編集")
def edit_agent_detail(agent_name: str, agent_info: AgentInfo, request: Request):
    logger = get_logger()
    log(
        logger,
        request.method,
        str(request.url),
        request.headers.get("User-Agent", "Unknown")
    )

    try:
        rmma_service = RmmaService()
        agent_info = rmma_service.edit_agent_detail(agent_info)
        
        return {
            "status": "success",
            "agent_name": agent_name,
            "result": agent_info
        }

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"内部エラー: {str(e)}")

@app.get("/prompt/lists", summary="全てのプロンプトを返す")
def get_prompt_list(request: Request):
    logger = get_logger()
    log(
        logger,
        request.method,
        str(request.url),
        request.headers.get("User-Agent", "Unknown")
    )

    PM = PromptManager()
    prompts = PM.get_prompt_all()
    
    return {
        "result": json.dumps(prompts, ensure_ascii=False)
    }


