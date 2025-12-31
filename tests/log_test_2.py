import logging
import os
import time
from datetime import datetime


class CentOSCompatibleTimedRotatingHandler:
    """
    CentOS兼容的定时滚动日志处理器
    不依赖TimedRotatingFileHandler的内部计时
    """

    def __init__(self, log_file, when='D', interval=1, backup_count=30):
        self.log_file = log_file
        self.when = when
        self.interval = interval
        self.backup_count = backup_count

        # 解析when参数
        self.rollover_seconds = self._parse_when(when)

        # 当前活跃日志文件
        self.current_file = None
        self.current_date_key = None

        # 初始化
        self._update_file()

    def _parse_when(self, when):
        """将when参数转换为秒数"""
        when_map = {
            'S': 1,  # 秒
            'M': 60,  # 分
            'H': 3600,  # 小时
            'D': 86400,  # 天
            'midnight': 86400,  # 午夜
        }
        return when_map.get(when.upper(), 86400) * self.interval

    def _get_date_key(self):
        """获取当前时间的关键字（用于判断是否应该滚动）"""
        now = time.time()

        if self.when.upper() == 'MIDNIGHT':
            # 午夜：使用天数作为key
            return time.strftime('%Y-%m-%d', time.localtime(now))
        elif self.when.upper() == 'H':
            # 小时：使用小时作为key
            return time.strftime('%Y-%m-%d-%H', time.localtime(now))
        elif self.when.upper() == 'D':
            # 天：使用天数作为key
            return time.strftime('%Y-%m-%d', time.localtime(now))
        else:
            # 默认：使用时间戳整除间隔
            interval = self.rollover_seconds
            return str(int(now // interval))

    def _update_file(self):
        """更新当前日志文件"""
        date_key = self._get_date_key()

        # 如果日期/时间段变化，创建新文件
        if date_key != self.current_date_key:
            self._rotate_if_needed()

            # 新文件名
            new_file = f"{self.log_file}.{date_key}"

            # 如果文件存在且当前有打开的文件，先关闭
            if self.current_file and not self.current_file.closed:
                self.current_file.close()

            # 打开新文件
            self.current_file = open(new_file, 'a', encoding='utf-8')
            self.current_date_key = date_key

            # 创建符号链接指向当前日志
            try:
                if os.path.exists(self.log_file):
                    os.remove(self.log_file)
                os.symlink(new_file, self.log_file)
            except:
                pass

    def _rotate_if_needed(self):
        """如果需要，滚动旧日志"""
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            return

        # 获取所有备份文件
        base_name = os.path.basename(self.log_file)
        backups = []

        for f in os.listdir(log_dir):
            if f.startswith(base_name + '.'):
                try:
                    full_path = os.path.join(log_dir, f)
                    mtime = os.path.getmtime(full_path)
                    backups.append((mtime, full_path))
                except:
                    pass

        # 按时间排序
        backups.sort(reverse=True)

        # 删除多余的备份
        for i in range(self.backup_count, len(backups)):
            try:
                os.remove(backups[i][1])
            except:
                pass

    def write(self, message):
        """写入日志消息"""
        self._update_file()

        if self.current_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.current_file.write(f"{timestamp} - {message}\n")
            self.current_file.flush()

    def close(self):
        """关闭文件"""
        if self.current_file and not self.current_file.closed:
            self.current_file.close()


# 使用示例
if __name__ == "__main__":
    # 创建处理器
    handler = CentOSCompatibleTimedRotatingHandler(
        log_file='app.log',
        when='midnight',
        backup_count=30
    )

    # 模拟日志写入
    for i in range(1000):
        handler.write(f"测试消息 {i}")
        time.sleep(1)

    handler.close()
    print("测试完成")