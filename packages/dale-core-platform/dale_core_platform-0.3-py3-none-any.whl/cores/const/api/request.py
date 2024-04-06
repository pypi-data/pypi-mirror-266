from ..__const import Const


class RequestConst(Const):

    class Method:
        GET = 'GET'
        POST = 'POST'
        PATCH = 'PATCH'
        PUT = 'PUT'
        DELETE = 'DELETE'
        ATTACH = 'ATTACH'

    class Header:
        CONTENT_TYPE_JSON = 'application/json'
        CONTENT_TYPE_UPLOAD = 'application/x-www-form-urlencoded'
        CONTENT_TYPE_XML = 'text/xml; charset=utf-8'

    class StatusCode:
        OK: int = 200
        CREATED: int = 201
        ACCEPTED: int = 202
        NON_AUTHORITATIVE_INFORMATION: int = 203
        NO_CONTENT: int = 204
        BAD_REQUEST: int = 400
        UNAUTHORIZED: int = 401
        PAYMENT_REQUIRED: int = 402
        PERMISSION_DENIED: int = 403
        NOT_FOUND: int = 404
        METHOD_NOT_ALLOWED: int = 405

    class GRPCCode:
        BAD_REQUEST: int = 3
        NOT_FOUND: int = 5
        PERMISSION_DENIED: int = 7
        UNAUTHORIZED: int = 16

    class Message:
        OK: str = 'success'
        UNAUTHORIZED: str = 'unauthorized'
        METHOD_NOT_ALLOWED: str = 'Method Not Allowed'
        NO_ACCESS_RULE: str = 'no access rule defined'
        NOT_FOUND: str = 'not found'
        PERMISSION_DENIED: str = ''
