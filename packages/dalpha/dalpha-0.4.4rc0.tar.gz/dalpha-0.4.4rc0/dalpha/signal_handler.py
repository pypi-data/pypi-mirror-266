import signal
from dalpha.logging import logger

shutdown_requested = False

def signal_handler(signum, frame):
    logger.info(
        message = f"Signal handler called with signal {signum}",
        data = {
            "signal": signum,
            "frame": frame
        }
    )
    global shutdown_requested
    shutdown_requested = True

def get_shutdown_requested():
    return shutdown_requested


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)