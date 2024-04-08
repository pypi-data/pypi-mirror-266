import logging
import logging.config
import os

from dalpha.logging.log_formatter import DalphaJsonFormatter

class DalphaLogger:
    def __init__(self, format_type='json', level=logging.INFO):
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(level)

        # Create formatter
        if format_type == 'json':
            formatter = DalphaJsonFormatter(json_ensure_ascii=False)
        else:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Add formatter to handler
        consoleHandler.setFormatter(formatter)

        # Get the root logger
        self.logger = logging.getLogger('Dalpha')
        self.logger.setLevel(level)
        self.logger.addHandler(consoleHandler)

    def __make_extra(self, event, properties, data):
        return {
            "event": event,
            "properties": properties,
            "data": data
        }
    
    def info(self, message, event=None, properties={}, data={}):
        self.logger.info(
            message,
            extra = self.__make_extra(event, properties, data)
        )
    
    def error(self, message, event=None, properties={}, data={}):
        self.logger.error(
            message,
            extra = self.__make_extra(event, properties, data)
        )

    def warning(self, message, event=None, properties={}, data={}):
        self.logger.warning(
            message,
            extra = self.__make_extra(event, properties, data)
        )
    
    def debug(self, message, event=None, properties={}, data={}):
        self.logger.debug(
            message,
            extra = self.__make_extra(event, properties, data)
        )

if bool(os.environ.get('DEV_SERVER', 'True') == 'True'):
    format_type = 'text'
else:
    format_type = 'json'
logger = DalphaLogger(format_type=format_type)

