"""Module designed to init and configure logger."""
import os
import logging
import datetime


logger = logging.getLogger(__name__)
logs_path = f"logs/{datetime.datetime.now()}-stock-app.log"
os.makedirs(os.path.dirname(logs_path), exist_ok=True)
logging.basicConfig(filename=logs_path, level=logging.INFO)
