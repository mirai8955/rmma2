# rmma_logger.py
import os
import atexit
from datetime import datetime

class RMMALogger:
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.log_dir = 'logs'
            os.makedirs(self.log_dir, exist_ok=True)
            self.file_handlers = {}  # ファイルハンドラーをキャッシュ
            self.initialized = True
            # アプリケーション終了時にファイルハンドラーを閉じる
            atexit.register(self._close_all_handlers)
    
    def _get_file_handler(self, logger_name):
        """ファイルハンドラーを取得（キャッシュ機能付き）"""
        if logger_name not in self.file_handlers:
            log_file = os.path.join(self.log_dir, f"{logger_name}.log")
            self.file_handlers[logger_name] = open(log_file, 'a', encoding='utf-8')
        return self.file_handlers[logger_name]
    
    def _close_all_handlers(self):
        """全てのファイルハンドラーを閉じる"""
        for handler in self.file_handlers.values():
            if not handler.closed:
                handler.close()
    
    def _write(self, level, message, logger_name='rmma'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp} - {logger_name} - {level} - {message}"
        
        # ファイルハンドラーを取得して書き込み
        handler = self._get_file_handler(logger_name)
        handler.write(log_line + '\n')
        handler.flush()  # 即座にディスクに書き込み
        
        # INFOレベルの場合のみコンソールにも出力
        if level == 'INFO':
            print(log_line)
    
    def get_logger(self, name):
        """ロガーを取得（logging.getLogger()と同様）"""
        if name not in self._loggers:
            self._loggers[name] = LoggerInstance(name, self)
        return self._loggers[name]

class LoggerInstance:
    """個別のロガーインスタンス"""
    def __init__(self, name, manager):
        self.name = name
        self.manager = manager
    
    def info(self, message):
        self.manager._write('INFO', message, self.name)
    
    def error(self, message):
        self.manager._write('ERROR', message, self.name)
    
    def warning(self, message):
        self.manager._write('WARNING', message, self.name)
    
    def debug(self, message):
        self.manager._write('DEBUG', message, self.name)

# グローバルインスタンス
_logger_manager = RMMALogger()

# loggingモジュールと同様のインターフェース
def get_logger(name='rmma'):
    """ロガーを取得する関数（logging.getLogger()と同様）"""
    return _logger_manager.get_logger(name)

def info(message):
    """デフォルトロガーでINFOログを出力"""
    get_logger().info(message)

def error(message):
    """デフォルトロガーでERRORログを出力"""
    get_logger().error(message)

def warning(message):
    """デフォルトロガーでWARNINGログを出力"""
    get_logger().warning(message)

def debug(message):
    """デフォルトロガーでDEBUGログを出力"""
    get_logger().debug(message)