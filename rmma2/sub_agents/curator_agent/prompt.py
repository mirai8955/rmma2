from prompt.prompt_manager import PromptManager
pm = PromptManager()
curator_agent_prompt = pm.get_prompt("curator_agent_prompt")

CURATOR_AGENT_PROMPT = f"""
{curator_agent_prompt}
"""