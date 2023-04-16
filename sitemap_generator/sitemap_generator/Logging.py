import logging
import os
from django.conf import settings as django_settings


class Logging:
    def __init__(self, base_filepath):
        log_path = os.path.join(django_settings.LOGS_ROOT, (base_filepath + '-logs.log'))
        logging.basicConfig(
            filename=log_path,
            encoding='utf-8',
            filemode='w',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s')
        self.logger = logging.getLogger('exceptions')

    def log_exception(self, *args, **kwargs):
        self.logger.exception('EXCEPTION: ', args, kwargs)

    def log_info(self, msg):
        self.logger.info(msg)

