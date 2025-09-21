## 学習メモ（プロンプト更新が反映されない／エージェント未検出）

- 原因1（エージェント未検出）: ルート `rmma` の `sub_agents` に `persona_agent` が未登録だった。
  - 対応: `rmma2.agent` で `persona_agent` を import し、`sub_agents` に追加。

- 原因2（フロントに古いプロンプトが表示）: `prompt.py` でモジュール読込時に `PromptManager` から文字列を取得して固定化＝キャッシュされるため。
  - 連鎖: `reload_agent_module` が `agent.py` だけをリロードし、`prompt.py` はリロードしていなかった。
  - 対応: `agent_manager.reload_agent_module` を拡張し、対応する `prompt` モジュールもリロード。`prompt.py` は関数経由で都度 `PromptManager` から取得する形に変更（動的取得）。

- 追加の運用tip: `GET /agent/{agent_name}` の `instruction` を返すとき、エージェントインスタンスの保持値ではなく `PromptManager` から最新YAMLを取り直すとズレを防げる。

- ポート競合の原因: `uvicorn` を `Ctrl+Z` でサスペンド（状態=T）し、プロセスが 8000 を保持していた。
  - 確認/解放: `lsof -ti:8000` → `kill -9 <pid>`、または別ポートで起動。

- 設計メモ: `persona_agent` は高性能モデル用に `MODEL_PRO`（例: `gemini-2.5-pro`）を使う設計。他エージェントは `MODEL`（例: `gemini-2.5-flash`）。

- `__init__.py` について: パッケージのエクスポート整理に有用だが必須ではない。必要なときのみ `__all__` を定義。


## ホットリロード時の Pydantic 親子関係エラー

- **問題**: プロンプト更新時のホットリロード処理で `importlib.reload()` を使用した際、`pydantic.ValidationError: Agent ... already has a parent agent` が発生した。

- **原因**: `importlib.reload()` は、指定されたモジュールのコードを再実行し、既存のモジュールオブジェクトの内容を上書きする。親エージェントモジュール (`rmma2.agent`) をリロードすると、新しい親エージェントが生成される。しかし、その時点で子エージェントのモジュールはリロードされていないため、子エージェントのオブジェクトは古い親への参照を保持したままである。新しい親が、すでに親を持つ子を自身の `sub_agents` として登録しようとしたため、ADK (`LlmAgent`) が内部で使用している Pydantic の検証ルールに抵触し、エラーとなった。

- **解決策**: リロードの順序を厳密に制御する。
    1.  **全ての子エージェントを先にリロードする**: 親をリロードする前に、全ての子エージェントのモジュール (`*.agent.py` と `*.prompt.py`) をリロードする。これにより、全ての子エージェントが「親を知らない」クリーンな状態で再生成される。
    2.  **親エージェントをリロードする**: 全ての子がクリーンになった後で、親エージェントのモジュール (`rmma2.agent`) をリロードする。これにより、新しい親がクリーンな子を使ってエージェントツリーを正常に再構築できる。
    3.  **参照を更新する**: 最後に、`AgentManager` などが保持しているエージェントへの参照を、新しく作られたオブジェクトツリーに差し替える。

## カスタムロガーでのスタックトレース出力

- **問題**: `try...except` ブロックで例外を捕捉し `logger.error()` でログを出力しても、エラーのスタックトレースがログファイルにもターミナルにも表示されなかった。また、`logger.exception()` や `logger.error(exc_info=True)` を使用すると `AttributeError` や `TypeError` が発生した。

- **原因**: `log/rmma_logger.py` でセットアップされたカスタムロガーが、Python 標準の `logging.Logger` のインターフェース（`exception` メソッドや `exc_info` 引数）に完全には準拠していなかったため。FastAPI の例外ミドルウェアがエラーを捕捉した後、このカスタムロガーに処理が渡るが、スタックトレースを出力する機能が呼び出せていなかった。

- **解決策**: `traceback` モジュールを使い、スタックトレースを手動で取得してログメッセージに含める。
    ```python
    import traceback
    
    try:
        # ... some code that might fail ...
    except Exception as e:
        # traceback.format_exc()でスタックトレースを文字列として取得
        logger.error(f"An error occurred: {e}\n{traceback.format_exc()}")
    ```


## 設計改善：動的プロンプトによるホットリロードの代替

- **問題**: プロンプトの変更を即時反映させるために `importlib.reload()` を使うアプローチは、親子関係エラーなど複雑な副作用が多く、堅牢な実装が非常に難しい。

- **根本原因**: **状態（データ）とコードの密結合**。プロンプトという「データ」を、モジュール内のグローバル変数という「コード」の一部として定義していた。これにより、Pythonのモジュールキャッシュ機構の制約を直接受けてしまい、プロンプトがモジュール読み込み時に固定化されていた。

- **より優れた解決策（学習したこと）**: **状態とコードを分離し、プロンプトを実行時に関数経由で動的に取得する。**
    1.  **ADKの設計**: `LlmAgent` の `instruction` 引数は、文字列だけでなく**関数（Callable）**も受け入れるように設計されている。これは、まさにキャッシュによるデータの固定化を避けるための仕組みである。
    2.  **仕組み**:
        -   `instruction` に**関数オブジェクト**を渡すと、エージェントのインスタンス化の時点ではその関数は実行されない。
        -   エージェントが**実際に実行される段階**で、ADKの内部ロジックが `instruction` が関数であると判断し、その関数を**呼び出す**。
        -   関数の戻り値（プロンプト文字列）が、その場で生成されて利用される。
    3.  **実装**: 各 `prompt.py` でプロンプトを返す関数を定義し (`def get_prompt(): ...`)、`agent.py` で `LlmAgent(instruction=get_prompt)` のように関数そのものを渡す。

- **結論**: この設計に変更することで、`importlib.reload()` という複雑でエラーの温床となる仕組みを完全に排除できる。プロンプト（データ）は `prompts.yaml` に、ロジックは `agent.py` にと綺麗に分離され、プロンプトの変更はエージェントの次回の実行時に自動で反映されるようになり、はるかにクリーンで堅牢な設計になる。


## ADK 自動Function Callingとシグネチャ設計（要約）
- 問題: Optional/Union（例: `folder: str | None = None`）が自動JSON Schema生成で失敗し ValueError。 
- 一般化: フレームワークの自動スキーマ生成とIDL境界の不一致。required/nullableの曖昧さはLLMの引数合成を不安定化（省略/null/空文字の選択が揺れる）。
- 原因: ADKは単純型前提でスキーマ化。Union/nullableはrequired判定やnull/省略の意味付けが衝突しやすい。
- 解決: 公開シグネチャを単純化し自動生成に寄せる。
  - `folder: str = ""`（未指定は空文字）にする、または関数を分割（`read_document` / `read_persona_document`）。
  - 返却型はJSON直列可能な単純型に統一（str/list[str]/dict）。
  - 必要ならFunctionToolに明示スキーマを付与（enum等）。
  - Toolの外向きシグネチャから Optional/Union/ctx/**kwargs を排除し、内部で正規化・検証。


