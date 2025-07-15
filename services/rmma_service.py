from rmma2.agent_manager import AgentManager, get_agent_all
from fastapi import HTTPException
from log.rmma_logger import get_logger
from prompt.prompt_manager import PromptManager
from schemas.agent import AgentInfo

logger = get_logger()

def convert_camel_to_snake(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class RmmaService:
    def __init__(self):
        pass

    def get_agent_detail(self, agent_name) -> dict:
        agent_manager = AgentManager(agent_name)
        agent = agent_manager.get_agent(agent_name)
        
        if agent is None:
            raise HTTPException(status_code=404, detail=f"エージェント '{agent_name}' が見つかりません。利用可能なエージェント: {get_agent_all()}")
        
        # エージェントオブジェクトを辞書に変換
        agent_info = {
            "name": agent.name,
            "description": agent.description,
            "instruction": getattr(agent, 'instruction', None),
            "model": getattr(agent, 'model', 'Unknown'),
            "output_key": getattr(agent, 'output_key', None),
            "sub_agents": [sub_agent.name for sub_agent in getattr(agent, 'sub_agents', [])],
            "tools": [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in getattr(agent, 'tools', [])]
        }

        if not agent_info:
            logger.info(f"agent_info was not found with agent_name: {agent_name}")

        return agent_info

    def edit_agent_detail(self, agent_info: AgentInfo) -> AgentInfo:
        """Currently, only instruction of agent can be edited"""
        try:
            prompt_manager = PromptManager()
            agent_manager = AgentManager(agent_info.name)
            agent_name_snake = convert_camel_to_snake(agent_info.name) + "_prompt"
            if agent_info.instruction is not None:
                prompt_manager.save_prompt(agent_name_snake, agent_info.instruction)
            
            agent_info.instruction = prompt_manager.get_prompt(agent_name_snake)
            agent_manager.reload_agent_module(agent_info.name)
            return agent_info

        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            raise HTTPException(status_code=500, detail=f"エージェント情報の編集中にエラーが発生しました: {str(e)}")



        
