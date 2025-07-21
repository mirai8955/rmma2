from log.rmma_logger import get_logger
import os


logger = get_logger()
current_dir = os.getcwd()
def doc_write(filename: str, content: str):
    """
    ドキュメントを保存する関数
    Args:
        filename: 拡張子無しのファイルの名前
        content: ドキュメントとして保存する内容
    Return:
        result: 保存された内容
    """

    doc_file = os.path.join(current_dir, f"{filename}.md")
    
    try:
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return content
    except Exception as e:
        logger.error(f"ドキュメントの保存中にエラーが発生しました: {doc_file}, エラー: {str(e)}")
        raise e
    

        

        
