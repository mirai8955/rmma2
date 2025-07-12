import asyncio
import json

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.agent_tool import AgentTool
from rmma2.agent import rmma 


def find_agent(agent, targat_name):

    result = None
    print("Matching...", agent.name)
    if agent.name==targat_name:
        return agent
    for sub_agent in agent.sub_agents:
        print("Searching...", )
        result = find_agent(sub_agent, targat_name)
        if result:
            break
    for tool in agent.tools:
        if isinstance(tool, AgentTool):
            result = find_agent(tool.agent, targat_name)
            if result:
                break
    return result


def get_agent():
    print("Inserting Agent")

    root_agent = rmma
    creator = find_agent(root_agent, "posting_agent")
    if creator:
        print("FOUND", creator.name)
    else:
        print("NOT FOUND")
    return root_agent

def get_agent_by(agent):
    print("Inserting Agent")
    root_agent = agent
    found_agent = find_agent(root_agent, "rakuten_mobile_marketing_agent")
    if found_agent:
        print("FOUND", found_agent.name)
    else:
        print("NOT FOUND")
    return root_agent


async def stream_run_agent(prompt: str):
    try:
        yield "rmmaの実行を開始します...\n"
        print("rmmaの実行を開始")
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        agent = get_agent_by(rmma)

        session = await session_service.create_session(
            state={}, app_name='rmma', user_id="user1"
        )

        yield f"Created session with ID: {session.id}"
        print(f"Created session with ID: {session.id}")

        yield f"[user]: {prompt}"
    
        content = types.Content(role="user", parts=[types.Part(text=prompt)])

        runner = Runner(
            app_name="rmma",
            agent=agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        events_async = runner.run_async(
            session_id=session.id, user_id="user1", new_message=content
        )

        async for event in events_async:
            if not event.content:
                continue
            author = event.author

            function_calls = [
                e.function_call for e in event.content.parts if e.function_call
            ]

            function_responses = [
                e.function_response for e in event.content.parts if e.function_response
            ]

            if event.content.parts[0].text:
                text_response = event.content.parts[0].text
                yield f"\n[{author}]: {text_response}"
                print(f"\n[{author}]: {text_response}")

            if function_calls:
                for function_call in function_calls:
                    yield f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)})"
                    print(f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)})")

        yield "プロセスが正常に終了しました．"

    except Exception as e:
        error_json = json.dumps({
            "type": "error",
            "message": "エージェント実行中にエラーが発生しました．",
            "detail": str(e)
        })
        yield f"event: error\ndata: {error_json}\n\n"


async def async_content_generation(prompt):
    
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

    async for event in events_async:
        
        if not event.content:
            continue

        author = event.author

        function_calls = [
            e.function_call for e in event.content.parts if e.function_call
        ]

        function_responses = [
            e.function_response for e in event.content.parts if e.function_response
        ]

        if event.content.parts[0].text:
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

    #debug 1
    # asyncio.run(
    #     async_content_generation(
    #         "Please generate the content of tweet. Just only generate the content."
    #     )
    # )

    #debug 2
    asyncio.run(
        async_content_generation(
            "Please generate the content of tweet and post it on X. please use tool calling."
        )
    )