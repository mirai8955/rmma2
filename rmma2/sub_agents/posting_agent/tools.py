"""posting agentのためのツール群"""


def post(content):
    return 1

def post_on_x(content: str):
    """
    XのAPIを利用してXで投稿するツール．

    Args:
        content: 投稿する投稿内容
    
    Returns:
        post_id: 投稿されたポストのid
        content: 投稿内容    
    """
    print("Posting the content...", content)
    
    post_id = post(content)

    return post_id, content