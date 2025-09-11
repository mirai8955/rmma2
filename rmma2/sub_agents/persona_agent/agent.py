from google.adk.agents import LlmAgent
from .prompt import PERSONA_AGENT_PROMPT
from os import getenv
from dotenv import load_dotenv

load_dotenv()
MODEL_PRO = getenv("MODEL_PRO")

persona_agent = LlmAgent(
    name="PersonaAgent",
    model=MODEL_PRO or 'gemini-2.5-pro',
    description="Xのアカウントキャラクターを考えるエージェント",
    instruction=PERSONA_AGENT_PROMPT,
    output_key="persona_result"
)