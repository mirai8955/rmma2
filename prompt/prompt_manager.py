from pathlib import Path
import yaml
from log.rmma_logger import get_logger

logger = get_logger()

class PromptManager:
    def __init__(self, path: str = "prompt/prompts.yaml"):
        self.path = Path(path)
        self.prompts = None

    def load_config(self) -> dict:
        # if self.prompts is None:
        with open(self.path, 'r', encoding='utf-8') as f:
            self.prompts = yaml.safe_load(f)
        return self.prompts

    def get_prompt(self, agent_name: str) -> str:
        prompts = self.load_config()
        return prompts['agents'][agent_name]

    def get_prompt_all(self) -> dict:
        prompts = self.load_config()
        return prompts

    def save_prompt(self, agent_name: str, new_prompt: str):
        prompts = self.load_config()
        logger.debug(f"saving prompt...{new_prompt}")

        if 'agents' not in prompts:
            prompts['agents'] = {}

        try:
            prompts['agents'][agent_name] = new_prompt
            with open(self.path, 'w', encoding="utf-8") as f:
                yaml.dump(prompts, f, sort_keys=False, allow_unicode=True, indent=2)
            logger.info(f"プロンプトの保存が成功しました: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"プロンプトの保存中にエラーが発生しました: {agent_name}, エラー: {str(e)}")
            return False
        
        

# test
if __name__ == "__main__":

    prompt_manager = PromptManager()
    print(prompt_manager.get_prompt)

    name = 'new_prompt'
    new_prompt = "新しいプロンプトです"

    prompt_manager.save_prompt(name, new_prompt)
    print(prompt_manager.get_prompt(name))

    print(prompt_manager.get_prompt_all())