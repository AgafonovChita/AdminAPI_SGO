import logging
import sys

base_logger = logging.getLogger()
base_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('BaseClient.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

base_logger.addHandler(file_handler)
base_logger.addHandler(stdout_handler)
