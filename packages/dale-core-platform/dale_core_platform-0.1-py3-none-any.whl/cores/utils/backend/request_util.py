from ..common.logger_util import logger
from cores.decorators import handle_exception
from cores.model import ResponseObjModel, RequestObjModel
from cores.const.custom_exception import RequestError
from cores.const.api import RequestConst
from cores.const.common import EnvConst
from requests.exceptions import Timeout, ConnectTimeout
from requests import Response, RequestException
import json
import os
from typing import Dict

import curl
import requests
# Follow the reply in this thread: https://stackoverflow.com/questions/72479812/how-to-change-tweak-python-3-10-default-ssl-settings-for-requests-sslv3-alert
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'
# -------


class RequestUtil:

    __log = '''
        Method: %(method)s
        Url: %(url)s
        Curl: %(r_curl)s
        Header: %(header)s
        Data:   %(data)s
        StatusCode: %(code)s
        '''

    def _log(url: str = None, headers: Dict = None, data: Dict = None, response: Response = None,
             log_level=os.getenv('LOG_LEVEL') if os.getenv(
                 'LOG_LEVEL') else EnvConst.Logger.INFO,
             method: str = str()):
        _data = RequestUtil.__log % {'method': method.upper(),
                                     'url': url if url else None,
                                     'r_curl': curl.parse(response, return_it=True) if response else None,
                                     'header': headers if headers else None,
                                     'data': data if data else None,
                                     'code': response.status_code if response else None}
        if log_level == EnvConst.Logger.INFO:
            logger.info(_data)

        elif log_level == EnvConst.Logger.DEBUG:
            logger.debug(
                f'Pretty Payload:\n{_data}\nFull Response:\n{response.json()}')
        elif log_level == EnvConst.Logger.ERROR:
            logger.error(_data)
        else:
            logger.warning('Not support this log value')

    def _parse_data(response: Response):
        try:
            return ResponseObjModel(**dict(status_code=response.status_code,
                                           status_msg=response.json().get('status').get('code'),
                                           message='' if not (response.json().get('status').get('message'))
                                           else response.json().get('status').get('message'),
                                           response_data=response.json().get('payload'),
                                           meta_data=response.json().get('meta')
                                           )
                                    )
        except AttributeError as e:
            logger.warning('Using the default output for response outside project')
            return ResponseObjModel(**dict(status_code=response.status_code,
                                           response_data=response.json()
                                           )
                                    )

    @handle_exception
    def _post(url: str, data: RequestObjModel) -> Response:
        body = None
        try:
            body = json.dumps(data.body)
        except AttributeError as e:
            logger.warn('Missing attribute {e}')
            body = data.body
        finally:
            return requests.post(url=url, headers=data.header, data=body)

    @handle_exception
    def _get(url: str, data: RequestObjModel=None) -> Response:
        return requests.get(url, headers=data.header)

    @handle_exception
    def _query(url: str, data: RequestObjModel = None, query: str = None) -> Response:
        return requests.get(url, headers=data.header, params={'q': query})

    @handle_exception
    def _put(url: str, data: RequestObjModel) -> Response:
        return requests.put(url, headers=data.header, data=json.dumps(data.body))

    @handle_exception
    def _patch(url: str, data: RequestObjModel) -> Response:
        return requests.patch(url=url, headers=data.header,
                              data=json.dumps(data.body))

    @handle_exception
    def _delete(url: str, data: RequestObjModel) -> Response:
        return requests.delete(url, headers=data.header, data=data.body)

    # @staticmethod
    # def post_with_oauth(url: str, header: str, data: str, json_flag=False):
    #     logger.debug('/POST url: %s \n header: %s \n data: %s' %
    #                  (url, header, data))
    #     r = requests.post(url, headers=header, data=data)
    #     logger.debug(r.json())
    #     return r.json() if json_flag else Json2Obj.convert_json_to_object(r.json())

    @handle_exception
    def _attach(url: str, data: RequestObjModel) -> Response:
        return requests.post(url, headers=data.header, files=data.files)

    @staticmethod
    def retry_until_die(max_retries: int = 2, resp: Response = Response(), request_url: str = str(), data: ResponseObjModel = ResponseObjModel(),
                        is_convert: bool = True, method: str = str()) -> ResponseObjModel | None:
        """Retry while timeout, do not apply for failed request

        Args:
            max_retries (int, optional): _description_. Defaults to 2.
            resp (Response, optional): _description_. Defaults to Response().
            request_url (str, optional): _description_. Defaults to str().
            data (ResponseObjModel, optional): _description_. Defaults to ResponseObjModel().
            is_convert (bool, optional): _description_. Defaults to True.
            method (str, optional): _description_. Defaults to str().

        Raises:
            Exception: Not really rasie exception, but warn the timeout occurs then do the retry

        Returns:
            ResponseObjModel or None: _description_
        """
        for retry in range(max_retries):
            try:
                if resp.status_code in (RequestConst.StatusCode.OK, RequestConst.StatusCode.CREATED):
                    RequestUtil._log(url=request_url, headers=data.header,
                                     data=data.body, response=resp, method=method)
                else:
                    logger.error(RequestException(
                        f'Error with code: {resp.status_code} \nmessage {resp.json()}'))
                    RequestUtil._log(url=request_url, headers=data.header,
                                     data=data.body, log_level=EnvConst.Logger.ERROR, method=method, response=resp)
                return RequestUtil._parse_data(resp) if is_convert else resp.json()
            except (Timeout, ConnectTimeout):
                logger.warning('Timeout occurred! Retrying!')
            if retry == max_retries:
                raise RequestError(f'Failed to making {method} request to {request_url}!')

    @staticmethod
    def request(url: str, data: RequestObjModel, is_convert: bool = True) -> ResponseObjModel:
        response: ResponseObjModel
        match data.method:
            case RequestConst.Method.GET:
                response = RequestUtil.retry_until_die(resp=RequestUtil._get(url=url, data=data),
                                                       request_url=url, data=data, is_convert=is_convert, method=data.method)
            case RequestConst.Method.POST:
                response = RequestUtil.retry_until_die(resp=RequestUtil._post(url=url, data=data),
                                                       request_url=url, data=data, is_convert=is_convert, method=data.method)
            case RequestConst.Method.PUT:
                response = RequestUtil.retry_until_die(resp=RequestUtil._put(url=url, data=data),
                                                       request_url=url, data=data, is_convert=is_convert, method=data.method)
            case RequestConst.Method.ATTACH:
                response = RequestUtil.retry_until_die(resp=RequestUtil._attach(url=url, data=data),
                                                       request_url=url, data=data, is_convert=is_convert, method=data.method)
            case RequestConst.Method.DELETE:
                response = RequestUtil.retry_until_die(resp=RequestUtil._delete(url=url),
                                                       request_url=url, is_convert=is_convert, method=data.method)
            case _:
                raise RequestError(f'Do not support this method {data.method}')
        return response
