from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
from log.rmma_logger import get_logger
from rmma2.agent import rmma
import json
import importlib
import traceback

def find_agent(array, agent):
    array.append(agent.name)
    for sub_agent in agent.sub_agents:
        find_agent(array, sub_agent)
    return array

def get_agent_all():
    result = []
    root_agent = rmma
    find_agent(result, root_agent)
    return result

class AgentManager:
    def __init__(self, agent_name: str):
        self.runner = None
        self.root_agent = rmma
        self.logger = get_logger()
        self.agent = self.get_agent(agent_name)
        self.agent_name = agent_name
        
    def find_agent(self, agent, target_name):
        result = None
        # self.logger.info(f"Matching...{agent.name}")
        if agent.name ==  target_name:
            return agent
        for sub_agent in agent.sub_agents:
            # self.logger.info(f"Searching...{sub_agent.name}")
            result = self.find_agent(sub_agent, target_name)
            if result:
                break
        return result

    def get_agent(self, agent_name):
        # self.logger.info("Inserting Agent")
        agent = self.find_agent(self.root_agent, agent_name)
        if agent:
            # self.logger.info("Agent found")
            return agent
        else:
            self.logger.error("Agent was not found.")
            return None

    def reload_agent_module(self, agent_name):
        # 対象エージェントの存在確認（現在のツリー上）
        agent = self.find_agent(self.root_agent, agent_name)
        if not agent:
            self.logger.error("Agent was not found.")
            return False

        # エージェント名から自前のモジュールパスを決定
        if agent_name == self.root_agent.name:
            agent_module_name = self.root_agent.__class__.__module__
            base_path, _ = agent_module_name.rsplit('.', 1)
            prompt_module_name = f"{base_path}.prompt"
        if agent_name == "RMMA":
            agent_module_name = "rmma2.agent"
            prompt_module_name = "rmma2.prompt"
        else:
            snake_case_name = self._convert_to_snake_case(agent_name)
            agent_module_name = f"rmma2.sub_agents.{snake_case_name}.agent"
            prompt_module_name = f"rmma2.sub_agents.{snake_case_name}.prompt"

        self.logger.info(f"Reload target -> agent: {agent_module_name}, prompt: {prompt_module_name}")

        # 1) プロンプトモジュールを先にリロード
        try:
            prompt_module = importlib.import_module(prompt_module_name)
            importlib.reload(prompt_module)
            self.logger.info(f"Reloaded prompt module: {prompt_module_name}")
        except ModuleNotFoundError:
            self.logger.warning(f"Prompt module not found: {prompt_module_name}")
        except Exception as e:
            self.logger.error(f"Failed to reload prompt module: {prompt_module_name}: {e}\n{traceback.format_exc()}")
            return False

        # 2) エージェントモジュールをリロード（新しい instruction で再構築される）
        try:
            agent_module = importlib.import_module(agent_module_name)
            importlib.reload(agent_module)
            self.logger.info(f"Reloaded agent module: {agent_module_name}")
        except ModuleNotFoundError:
            self.logger.error(f"Agent module not found: {agent_module_name}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to reload agent module: {agent_module_name}: {e}\n{traceback.format_exc()}")
            return False


        return True
        # # 3) ルート集約モジュールをリロードし、root_agent と self.agent を差し替える
        try:
            root_module = importlib.import_module("rmma2.agent")
            importlib.reload(root_module)
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload root rmma2.agent: {e}\n{traceback.format_exc()}")
            return False

    def _convert_to_snake_case(self, camel_case_name):
        import re
        name = camel_case_name.replace("Agent", "")
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return f"{snake_case}_agent"
        
    async def create_session_and_services(self):
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()

        session = await session_service.create_session(
            state={}, app_name=self.agent_name, user_id="test"
        )
        self.logger.info(f"Created session with ID: {session.id}")

        return session, session_service, artifacts_service


    async def set_runner(self, prompt, agent_name, session_service, artifacts_service):
        

        runner = Runner(
            app_name=self.agent_name,
            agent=self.agent if self.agent else self.root_agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        self.runner = runner
        self.logger.info("Runner set.")

    async def monitor_llm(self, events_async):

        async for event in events_async:
                if not event.content:
                    continue
                author = event.author

                function_calls = [
                    e.function_call for e in event.content.parts if e.function_call
                ] if event.content.parts else []

                if event.usage_metadata:
                    total_token = event.usage_metadata.total_token_count
                    yield f"Total token is {total_token}"
                    self.logger.info(f"Total token is {total_token}")

                if event.content.parts and event.content.parts[0].text:
                    text_response = event.content.parts[0].text
                    self.logger.info(f"\n[{author}]: {text_response}")
                    yield f"\n[{author}]: {text_response}"

                if function_calls:
                    for function_call in function_calls:
                        message = f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args, ensure_ascii=False)})"
                        self.logger.info(message)
                        yield message



    async def run_stream_agent(self, prompt: str):
        """Generate tweet content with posting_agent"""

        yield f"[agent] Starting {self.agent_name} execution\n"

        session, session_service, artifacts_service = await self.create_session_and_services()

        await self.set_runner(prompt, self.agent_name, session_service, artifacts_service)

        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        try:
            if self.runner:
                events_async = self.runner.run_async(
                    session_id=session.id, user_id="test", new_message=content
                )
                async for message in self.monitor_llm(events_async):
                    yield message

            else:
                self.logger.error("Runner is not set")
                yield "Error: Runner is not set"

        except Exception as e:
            self.logger.exception("Streaming faild")
            yield f"Error: {e}"




        

        
            
