from json import JSONDecodeError

from ...utils.common.json_util import JsonConverterUtil
from ..common.logger_util import logger
from ...utils.common.store_util import StoreUtil, GetUtil
from ...utils.backend.gitlab_util import GitLabService
from ...utils.backend.request_util import RequestUtil

from ...const.common import EnvConst
from ...const.api import RequestConst
from ...model import RequestObjModel


class SwaggerUtil:

    @staticmethod
    def attributes_cooker(**kwargs):
        """
        return json format:
        API : {
        endpoint: str,
        content_type: list[],
        method: str,
        request: params,
        response: str(Type)
        }

        """
        attr: dict = dict()
        __p = kwargs
        paths = __p.get('paths')
        end_point = __p.get('end_point')
        method = __p.get('method')
        host = __p.get('host')
        consume = __p.get('consume')
        params = __p.get('params')
        response = __p.get('response')
        logger.debug(
            f'Cooking data for {host + end_point} with {(method.upper())} method')
        attr[paths[end_point][method]['operationId']] = {
            'endpoint': host + end_point,
            'content_type': consume,
            'method': method,
            'request': params,
            'response': response}
        return attr

    @staticmethod
    def response_schema_parser(json_str: str) -> dict:
        """Parsing the response schema to 

        Args:
            json_str (str): _description_

        Returns:
            _type_: dict
        """
        response: dict = dict()
        if 'properties' not in json_str.keys():
            return response
        else:
            for k, v in json_str.get('properties').items():
                if v.get('type') == 'array':
                    response[k] = 'list'
                else:
                    response[k] = v.get('type')
            return response

    def __get_parser(file_content: dict, path, endpoint, method):
        """
        1. If select - GET (or possibly delete - DELETE) api, we normally parse the required params to the request url
        or using query params
        :param file_content:
        :param obj_convert:
         :return: object of the api in Json2Obj format
            Json2Obj(API_NAME:(
                    endpoint: 'https://server.com/v1/api',
                    method: 'post',
                    content_type: 'type',
                    request:  Obj( param: type, ...),
                    response: Obj(pramm: type_name)
                              )
                    )
        e.g.
        RoomService_CreatePrivateRoom  (api_name:"https://server.com/v1/rooms/private",
                                        method:"post",
                                        content_type:"application/x-www-form-urlencoded"
                                        request:(
                                                countryId:{type: string, required: True}
                                                description:{type: string, required: False}
                                                levelIds:{type: array}
                                        )
                                        response: parameters : (id: integer)
        """
        params = None
        if path[endpoint][method].get('parameters'):
            params = path[endpoint][method]['parameters']
            body: dict = dict()
            attrs: dict = dict()
            if params:
                for p in params:
                    try:
                        body[p['name']] = dict(
                            type=p['type'], required=p['required'])
                    except Exception as e:
                        logger.warn(
                            f'{p}: {e}. Do not find type property, applying workaround')
                        body[p['name']] = dict(
                            type=p['schema']['type'], required=p['required'])
            attrs.update(SwaggerUtil.attributes_cooker(paths=path))
        return attrs

    def __post_parser(file_content: dict, path, endpoint, method, host, consume, definition, response):
        """
        Applicable for create / update (POST / PATCH / PUT) api:
            a. we have to check if the params using the #refs in model definition and then parsing all params in model
            b. we have to check if the params don't have #refs in model definition:
                b.1. if object only -> parse params to object
                b.2. if object with array
                    b.2.1. ignore params put in path
                    b.2.2. -> iterate into params -> parse the child params into json -> put into list -> wrap list into
                                json format of parent params
        :param file_content:
        :param obj_convert:
         :return: object of the api in Json2Obj format
            Json2Obj(API_NAME:(
                    endpoint: 'https://server.com/v1/api',
                    method: 'post',
                    content_type: 'type',
                    request:  Obj( param: type, ...),
                    response: Obj(pramm: type_name)
                              )
                    )
        e.g.
        RoomService_CreatePrivateRoom(  api_name:"https://server.com/v1/rooms/private",
                                        method:"post",
                                        content_type:"application/x-www-form-urlencoded"
                                        request:parameters: (
                                                countryId:{type: string, required: True}
                                                description:{type: string, required: False}
                                                levelIds:{type: array}
                                                )
                                        response: parameters : (
                                                            id: integer
                                                            )
        """
        attrs: dict = dict()
        if not path[endpoint][method].get('parameters'):
            params = None
        else:
            params = [x for x in path[endpoint]
                      [method].get('parameters') if x['in'] == 'body']
        if params:
            params = params[0]
            schema = params.get('schema')
            ref = schema.get('$ref') if not schema.get(
                'items') else schema.get('items').get('$ref')
            properties = schema.get('properties')
        if schema and ref:
            body = {}
            def_name = ref.replace('#/definitions/', '')
            # Using reference for body
            for k, v in definition[def_name].get('properties').items():
                body[k] = dict(type=v.get('type'), required=True)
            attrs.update(SwaggerUtil.attributes_cooker(paths=path,
                                                       end_point=endpoint,
                                                       method=method,
                                                       host=host,
                                                       consume=consume,
                                                       params=body,
                                                       response=SwaggerUtil.response_schema_parser(definition[response])))
        elif schema == {'type': 'object'}:
            # Using reference for body
            attrs.update(SwaggerUtil.attributes_cooker(paths=path,
                                                       end_point=endpoint,
                                                       method=method,
                                                       host=host,
                                                       consume=consume,
                                                       params={},
                                                       response=SwaggerUtil.response_schema_parser(definition[response])))
        elif schema and properties:
            """
                if request uses #ref, all parameters will be parsed from definitions
                    if parameter format as list of items, param will be parsed as 
                    param = {type: array, required=True}
                    other will be parsed as usual
            """
            body = {}
            for k in properties.keys():
                body[k] = dict(type=properties[k].get('type'), required=True)
            attrs.update(SwaggerUtil.attributes_cooker(paths=path,
                                                       end_point=endpoint,
                                                       method=method,
                                                       host=host,
                                                       consume=consume,
                                                       params=body,
                                                       response=SwaggerUtil.response_schema_parser(definition[response])))
        else:
            logger.warning(
                f'Unhandled value: {endpoint}:{method} {schema} and {properties} or {ref}')
        return attrs

    @staticmethod
    def swagger_parser_factory(request_type: str, **kwargs):
        file_content: dict = kwargs.get('file_content')
        obj_convert: bool = kwargs.get('obj_convert')
        attrs: dict = dict()
        try:
            if getattr(file_content) is not dict:
                file_content = JsonConverterUtil.convert_string_to_json(
                    str(file_content))
        except JSONDecodeError as parsing_err:
            raise Exception(f'{parsing_err} when parsing {file_content}')
        __service_name = file_content.get('tags')[0].get('name')
        if not GetUtil.suite_get(__service_name):
            __consume = file_content.get('consumes') if file_content.get(
                'consumes') else 'application/json'
            __paths = file_content.get('paths')
            __definition = file_content.get('definitions')
            __base_path = file_content.get('basePath')
            __scheme = file_content.get('schemes')[0]
            methods = [x for x in __paths[end_point].keys()]
            base_path = None
            if __base_path:
                base_path = __base_path if '/v1' not in __base_path else __base_path.replace(
                    '/v1', '')
            host = f"{__scheme}://{file_content.get('host')}{base_path if base_path else '/api'}"
            # workaround until backend found solution for swagger base
            __env = GetUtil.suite_get(EnvConst.Environment.ENV_OBJ).env
            if __env == 'stg':
                host = host.replace('dev', 'stg')
            elif __env == 'srv':
                host = host.replace('dev', 'srv')
            else:
                logger.warn(f'Un-recognized environement {__env}')
            for end_point in __paths:
                # loggerger.debug(f'{end_point} support {len(methods)} methods: {methods}')
                for method in methods:
                    tmp_path = __paths[end_point][method]['responses']['200']['schema']['$ref']
                    if 'definition' in tmp_path:
                        response = tmp_path.replace('#/definitions/', '')
                    else:
                        # workaround incase ref not as the format
                        response = ''.join(i for i in tmp_path.split('.')[-2:])
                params = dict(
                    file_content=file_content,
                    path=__paths,
                    consume=__consume,
                    method=method,
                    endpoint=end_point,
                    definition=__definition,
                    response=response
                )
                if method.upper() in [RequestConst.Method.GET, RequestConst.Method.DELETE]:
                    SwaggerUtil.__get_parser(**params)
                elif method.upper() in [RequestConst.Method.PUT, RequestConst.Method.PATCH, RequestConst.Method.POST]:
                    SwaggerUtil.__post_parser(**params)
                else:
                    raise Exception(
                        f'not support this request type {request_type}')
        if obj_convert:
            obj = JsonConverterUtil.convert_json_to_object(attrs)
            StoreUtil.suite_store(keyword=__service_name, data=obj)
            return obj
        else:
            StoreUtil.suite_store(keyword=__service_name, data=attrs)
            return attrs

    @staticmethod
    def parsing_swagger(is_gitlab: bool = True, url: str = None, prj_name: str = None):
        if is_gitlab:
            gl = GitLabService()
            if not prj_name:
                prj_name = GetUtil.suite_get(
                    EnvConst.Environment.ENV_OBJ).PROJECT_NAME
            try:
                swagger_content = gl.parsing_swagger_content(projects=prj_name)
                StoreUtil.suite_store(
                    EnvConst.Swagger.SWAGGER_OBJ, swagger_content)
                return swagger_content
            except Exception as e:
                raise Exception(f"Can't find the service url \n{e}")
        else:
            data = RequestObjModel()
            data.header = {'Content-Type': 'application/json'}
            swagger_content = RequestUtil.get(
                url=url, data=data, is_convert=False)
            StoreUtil.suite_store(
                EnvConst.Swagger.SWAGGER_OBJ, swagger_content)
