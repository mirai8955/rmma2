from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
from log.rmma_logger import get_logger
from rmma2.agent import rmma
import json
import importlib

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
        agent = self.find_agent(self.root_agent, agent_name)
        if agent:
            # エージェントのモジュール名を取得
            module_name = agent.__class__.__module__
            self.logger.info(f"Reload agent module: {module_name}")
            module = importlib.import_module(module_name)
            return importlib.reload(module)
        else:
            self.logger.error("Agent was not found.")
            return None
        
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

        if self.runner:
            events_async = self.runner.run_async(
                session_id=session.id, user_id="test", new_message=content
            )
            async for message in self.monitor_llm(events_async):
                yield message

        else:
            self.logger.error("Runner is not set")
            yield "Error: Runner is not set"



        

        
            
