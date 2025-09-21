from google.adk.agents import LlmAgent
from .prompt import PERSONA_AGENT_PROMPT
from os import getenv
from dotenv import load_dotenv
from documents.document import doc_write
from prompt.prompt_manager import PromptManager

load_dotenv()
MODEL_PRO = getenv("MODEL_PRO")

def get_prompt(ctx=None):
    pm = PromptManager()
    return pm.get_prompt('persona_agent_prompt')


persona_agent = LlmAgent(
    name="PersonaAgent",
    model=MODEL_PRO or 'gemini-2.5-pro',
    description="Xのアカウントキャラクターを考えるエージェント",
    instruction=get_prompt,
    output_key="persona_result",
    tools=[ doc_write],
)