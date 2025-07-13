from rmma2.sub_agents.posting_agent.tools import x_client
from log.rmma_logger import get_logger

def main():
    """X APIクライアントを初期化する"""
    logger = get_logger()
    
    try:
        client = x_client()
        access_token = client.ensure_tokens()
        
        if access_token:
            logger.info("X APIの初期化が正常に完了しました")
            print("X APIの初期化が終了しました．")
            return True
        else:
            logger.info("X APIの初期化に失敗しました - アクセストークンが取得できませんでした")
            print("X APIの初期化が失敗しました")
            return False
            
    except Exception as e:
        logger.info(f"X APIの初期化中にエラーが発生しました: {str(e)}")
        print(f"X APIの初期化が失敗しました: {str(e)}")
        return False

if __name__ == "__main__":
    main()

