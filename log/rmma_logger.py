# rmma_logger.py
import os
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
            self.initialized = True
    
    def _write(self, level, message, logger_name='rmma'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp} - {logger_name} - {level} - {message}"
        
        # ファイルに書き込み
        log_file = os.path.join(self.log_dir, f"{logger_name}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
        
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