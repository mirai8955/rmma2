"""posting agentのためのツール群"""
from dotenv import load_dotenv
import os
import json
import requests
import string
import secrets
import hashlib
import base64
import urllib.parse
import webbrowser
import http.server
from log.rmma_logger import get_logger

logger = get_logger()



### Regarding to X ###
class x_client:
    def __init__(self):
        load_dotenv()
        self.CLIENT_ID = os.getenv('X_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('X_CLIENT_SECRET')
        self.TOKEN_FILE = "x_tokens.json"
        self.TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
        self.PORT = 8000
        self.REDIRECT_URI = f"http://127.0.0.1:{self.PORT}/callback"
        self.SCOPE = "tweet.read tweet.write users.read offline.access"
        self.AUTH_URL = "https://twitter.com/i/oauth2/authorize"

        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError("X_CLIENT_ID and X_CLIENT_SECRET is not set")
        
    def _gen_pkce_pair(self):
        verifier = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64) ) 
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).rstrip(b"=").decode()
        return verifier, challenge

    def _build_authorize_url(self, challenge):
        params = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "scope": self.SCOPE,
            "state": secrets.token_urlsafe(16),
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    def _save_tokens(self, tok: dict):
        with open(self.TOKEN_FILE, "w") as fp:
            json.dump(tok, fp, indent=2)

    def _load_tokens(self):
        if not os.path.exists(self.TOKEN_FILE):
            return None
        return json.load(open(self.TOKEN_FILE))

    def _get_authorization_code(self, verifier, challenge):
        url = self._build_authorize_url(challenge)
        logger.info("Opening browser for consent...")
        webbrowser.open(url)
        with http.server.HTTPServer(("127.0.0.1", self.PORT), CallbackHandler) as httpd:
            while CallbackHandler.code is None:
                httpd.handle_request()
            return CallbackHandler.code

    def _token_request(self, data: dict):
        r = requests.post(self.TOKEN_URL, data=data, auth=(self.CLIENT_ID, self.CLIENT_SECRET), timeout=30) # type: ignore
        r.raise_for_status()
        return r.json()

    def exchange_code_for_tokens(self, code, verifier):
        return self._token_request({
            "grant_type": "authorization_code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "code": code,
            "code_verifier": verifier,
        })

    def refresh_tokens(self, refresh_token):
        return self._token_request({
            "grant_type" : "refresh_token",
            "client_id" : self.CLIENT_ID,
            "refresh_token": refresh_token,
        })

    def ensure_tokens(self):
        tok = self._load_tokens()
        if tok:
            tok = self.refresh_tokens(tok["refresh_token"])
            self._save_tokens(tok)
            logger.info("token is ensured!")
            return tok["access_token"]
        
        #first time flow
        return self.authenticate()

    def authenticate(self):
        verifier, challenge = self._gen_pkce_pair()
        code = self._get_authorization_code(verifier, challenge)
        tok = self.exchange_code_for_tokens(code, verifier)
        self._save_tokens(tok)
        return tok["access_token"]

    def check_result(self, result, content: str):
        logger.info(f"[X] tweet result: {result.status_code} {result.text}")

        if result.status_code == 403:
            logger.info("[X] 403 Error Details:")
            logger.info(f"    - Content length: {len(content)} characters")
            logger.info(f"    - Content preview: {content[:100]}...")
            logger.info("    - This might be due to:")
            logger.info("      1. App permissions not set to 'Read and Write'")
            logger.info("      2. Token scope insufficient")
            logger.info("      3. Content policy violation")


    def tweet(self, content: str):
        access_token = self.ensure_tokens()
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        r = requests.post("https://api.twitter.com/2/tweets", json={"text": content}, headers=headers, timeout=30)
        self.check_result(r, content)

        return r.json()
        

    def get_tweet_by_id(self, tweet_id: str):
        access_token = self.ensure_tokens()
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"https://api.twitter.com/2/tweets/{tweet_id}", headers=headers, timeout=30)
        logger.info(f"[X] get_tweet_by_id result: {r.status_code}")
        if r.ok:
            logger.info(f"[X] Fetched tweet data: {r.json()}")
        else:
            logger.info(f"[X] Failed to fetch tweet: {r.text}")
        return r

    def reply_to_tweet(self, content: str, tweet_id_to_reply_to: str):
        access_token = self.ensure_tokens()
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "text": content,
            "reply": {
                "in_reply_to_tweet_id": tweet_id_to_reply_to
            }
        }
        r = requests.post("https://api.twitter.com/2/tweets", json=payload, headers=headers, timeout=30)
        logger.info(f"[X] replied tweet: {r.status_code} {r.text}")
        if r.ok:
            return r.json()
        return None

    def search(self, query: str, max_results=10):
        access_token = self.ensure_tokens()
        headers = {"Authorization": f"Bearer {access_token}"}
        params  = {"query": query, "max_results": max_results, "tweet.fields": "author_id"}
        r = requests.get("https://api.twitter.com/2/tweets/search/recent", params=params, headers=headers, timeout=30)
        logger.info(f"[X] search result: {r.status_code} {r.json() if r.ok else r.text}")
        return r

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    code = None
    def do_GET(self):
        if self.path.startswith("/callback"):
            qs = urllib.parse.urlparse(self.path).query
            CallbackHandler.code = urllib.parse.parse_qs(qs)["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization complete! You can close this tab.")
        else:
            self.send_error(404)


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
    logger.info(f"Posting the content... {content}")
    
    # Twitter の文字数制限（280文字）を適用
    if len(content) > 280:
        content = content[:277] + "..."
        logger.info(f"Content truncated to 280 characters: {content}")
    
    x = x_client()
    r = x.tweet(content)
    
    if not r:
        logger.info(f"Failed to post: {r}")
        return None, content

    post_id = 1
    return post_id, content

def reply_on_x(content: str, tweet_id: str):
    """
    指定されたtweet_idの投稿に対して返信を行うツール。

    Args:
        content (str): 返信する投稿内容。
        tweet_id (str): 返信先のツイートID。

    Returns:
        dict | None: 投稿結果。成功すればツイート情報、失敗すればNone。
    """
    logger.info(f"Replying to tweet {tweet_id} with content: {content}")
    client = x_client()
    response = client.reply_to_tweet(content, tweet_id)
    return response

def search_on_x(query: str):
    """
    XのAPIを利用してXで投稿を検索するツール．

    Args:
        query: 検索時のキーワード
    
    Returns:
        content: json形式の検索結果
          
    """
    logger.info(f"Searching with query...{query}")
    x = x_client()
    r = x.search(query, max_results=10)

    if r.ok:
        return r.json()
    else:
        logger.info(f"Search failed: {r.status_code} {r.text}")
        return {"error": f"Search failed with status {r.status_code}"}




### 