from google.adk.agents import LlmAgent, SequentialAgent
from .prompt import REPLY_GENERATION_AGENT, RMMA_REPLY_PROMPT,  TWEET_SEARCH_AGENT_PROMPT, REPLY_POST_AGENT
from os import getenv
from dotenv import load_dotenv
from rmma2.sub_agents.posting_agent.tools import search_on_x, reply_on_x
from prompt.prompt_manager import PromptManager

load_dotenv()
MODEL = getenv("MODEL")

def get_prompt_tsa():
    pm = PromptManager()
    return pm.get_prompt('tweet_search_agent')

def get_prompt_rga():
    pm = PromptManager()
    return pm.get_prompt('reply_generation_agent')

def get_prompt_rpa():
    pm = PromptManager()
    return pm.get_prompt('reply_post_agent')


tweet_search_agent = LlmAgent(
    name="TweetSearchAgent",
    model=MODEL or "gemini-2.5-flash",
    description="XのAPIを使用して投稿を検索するエージェント",
    instruction=get_prompt_tsa,
    output_key="search_result",
    tools=[search_on_x],
)

reply_generation_agent = LlmAgent(
    name="ReplyGenerationAgent",
    model=MODEL or "gemini-2.5-flash",
    description="検索結果から楽天モバイルをおすすめする返信を考えるエージェント",
    instruction=get_prompt_rga,
    output_key="reply_content"
)

reply_post_agent = LlmAgent(
    name="ReplyPostAgent",
    model=MODEL or "gemini-2.5-flash",
    description="生成した文章で実際に返信を実行するエージェント",
    instruction=get_prompt_rpa,
    tools=[reply_on_x],
)

reply_pipeline_agent = SequentialAgent(
    name="ReplyPipelineAgent",
    description="Xから該当する投稿を検索し，返信内容を考え，返信するエージェント",
    sub_agents=[tweet_search_agent, reply_generation_agent, reply_post_agent],
)

