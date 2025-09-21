## ADK Instruction/Prompt 運用Tips

- InstructionProvider の型
```python
# google/adk/agents/llm_agent.py より
InstructionProvider: TypeAlias = Callable[[ReadonlyContext], Union[str, Awaitable[str]]]
```
  - instruction は「文字列」または「関数（ctxを1引数、同期/非同期どちらも可）」
  - ADKは実行時に `self.instruction(ctx)` を呼ぶ（文字列ならそのまま使用）

- 推奨シグネチャ（安全形）
```python
def get_prompt(ctx=None, *args, **kwargs) -> str:
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt("your_prompt_key")
# 渡す時は関数オブジェクトのまま: instruction=get_prompt
```

- よくある落とし穴
  - `instruction=pm.get_prompt("key")` とすると「即実行→文字列固定化」になる（キャッシュ問題再発）
  - 関数に `ctx` を受け口として用意しないと TypeError（ADK側が `instruction(ctx)` で呼ぶ）

- ctx を使う主な目的
  - 実行時の文脈でプロンプトを動的生成（セッション状態、履歴長、ロケール、権限、ABテスト 等）
  - 非同期ソースから設定/フラグ取得（Awaitable[str]対応）

### 代表的な実装パターン

- ペルソナで切替
```python
def get_prompt(ctx=None):
    st = (getattr(ctx, "state", {}) or {})
    persona = st.get("persona", "default")
    key = f"{persona}_agent_prompt"
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt(key)
```

- ロケールで切替
```python
def get_prompt(ctx=None):
    st = (getattr(ctx, "state", {}) or {})
    locale = st.get("locale", "ja")
    base = "rakuten_mobile_marketing_agent_prompt"
    key = f"{base}_{locale}"
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt(key)
```

- 履歴/使用トークン量で軽量版へフェイルオーバー
```python
def get_prompt(ctx=None):
    st = (getattr(ctx, "state", {}) or {})
    usage = st.get("token_usage", 0)
    key = ("rakuten_mobile_marketing_agent_prompt_light"
           if usage > 20000 else "rakuten_mobile_marketing_agent_prompt")
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt(key)
```

- A/Bテスト（バリアント固定）
```python
def get_prompt(ctx=None):
    st = (getattr(ctx, "state", {}) or {})
    variant = st.get("ab_variant")
    if not variant:
        import random
        variant = random.choice(["A", "B"])
        st["ab_variant"] = variant
    key = f"posting_agent_prompt_{variant}"
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt(key)
```

- 非同期に外部設定取得
```python
import asyncio

async def fetch_flags():
    # 外部サービス/DBから取得する想定
    return {"short_copy": True}

async def get_prompt(ctx=None):
    flags = await fetch_flags()
    key = "posting_agent_prompt_short" if flags.get("short_copy") else "posting_agent_prompt"
    from prompt.prompt_manager import PromptManager
    return PromptManager().get_prompt(key)
```

- 再利用できるファクトリ
```python
def make_instruction(base_key: str):
    def provider(ctx=None):
        st = (getattr(ctx, "state", {}) or {})
        locale = st.get("locale", "ja")
        key = f"{base_key}_{locale}"
        from prompt.prompt_manager import PromptManager
        return PromptManager().get_prompt(key)
    return provider

# 例: instruction = make_instruction("rakuten_mobile_marketing_agent_prompt")
```

### 表示/API側の注意
- 表示用APIで instruction を返す場合、関数ならその場で実行して文字列に解決
```python
val = getattr(agent, "instruction", None)
text = val(ctx) if callable(val) else val
```
- ブラウザ/プロキシキャッシュ無効化（JSONResponseでヘッダ付与）
```python
headers = {"Cache-Control": "no-cache, no-store, must-revalidate",
           "Pragma": "no-cache", "Expires": "0"}
```

### ドキュメントI/O 設計メモ
- Repository パターンで責務分離
  - `DocumentRepository` 抽象: read/write/list
  - `LocalDocumentRepository(root)` 実装: ルート固定・フォルダはホワイトリスト（persona/research 等）
  - パス正規化と検証でディレクトリトラバーサル防止
- Tool は Repository の薄いファサード（引数スキーマ明確化）

### チェックリスト
- [ ] instruction は関数オブジェクトを渡す（呼ばない）
- [ ] 関数は `ctx=None` を受け取れる
- [ ] 表示/APIは常に最新を返す（関数なら実行）
- [ ] レスポンスキャッシュを無効化
- [ ] ドキュメントI/Oは安全なRepository経由
