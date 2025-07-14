from pydantic import BaseModel
from typing import Optional

class AgentInfo(BaseModel):
    name: str
    description: str
    instruction: Optional[str] = None
    model: str = "Unknown"
    output_key: Optional[str] = None
    sub_agents: list[str] = []
    tools: list[str] = []