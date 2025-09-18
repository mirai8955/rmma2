
import os
from pathlib import Path
import importlib
import sys
from log.rmma_logger import get_logger


logger = get_logger()

def read_file(filename: str, folder: str | None = None) -> str:
    """
    ドキュメントとして保存してあるファイルを読み取る関数
    
    Args:
        filename (str): 読み取るファイル名（拡張子なし、.mdが自動で付加される）
        folder (str | None): サブフォルダ名（指定されない場合は現在のディレクトリ）
        
    Returns:
        str: ファイルの内容
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    logger.info(f"Reading file: {filename}")

    # .md拡張子を付加
    if not filename.endswith('.md'):
        filename = f"{filename}.md"

    if folder:
        md_filename = f"{folder}/{filename}"
    else:
        md_filename = filename
    
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

        # 書き込み完了をログに記録
        logger.info(f"ファイル書き込み完了: {md_filename}")

        # 書き込み後にファイルを読み込んで返却
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"ファイル書き込みエラー: {str(e)}")
            
def get_document_lists(folder: str | None = None):
    """
    現在のディレクトリ配下の全てのMarkdownファイルの名前を拡張子なしで返す関数
    
    Args:
        folder (str | None): サブフォルダ名（指定されない場合は現在のディレクトリ）
    
    Returns:
        list[str]: .md拡張子を除いたファイル名のリスト
    """
    current_dir = Path(__file__).parent
    
    # folderが指定されている場合はサブフォルダを対象にする
    if folder:
        target_dir = current_dir / folder
    else:
        target_dir = current_dir
    
    # ディレクトリが存在しない場合は空のリストを返す
    if not target_dir.exists():
        raise FileNotFoundError(f"ディレクトリ '{target_dir}' が見つかりません")
    
    # .mdファイルを全て取得し、拡張子を除いたファイル名のリストを作成
    md_files = [f.stem for f in target_dir.glob("*.md")]
    
    return md_files

def doc_write(content: str, filename: str):
    """
    ドキュメントを保存する関数．
    注意：調査結果などを保存する際にはルートディレクトリであるdocumentsフォルダにその内容が保存される.この場合は引数folderには何も指定しない．
    Args:
        content: ドキュメントとして保存する内容
        filename: 拡張子無しのファイルの名前
    Return:
        result: 保存された内容
    """

    folder = "persona"
    logger.info(f"Writing file with the filename:{filename}")
    if folder == 'persona':
        doc_file = os.path.join("documents", "persona", f"{filename}.md")
    elif folder is None:
        doc_file = os.path.join("documents", f"{filename}.md")
    else: 
        raise FileNotFoundError(f"Filename contains invalid folder name: {folder}")
    
    try:
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return content
    except Exception as e:
        logger.error(f"ドキュメントの保存中にエラーが発生しました: {doc_file}, エラー: {str(e)}")
        raise e

def read_persona_file(filename: str)-> str:
    """
    ペルソナに関する情報が記述されたドキュメントを取得する関数

    Args:
        filename (str): 取得したいファイル名
    Returns:
        str: ドキュメントの内容
    
    """

    logger.info(f"Reading file: {filename}")

    if not filename.endswith(".md"):
        filename = f"{filename}.md"
    
    current_dir = Path(__file__).parent
    file_path = current_dir / "persona" / filename

    if not file_path.exists():
        raise FileNotFoundError(f"filename: {filename} was not found.")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        logger.error(f"ファイル読み取りエラー: {str(e)}")
        raise e