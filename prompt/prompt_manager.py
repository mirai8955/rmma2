from pathlib import Path
import yaml
class PromptManager:
    def __init__(self, path: str = "prompt/prompts.yaml"):
        self.path = Path(path)
        self.prompts = None

    def load_config(self) -> dict:
        # if self.prompts is None:
        with open(self.path, 'r', encoding='utf-8') as f:
            self.prompts = yaml.safe_load(f)
        return self.prompts

    def get_prompt(self, name: str) -> str:
        prompts = self.load_config()
        return prompts['agents'][name]

    def get_prompt_all(self) -> dict:
        prompts = self.load_config()
        return prompts

    def save_prompt(self, name: str, new_prompt: str):
        prompts = self.load_config()

        if 'agents' not in prompts:
            prompts['agents'] = {}

        prompts['agents'][name] = new_prompt
        with open(self.path, 'w', encoding="utf-8") as f:
            yaml.dump(prompts, f, sort_keys=False, allow_unicode=True, indent=2)
        
        

# test
if __name__ == "__main__":

    prompt_manager = PromptManager()
    print(prompt_manager.get_prompt)

    name = 'new_prompt'
    new_prompt = "新しいプロンプトです"

    prompt_manager.save_prompt(name, new_prompt)
    print(prompt_manager.get_prompt(name))

    print(prompt_manager.get_prompt_all())