import logging
import chkp_harmony_endpoint_management_sdk.core.logger as sdk_logger


def output_issue(verbose_level, message):
    if verbose_level == 'error' or verbose_level == '*':
        sdk_logger.error_logger(message)
    else:
        print(message)


def configure_logger(verbose_level):
    sdk_logger._logger.name = 'chkp_harmony_endpoint_management_cli:info'
    sdk_logger._error_logger.name = 'chkp_harmony_endpoint_management_cli:error'
    sdk_logger._network_logger.name = 'chkp_harmony_endpoint_management_cli:network'

    sdk_logger._logger.setLevel(logging.CRITICAL + 1)
    sdk_logger._error_logger.setLevel(logging.CRITICAL + 1)
    sdk_logger._network_logger.setLevel(logging.CRITICAL + 1)

    if verbose_level == 'info' or verbose_level == '*':
        sdk_logger._logger.setLevel(logging.DEBUG)
    if verbose_level == 'error' or verbose_level == '*':
        sdk_logger._error_logger.setLevel(logging.DEBUG)
    if verbose_level == 'network' or verbose_level == '*':
        sdk_logger._network_logger.setLevel(logging.DEBUG)
