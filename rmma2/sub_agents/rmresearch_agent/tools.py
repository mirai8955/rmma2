from log.rmma_logger import get_logger
import os
from documents.document import doc_write, read_file

# logger = get_logger()
# current_dir = os.getcwd()
# def doc_write(filename: str, content: str):
#     """
#     ドキュメントを保存する関数
#     Args:
#         filename: 拡張子無しのファイルの名前
#         content: ドキュメントとして保存する内容
#     Return:
#         result: 保存された内容
#     """
#     logger.info(f"Writing file  with the filename:{filename}")
#     doc_file = os.path.join("documents", f"{filename}.md")
    
#     try:
#         with open(doc_file, 'w', encoding='utf-8') as f:
#             f.write(content)
#         return content
#     except Exception as e:
#         logger.error(f"ドキュメントの保存中にエラーが発生しました: {doc_file}, エラー: {str(e)}")
#         raise e
    

        

        
