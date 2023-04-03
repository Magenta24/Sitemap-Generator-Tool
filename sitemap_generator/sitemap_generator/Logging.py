import logging
import os
from django.conf import settings as django_settings


class Logging:
    def __init__(self):
        log_path = os.path.join(django_settings.LOGS_ROOT, 'logs.log')
        logging.basicConfig(filename=log_path, encoding='utf-8', filemode='w', level=logging.NOTSET)

