from google.adk.agents import LlmAgent, SequentialAgent
from .prompt import RMMA_REPLY_PROMPT,  TWEET_SEARCH_AGENT_PROMPT
from os import getenv
from dotenv import load_dotenv
from .tools import post_on_x, search_on_x, reply_on_x

load_dotenv()
MODEL = getenv("MODEL")

tweet_search_agent = LlmAgent(
    name="TweetSearchAgent",
    model=MODEL,
    description="XのAPIを使用して投稿を検索するエージェント",
    instruction=TWEET_SEARCH_AGENT_PROMPT,
    output_key="search_result",
    tools=[search_on_x],
)

# arrange_schema_agent = LlmAgent(
#     name="ArrangeSchemaAgent",
#     model=MODEL,
#     description="与えられた検索結果を整形して出力します"，
#     instructions="""
#     jsonで投稿の検索結果が与えられます．それらを全てTEXTの形に変更し，
#     一つの出力にまとめてください
#     """
#     output_schema=
# )

reply_generation_agent = LlmAgent(
    name="ReplyGenerationAgent",
    model=MODEL,
    description="検索結果から楽天モバイルをおすすめする返信を考えるエージェント",
    instruction="""
    あなたは優秀なマーケターであるだけでなく，優秀な返信エージェントです．
    あなたの目的はより多くの人に楽天モバイルに興味を持ってもらうように，Xの投稿に返信する内容を考慮することです．
    
    **タスク**
    検索結果が以下のように与えられます.

    ```
    検索結果例
    {
  "data": [
    {
      "id": "1942892737012937161",
      "author_id": "1534061802727694336",
      "edit_history_tweet_ids": [
        "1942892737012937161"
      ],
      "text": "ツイートの内容"
    },
    {
      "id": "1940393772866544049",
      "author_id": "1383744030190702596",
      "edit_history_tweet_ids": [
        "1940393772866544049"
      ],
      "text": "携帯料金、「よくわからない、他も同じかな、なんとなくそのまま」で高いスマホ代を払い続けていませんか？\n楽天モバイルならデータ使い放題で月3,278円！番号そのまま乗り換えで楽天ポイント14,000Pも！\nhttps://t.co/A1UgKiwRvD\nから楽天ログイン後、申し込みで従業員優待適用\n#お得 #節約 #役立つ https://t.co/CfuU2JBaYf"
    }
  ],
  "meta": {
    "newest_id": "1942892737012937161",
    "oldest_id": "1940393772866544049",
    "result_count": 8
  }
}
    ```
    この検索結果から返信することで，楽天モバイルに興味がある人から多くのインプレッションを得られるであろう投稿を一つ選択してください．
    そしてその投稿に対して，多くの人が楽天モバイルに興味を持ってもらうような返信内容を生成してください．
    返信内容は信頼性と親しみやすさを兼ね備えた文章です．
    虚偽の発言は控えており，必ず事実が確認できる内容の返信しか生成しません．
    返信文になる文章と返信する投稿の情報のみをoutputとし，
    他の余計な文字列をoutputには含まないようにしてください．
    また，返信文は200文字以内にしてください．

    **検索結果**
    ```
    {search_result}
    ```

    """,
    output_key="reply_content"
)

reply_post_agent = LlmAgent(
    name="ReplyPostAgent",
    model=MODEL,
    description="生成した文章で実際に返信を実行するエージェント",
    instruction="""
    あなたは，前のエージェントが生成した返信文を用いて，対象の投稿に返信します．
    前のエージェントからのアウトプットには返信対象となる投稿と返信文が出力されます．
    reply_on_xというツールのcontentという引数には，
    必ず前のエージェントが生成した返信文のみを入力してください．

    **返信内容**
    {reply_content}

    """,
    tools=[reply_on_x],
)

reply_pipeline_agent = SequentialAgent(
    name="ReplyPipelineAgent",
    # model=MODEL,
    description="Xから該当する投稿を検索し，返信内容を考え，返信するエージェント",
    # instruction=RMMA_REPLY_PROMPT,
    sub_agents=[tweet_search_agent, reply_generation_agent, reply_post_agent],
)

# root_agent = reply_pipeline_agent