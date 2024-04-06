import os
import sys
import time

from loguru import logger

from pathlib import Path

project_path = Path.cwd().parent
LogPath = Path(project_path, "logs")


class PLogger:
    """输出日志到文件和控制台"""

    def __init__(self, log_folder=None, log_name=None):
        # 文件的命名
        if not log_name:
            log_name = f"Fastapilog_{time.strftime('%Y-%m-%d', time.localtime()).replace('-', '_')}.log"
        if not log_folder:
            log_path = os.path.join(LogPath, log_name)
        else:
            log_path = os.path.join(log_folder, log_name)
        # print(f"log_path:{log_path}")
        self.logger = logger
        # 清空所有设置
        self.logger.remove()
        # 判断日志文件夹是否存在，不存则创建
        if not os.path.exists(LogPath):
            os.makedirs(LogPath)
        # 日志输出格式
        formatter = "{time:YYYY-MM-DD HH:mm:ss} | {level}: {message}"
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 日志写入文件
        self.logger.add(log_path,  # 写入目录指定文件
                        format='{time:YYYYMMDD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                               '{module}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        encoding='utf-8',
                        retention='7 days',  # 设置历史保留时长
                        backtrace=True,  # 回溯
                        diagnose=True,  # 诊断
                        enqueue=True,  # 异步写入
                        rotation="00:00",  # 每日更新时间
                        # rotation="5kb",  # 切割，设置文件大小，rotation="12:00"，rotation="1 week"
                        # filter="my_module"  # 过滤模块
                        # compression="zip"   # 文件压缩
                        )

    def get_logger(self):
        return self.logger


# log = PLogger().get_logger()
