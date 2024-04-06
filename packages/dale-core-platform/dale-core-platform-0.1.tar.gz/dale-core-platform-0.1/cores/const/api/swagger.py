from ..__const import Const


class SwaggerConst(Const):
    valid_json_file = 'data/unittest/swagger/swagger_utils_unittest.json'
    invalid_json_file_no_definition = 'data/unittest/swagger/swagger_utils_unittest_invalid_no_definition.json'
    invalid_json_file_no_path = 'data/unittest/swagger/swagger_utils_unittest_invalid_no_path.json'
    invalid_json_file_no_splash = 'data/unittest/swagger/swagger_utils_unittest_invalid_no_splash.json'
    invalid_json_file_no_schema = 'data/unittest/swagger/swagger_utils_unittest_invalid_no_schema.json'
    GITLAB_SERVER = 'https://gitlab.geniebook.com/'
    GITLAB_TOKEN = 'glpat-HmbhpGh1DoRvEFzeCJpy'
    SWAGGER_OBJ = 'swagger_object'
    SWAGGER_JSON = 'swagger_json'
    __SERVICE_LIST = ['user', 'chat', 'common',
                      'attachment', 'notificator', 'library', 'workbook']
    API_LIST = ['user', 'group', 'permission', 'role', 'search', 'student',
                'teacher', 'search', 'message', 'channel', 'market', 'topic', 'subtopic', 'tier', 'question',
                'channel_message_pin', 'attachment', 'sticker', 'template',
                'level', 'subject', 'subject_category', 'exambook_legacy',
                'channel_setting', 'student-worksheet-answer', 'student-worksheet']
    GITLAB_CONFIG_SERVICES = {'genie-kat': dict(service_list=__SERVICE_LIST,
                                                api_list_noti=[
                                                    'coordinate', 'notihub'],
                                                path='docs/api',
                                                version='v1')}
