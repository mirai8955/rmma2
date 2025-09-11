from prompt.prompt_manager import PromptManager
pm = PromptManager()

persona_agent_prompt = pm.get_prompt("persona_agent_prompt")


PERSONA_AGENT_PROMPT=f"""
{persona_agent_prompt}
"""