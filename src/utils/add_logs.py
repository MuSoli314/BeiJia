import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # 创建日志目录
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 基础配置
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置日志级别

    # 日志格式
    log_fmt = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s[%(lineno)d]: %(message)s'
    )

    # 文件日志（按大小轮转）
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_fmt)
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_fmt)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用示例
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")