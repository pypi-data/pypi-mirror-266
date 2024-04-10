import logging
import os
import config

if not os.path.exists(config.log_directory):
    os.makedirs(config.log_directory)
logging.basicConfig(filename=config.log_file, level=logging.DEBUG, format=config.log_format)

def new_log(bug_type, message):
    """
    Crée un logging correspondant au type de bug spécifié avec le message donné.

    Args:
        bug_type (str): Le type de bug (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        message (str): Le message à enregistrer dans le logging.
    """
    bug_type_mapping = {
        "DEBUG": logging.debug,
        "INFO": logging.info,
        "WARNING": logging.warning,
        "ERROR": logging.error,
        "CRITICAL": logging.critical
    }

    if bug_type not in bug_type_mapping:
        raise ValueError(f"Type de bug invalide : {bug_type}")

    bug_type_mapping[bug_type](message)



