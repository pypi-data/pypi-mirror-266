from .base_factory import GetRequest, PostRequest, AttachRequest, PutRequest, PatchRequest
from cores.model.request import RequestObjModel
from cores.const.api.request import RequestConst


class RequestFactory(object):
    """
    This Factory to register the method to create RequestObjModelect by the request_type.

    :return RequestObjModelect
    """
    @staticmethod
    def create_request(request_type: str, **kwargs) -> RequestObjModel:
        __content_type: str = str()
        __token: str = str()
        if kwargs.get('content_type'):
            __content_type = kwargs.get('content_type')
        if kwargs.get('token'):
            __token = kwargs.get('token')

        match request_type:
            case RequestConst.Method.GET:
                return GetRequest(token=__token,
                                  content_type=__content_type if __content_type
                                  else RequestConst.Header.CONTENT_TYPE_JSON).request_generate
            case RequestConst.Method.POST:
                return PostRequest(token=__token,
                                   content_type=__content_type if __content_type
                                   else RequestConst.Header.CONTENT_TYPE_JSON,
                                   body=kwargs.get('body')).request_generate
            case RequestConst.Method.ATTACH:
                return AttachRequest(token=__token,
                                     content_type=__content_type if __content_type
                                     else RequestConst.Header.CONTENT_TYPE_UPLOAD,
                                     body=kwargs.get('body'),
                                     file_location=kwargs.get('file_location'),
                                     file_name=kwargs.get('file_name')).request_generate
            case RequestConst.Method.PUT:
                return PutRequest(token=__token,
                                  content_type=__content_type if __content_type
                                  else RequestConst.Header.CONTENT_TYPE_JSON,
                                  body=kwargs.get('body')).request_generate
            # case RequestConst.Method.DELETE:
            #     return GetRequest(token=__token,
            #                       content_type=__content_type if __content_type
            #                       else RequestConst.Header.CONTENT_TYPE_JSON).request_generate
            case RequestConst.Method.PATCH:
                return PatchRequest(token=__token,
                                   content_type=__content_type if __content_type
                                   else RequestConst.Header.CONTENT_TYPE_JSON,
                                   body=kwargs.get('body')).request_generate
            case _:
                raise Exception(f'Do not support this method {request_type}')
