import json
from pythonjsonlogger import jsonlogger
from datetime import datetime
from dalpha.context import get_context
from dataclasses import asdict

class DalphaJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        properties = asdict(get_context())
        log_record['timestamp'] = datetime.now().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        super(DalphaJsonFormatter, self).add_fields(log_record, record, message_dict)
        if 'properties' in log_record:
            properties.update(log_record['properties'])
        log_record['properties'] = properties
        
    
    def format(self, record):
        # Build the log record using the parent class method
        log_record = super(DalphaJsonFormatter, self).format(record)
        # Convert the log record to a dictionary
        log_record_dict = json.loads(log_record)
        # Serialize the dictionary to a JSON string ensuring UTF-8 characters are not escaped
        return json.dumps(log_record_dict, ensure_ascii=False)
