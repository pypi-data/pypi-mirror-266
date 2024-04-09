from datetime import datetime
import logging
import logging.handlers
import uuid
import os

cmd_log_level = 'WARN'


class Logger():
	def __init__(self, log_path):
		ch = logging.StreamHandler()
		ch.setLevel(cmd_log_level) # 指定被处理的信息级别为最低级DEBUG，低于level级别的信息将被忽略
		# 输出到file
		file_name = '%s.log'%(datetime.now().strftime('%Y%m%d_%H%M%S.%f'))
		file_path = os.path.join(log_path, file_name)
		fh = logging.handlers.RotatingFileHandler(file_path, mode='w', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"))

		logger = self.logger = logging.getLogger(str(uuid.uuid1()))
		logger.setLevel(logging.DEBUG)
		logger.addHandler(ch)
		logger.addHandler(fh)

	def debug(self, msg):
		self.logger.debug(msg)
		
	def info(self, msg):
		self.logger.info(msg)
		
	def warn(self, msg):
		self.logger.warn(msg)
		
	def error(self, msg):
		self.logger.error(msg)

	def log(self, tag=None, kv={}, level='info'):
		now_dt = datetime.now()
		try:
			now_dt = datetime.now()
		except:
			pass

		msg = ''
		if tag:
			if isinstance(tag, list):
				msg += '【%s】'%('】【'.join(tag))
			else:
				msg += '【%s】'%(tag)
		
		if isinstance(kv, dict):
			for k in kv:
				v = kv[k]
				msg += '%s=%s | '%(k, v)
		elif isinstance(kv, list):
			msg += str(kv)
		else:
			msg += str(kv)

		msg += ' @%s'%(now_dt)
		
		if level == 'debug':
			self.logger.debug(msg)
		if level == 'info':
			self.logger.info(msg)
		elif level == 'warn':
			self.logger.warn(msg)
		elif level == 'error':
			self.logger.error(msg)