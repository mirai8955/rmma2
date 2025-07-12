import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from log.rmma_logger import get_logger
from rmma2.agent_manager import AgentManager

from main import async_content_generation, stream_run_agent

app = FastAPI(
    title="RMMA = Rakuten Mobile Marketing Agent API",
    description="楽天モバイルのマーケティング投稿を生成・実行するAPIです．",
    version="1.0.0",
)

class AgentRequest(BaseModel):
    agent_name: str
    prompt: str

def log(logger, method, request_url, user_agent):
    logger.info(f"[{method}] {request_url} [user_agent]: {user_agent}")

@app.get("/", summary="APIのヘルスチェック")
async def read_root():
    """
    APIサーバが正常に動作しているか確認するためのエンドポイントです．
    """
    return {"status": "ok", "message": "RMMA API is running!"}


@app.post("/agent", summary="Agentの使用")
async def run_agnet(request: AgentRequest):
    """
    指定されたプロンプトとエージェント名に基づいて，エージェントを実行します．
    """
    if not request.agent_name:
        raise HTTPException(status_code=400, detail="agent_name can't be None")

    if not request.prompt:
        raise HTTPException(status_code=400, detail="prompt can't be None")


    try:
            
        await async_content_generation(request.prompt)

        final_output = "完了しました"

        return {
            "status": "success",
            "message": "エージェントの実行が完了しました",
            "result": final_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エージェントの実行中にエラーが発生しました: {str(e)}")

@app.post("/agent/stream", summary="エージェントの応答をストリーミングで返す")
async def run_agent_stream(agent_request: AgentRequest, request: Request):
        """
        エージェントの実行プロセスをリアルタイムでクライアントにストリーミングします。
        """
        logger = get_logger("rmma")
        user_agent = request.headers.get("User-Agent", "Unknown")
        method = request.method
        request_url = str(request.url)
        log(logger, method, request_url, user_agent)
        # print("Recieve request")
        return StreamingResponse(
            stream_run_agent(agent_request.prompt),
            media_type="text/plain-stream"
        )



@app.post("/agent/stream/test", summary="エージェントの応答をストリーミングで返す")
async def run_agent_stream(agent_request: AgentRequest, request: Request):
        """
        エージェントの実行プロセスをリアルタイムでクライアントにストリーミングします。
        """
        logger = get_logger("rmma")
        user_agent = request.headers.get("User-Agent", "Unknown")
        method = request.method
        request_url = str(request.url)
        log(logger, method, request_url, user_agent)
        
        AM = AgentManager(agent_request.agent_name)

        return StreamingResponse(
            AM.generate_content(agent_request.prompt),
            media_type="text/plain-stream"
        )