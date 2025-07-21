
import os
from pathlib import Path
from log.rmma_logger import get_logger


logger = get_logger()

def read_file(filename: str) -> str:
    """
    ドキュメントとして保存してあるファイルを読み取る関数
    
    Args:
        filename (str): 読み取るファイル名（拡張子なし、.mdが自動で付加される）
        
    Returns:
        str: ファイルの内容
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    # .md拡張子を自動で付加
    md_filename = f"{filename}.md"
    
    # 現在のディレクトリからの相対パスを構築
    current_dir = Path(__file__).parent
    file_path = current_dir / md_filename
    
    # ファイル存在チェック
    if not file_path.exists():
        raise FileNotFoundError(f"ファイル '{md_filename}' が見つかりません")
    
    # ファイル読み取り
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"ファイル読み取りエラー: {str(e)}")

def write_file(filename: str, content: str) -> str:
    md_filename = f"{filename}.md"

    current_dir = Path(__file__).parent
    file_path = current_dir / md_filename

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # 書き込み後にファイルを読み込んで返却
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"ファイル書き込みエラー: {str(e)}")
            
def get_document_lists():
    """
    現在のディレクトリ配下の全てのMarkdownファイルの名前を拡張子なしで返す関数
    
    Returns:
        list[str]: .md拡張子を除いたファイル名のリスト
    """
    current_dir = Path(__file__).parent
    
    # .mdファイルを全て取得し、拡張子を除いたファイル名のリストを作成
    md_files = [f.stem for f in current_dir.glob("*.md")]
    
    return md_files


def doc_write(filename: str, content: str):
    """
    ドキュメントを保存する関数
    Args:
        filename: 拡張子無しのファイルの名前
        content: ドキュメントとして保存する内容
    Return:
        result: 保存された内容
    """
    logger.info(f"Writing file  with the filename:{filename}")
    doc_file = os.path.join("documents", f"{filename}.md")
    
    try:
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return content
    except Exception as e:
        logger.error(f"ドキュメントの保存中にエラーが発生しました: {doc_file}, エラー: {str(e)}")
        raise e