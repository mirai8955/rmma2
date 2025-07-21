from prompt.prompt_manager import PromptManager
pm = PromptManager()
rmresearch_agent_prompt = pm.get_prompt("rmresearch_agent_prompt")

RMResearch_AGENT_PROMPT = f"""
{rmresearch_agent_prompt}
"""