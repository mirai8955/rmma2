"""test reply agent search and content generation only"""

import asyncio
import json

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.agent_tool import AgentTool
from rmma2.agent import rmma 


def find_agent(agent, target_name):

    result = None
    print("Matching...", agent.name)
    if agent.name==target_name:
        return agent
    for sub_agent in agent.sub_agents:
        print("Searching...", )
        result = find_agent(sub_agent, target_name)
        if result:
            break
    # for tool in agent.tools:
    #     if isinstance(tool, AgentTool):
    #         result = find_agent(tool.agent, target_name)
    #         if result:
    #             break
    return result


def get_agent():
    print("Inserting RMMA Agent")
    root_agent = rmma
    creator = find_agent(root_agent, "rmma")
    if creator:
        print("FOUND", creator.name)
    else:
        print("NOT FOUND")
    return root_agent


async def async_execute_reply_agent(prompt):
    
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    agent = get_agent()
    
    session = await session_service.create_session(
        state={}, app_name="rmma", user_id="rmma01"
    )
    
    print(f"Created session with ID: {session.id}")

    query = prompt
    print("[user]: ", query)
    content = types.Content(role="user", parts=[types.Part(text=query)])

    runner = Runner(
        app_name="rmma",
        agent=agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    events_async = runner.run_async(
        session_id=session.id, user_id="rmma01", new_message=content
    )

    total_token = 0
    async for event in events_async:
        
        if not event.content:
            continue

        author = event.author

        function_calls = [
            e.function_call for e in (event.content.parts or []) if e.function_call
        ]
        function_responses = [
            e.function_response for e in (event.content.parts or []) if e.function_response
        ]

        if event.usage_metadata:
            total_token = event.usage_metadata.total_token_count
            print("Total token is ", total_token)

        if event.content.parts and event.content.parts[0].text:
            text_response = event.content.parts[0].text
            print(f"\n[{author}]: {text_response}")

        if function_calls:
            for function_call in function_calls:
                print(
                    f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)})"
                )

        # elif function_responses:
        #     for function_response in function_responses:
        #         function_name = function_response.name
        #         application_payload = function_response.text_response
        #         if  function_name == "airbnb_search":
        #             application_payload = application_payload["result"].content[0].text
                    
        #         print(
        #             f"\n[{author}]: {function_name} responds -> {application_payload}"
        #         )


if __name__ == "__main__":


    #debug 4
    asyncio.run(
        async_execute_reply_agent(
            "楽天モバイルの潜在顧客をXの投稿から探して，その投稿内容に対する返信を考えてほしい."
            "そして，実際に返信を行なってほしい．"
        )
    )