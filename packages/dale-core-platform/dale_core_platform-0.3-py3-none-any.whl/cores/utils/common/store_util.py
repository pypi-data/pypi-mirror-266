from getgauge.python import data_store
from typing import Any
import inspect

from .logger_util import logger


log_content = '[Caller: %(locator)s] - %(message)s'


class StoreUtil:

    @staticmethod
    def spec_store(keyword: str, data: Any):
        if data:
            data_store.spec[keyword] = data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tSpec store data <{keyword}> is NULL!'})

    @staticmethod
    def scenario_store(keyword: str, data: Any):
        if data:
            data_store.scenario[keyword] = data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tScenarios store data <{keyword}> is NULL!'})

    @staticmethod
    def suite_store(keyword: str, data: Any):
        if data:
            data_store.suite[keyword] = data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tSuite store data <{keyword}> is NULL!'})

    @staticmethod
    def clear_scenario_store():
        data_store.scenario.clear()

    @staticmethod
    def clear_scenario(keyword: str):
        data_store.scenario.pop(keyword)


class GetUtil:

    @staticmethod
    def spec_get(keyword: str) -> Any:
        data = data_store.spec.get(keyword)
        if data:
            return data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tSpec get data <{keyword}> is NULL!'})
            return list()

    @staticmethod
    def scenario_get(keyword: str) -> Any:
        data = data_store.scenario.get(keyword)
        if data:
            return data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tScenarios get data <{keyword}> is NULL!'})
            return list()

    @staticmethod
    def suite_get(keyword: str) -> Any:
        data = data_store.suite.get(keyword)
        if data:
            return data
        else:
            logger.warning(log_content % {'locator': inspect.stack()[1][3],
                                          'message': f'\tSuite get data <{keyword}> is NULL!'})
            return list()
