# import logging
# import os

# def get_project_root():
#     """プロジェクトルートを取得"""
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     # README.mdがある場所をプロジェクトルートとする
#     while current_dir != os.path.dirname(current_dir):
#         if os.path.exists(os.path.join(current_dir, "README.md")):
#             return current_dir
#         current_dir = os.path.dirname(current_dir)
#     return current_dir

# def setup_app_logger():
#     """アプリケーション全体のログ設定"""
#     project_root = get_project_root()
#     log_dir = os.path.join(project_root, "log/rmma")
    
#     if not os.path.exists(log_dir):
#         os.makedirs(log_dir)
    
#     log_file = os.path.join(log_dir, "app.log")
    
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_file, encoding='utf-8'),
#             logging.StreamHandler()
#         ]
#     )

# # アプリ起動時に1回実行
# setup_app_logger()

# def get_logger(name):
#     return logging.getLogger(name)