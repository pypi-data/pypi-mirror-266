import logging

from libsrg.LoggingAppBase import LoggingAppBase

"""
This module is a sample application template for libsrg application logging
"""


class Other:
    def __init__(self, n):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Created Other {n}!")


class SampleApp(LoggingAppBase):

    def __init__(self):
        super().__init__()  # super defines self.logger
        self.logger.info("before adding args")
        # setup any program specific command line arguments
        self.parser.add_argument('--zap', help="Zap something", dest='zap', action='store_true', default=False)
        self.parser.add_argument('--zip', help="Zip something", dest='zip', action='store_true', default=False)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")

    @classmethod
    def demo(cls):
        _ = SampleApp()
        _ = Other(1)
        _ = Other(2)


if __name__ == '__main__':
    SampleApp.demo()
