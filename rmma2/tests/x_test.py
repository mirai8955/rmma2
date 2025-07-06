from rmma2.sub_agents.posting_agent.tools import x_client
from datetime import datetime


def x_api_test():
    client = x_client()
    response = client.tweet(f"これはテストです {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if response and "data" in response:
        tweet_id = response["data"]["id"]
        print(f"==> Successfully posted tweet. ID: {tweet_id}")
        print("==> Now attempting to fetch the tweet by its ID...")
        client.get_tweet_by_id(tweet_id)
    else:
        print("==> Failed to post tweet or extract ID from response.")


if __name__ == "__main__":
    x_api_test()