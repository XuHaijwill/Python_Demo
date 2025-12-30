import logging
import os
import re
import time
from logging.handlers import TimedRotatingFileHandler


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    自定义时间轮转文件处理器
    解决自定义后缀格式导致删除不生效的问题
    """

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None,
                 suffix_format=None):
        """
        初始化自定义处理器

        Args:
            filename: 日志文件名
            when: 轮转时间单位 ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight')
            interval: 间隔
            backupCount: 保留的备份文件数量
            encoding: 文件编码
            delay: 是否延迟打开文件
            utc: 是否使用UTC时间
            atTime: 轮转时间 (用于'midnight'或特定时间)
            suffix_format: 自定义后缀格式，例如 '%Y%m%d' 或 '%Y%m%d_%H%M%S'
        """
        super().__init__(filename, when, interval, backupCount,
                         encoding, delay, utc, atTime)

        # 如果提供了自定义后缀格式，则设置相应的suffix和extMatch
        if suffix_format:
            self.suffix = suffix_format

            # 根据后缀格式生成匹配的正则表达式
            # 这里需要将strftime格式转换为对应的正则表达式
            self.extMatch = self._suffix_to_regex(suffix_format)

    def _suffix_to_regex(self, suffix_format):
        """
        将strftime格式的后缀转换为正则表达式

        Args:
            suffix_format: strftime格式字符串，如 '%Y%m%d'

        Returns:
            re.Pattern: 编译后的正则表达式
        """
        # 定义常见strftime指令到正则表达式的映射
        format_mapping = {
            '%Y': r'\d{4}',  # 4位年份
            '%y': r'\d{2}',  # 2位年份
            '%m': r'\d{2}',  # 月份
            '%d': r'\d{2}',  # 日期
            '%H': r'\d{2}',  # 24小时制小时
            '%I': r'\d{2}',  # 12小时制小时
            '%M': r'\d{2}',  # 分钟
            '%S': r'\d{2}',  # 秒
            '%f': r'\d{6}',  # 微秒
            '%j': r'\d{3}',  # 一年中的第几天
            '%W': r'\d{2}',  # 一年中的第几周
            '%U': r'\d{2}',  # 一年中的第几周(周日开始)
            '%w': r'\d{1}',  # 一周中的第几天(0-6)
            '%a': r'[A-Za-z]{3}',  # 缩写星期名
            '%A': r'[A-Za-z]+',  # 完整星期名
            '%b': r'[A-Za-z]{3}',  # 缩写月份名
            '%B': r'[A-Za-z]+',  # 完整月份名
        }

        # 将格式字符串转换为正则表达式
        regex_pattern = suffix_format
        for fmt, regex in format_mapping.items():
            regex_pattern = regex_pattern.replace(fmt, regex)

        # 对特殊字符进行转义
        special_chars = '.^$*+?{}[]\\|()'
        for char in special_chars:
            if char in regex_pattern and not regex_pattern.count(char) == regex_pattern.count('\\' + char):
                # 如果字符没有被转义，则转义它
                regex_pattern = regex_pattern.replace(char, '\\' + char)

        # 确保正则表达式匹配整个后缀
        regex_pattern = '^' + regex_pattern + '$'

        return re.compile(regex_pattern)

    def doRollover(self):
        """
        执行日志轮转
        重写此方法以实现自定义轮转逻辑
        """
        # 调用父类的轮转方法
        super().doRollover()

        # 自定义逻辑：可以在这里添加额外的轮转后处理
        # 例如：记录轮转事件、发送通知等
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """
        清理旧日志文件的扩展方法
        可以在这里添加自定义的清理逻辑
        """
        if self.backupCount <= 0:
            return

        # 获取轮转文件列表
        files_to_delete = self.getFilesToDelete()

        # 删除文件
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted old log file: {file_path}")
            except OSError as e:
                print(f"Failed to delete {file_path}: {e}")

    def getFilesToDelete(self):
        """
        获取需要删除的旧日志文件列表
        重写此方法可以实现自定义的删除策略

        Returns:
            list: 需要删除的文件路径列表
        """
        dir_name, base_name = os.path.split(self.baseFilename)
        file_names = os.listdir(dir_name)

        # 构建需要删除的文件列表
        result = []

        # 正则表达式匹配轮转文件
        # 格式: base_name + "." + suffix
        prefix = base_name + "."
        plen = len(prefix)

        for file_name in file_names:
            # 检查文件名是否以base_name.开头
            if file_name[:plen] == prefix:
                suffix = file_name[plen:]

                # 使用自定义的extMatch正则表达式匹配后缀
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dir_name, file_name))

        # 按创建时间排序，最旧的在前
        result.sort(key=lambda x: os.path.getctime(x) if os.path.exists(x) else 0)

        # 保留最新的backupCount个文件，删除其余文件
        if len(result) > self.backupCount:
            return result[:len(result) - self.backupCount]
        else:
            return []


class SizeAwareTimedRotatingFileHandler(CustomTimedRotatingFileHandler):
    """
    同时考虑时间和文件大小的轮转处理器
    """

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 max_file_size=10 * 1024 * 1024,  # 10MB
                 **kwargs):
        super().__init__(filename, when, interval, backupCount, **kwargs)
        self.max_file_size = max_file_size  # 最大文件大小

    def shouldRollover(self, record):
        """
        检查是否需要轮转
        同时检查时间条件和文件大小条件
        """
        # 检查时间条件
        if super().shouldRollover(record):
            return True

        # 检查文件大小条件
        if self.stream is None:
            self.stream = self._open()

        if hasattr(self.stream, 'tell') and hasattr(self.stream, 'seek'):
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # 移动到文件末尾
            if self.stream.tell() + len(msg) >= self.max_file_size:
                return True

        return False


def test_size():
    # 使用示例
    handler = SizeAwareTimedRotatingFileHandler(
        filename='app.log',
        when='D',
        backupCount=7,
        max_file_size=5 * 1024 * 1024,  # 5MB
        suffix_format='%Y%m%d'
    )

if __name__ == '__main__':
    # 使用自定义后缀格式
    handler = CustomTimedRotatingFileHandler(
        filename='app.log',
        when='M',  # 每天轮转
        interval=1,
        backupCount=7,  # 保留7天日志
        suffix_format='%Y%m%d'  # 自定义后缀格式：20231230
    )

    # 配置日志
    logger = logging.getLogger('my_app')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # 记录日志
    logger.info('This is a test log message')
