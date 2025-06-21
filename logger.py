import os
import logging
import logging.config

def setup_logging(default_path='logging.conf', default_level=logging.INFO):
    """
    Setup logging configuration from the specified config file.
    Ensures that the 'logs' directory exists.
    """
    # Determine the absolute path to the config file
    config_path = os.path.abspath(default_path)

    # Ensure the 'logs' directory exists
    logs_dir = os.path.join(os.path.dirname(config_path), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Load logging configuration
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        # Fallback to basic configuration if config file is missing
        logging.basicConfig(level=default_level)
        logging.warning(f"Logging configuration file '{config_path}' not found. Using basic configuration.")
