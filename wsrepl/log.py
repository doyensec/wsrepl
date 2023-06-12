import logging

from wsrepl.WSMessage import WSMessage

class WSReplHandler(logging.Handler):
    def __init__(self, app, level):
        super().__init__()
        self.history = app.history
        self.setLevel(level)

    def emit(self, record):
        msg = record.getMessage()

        if record.levelname == 'DEBUG':
            message = WSMessage.debug(msg)
        elif record.levelname == 'INFO':
            message = WSMessage.info(msg)
        elif record.levelname == 'WARNING':
            message = WSMessage.warning(msg)
        elif record.levelname == 'ERROR':
            message = WSMessage.error(msg)
        else:
            raise ValueError(f'Unknown log level: {record.levelname}')

        self.history.add_message(message)

log = logging.getLogger('wsrepl')

def register_log_handler(app, verbosity: int):
    log_level = (5 - verbosity) * 10
    handler = WSReplHandler(app, log_level)
    log.addHandler(handler)
