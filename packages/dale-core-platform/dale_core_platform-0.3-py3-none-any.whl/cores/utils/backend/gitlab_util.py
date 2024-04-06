import gitlab
import json
import os

from ...const.api import SwaggerConst
from ...utils.common.string_util import StringUtil


class GitLabService:
    def __init__(self):
        self.gl = gitlab.Gitlab(url=os.getenv('GITLAB_SERVER'),
                                private_token=os.getenv('GITLAB_TOKEN'))

    def get_project_id_from_name(self, project_name: str = 'genie-kat') -> int:
        """
        :param project_name:
        :return: int: gitlab project id
        """
        r = [p.id for p in self.gl.projects.list(
            get_all=True) if p.path in project_name]
        if r:
            return r[0]
        else:
            raise Exception(f'Unable to find project id for {project_name}')

    def parsing_swagger_content(self, projects):
        swagger_dict = dict()
        configs = SwaggerConst.GITLAB_CONFIG_SERVICES
        for project in projects.split(','):
            prj = self.gl.projects.get(self.get_project_id_from_name(project))
            services = configs[project].get('service_list')
            apis = SwaggerConst.API_LIST
            notification_api = configs[project].get('api_list_noti')
            path = configs[project].get('path')
            version = configs[project].get('version')
            _tmp = {}

            """
                return the service name and path as list [name, path]
            """

            swaggers = [[i['name'], i['path']] for i in prj.repository_tree(path=path, ref='main', get_all=True)
                        if i['name'] in (services if services else '') or '.json' in i['name']]
            for swagger in swaggers:
                ser, ser_path = swagger
                if ser == 'notificator':
                    expect_api = notification_api
                else:
                    expect_api = apis
                f_path = ser_path + f'/{version}' if version else ''
                """
                =======================
                if all swagger files not in the folder file na so no need to find the content of the folder
                else need to look in each folder to get the swagger file content
                =======================
                """
                if '.json' in ser_path:
                    f = prj.files.get(file_path=ser_path,
                                      ref='main', get_all=True)
                    _tmp[ser_path.split(
                        '/')[-1].split('.')[0]] = json.loads(StringUtil.decode_str(f.content))

                else:
                    services_list = [i['name'] for i in prj.repository_tree(path=path, ref='main', get_all=True)
                                     if i['name'] in ser_path]
                    api_path = []
                    """
                        get all file_path in the folder
                    """
                    for _ in services_list:
                        tmp = [item['path'] for item in prj.repository_tree(path=f_path, ref='main', get_all=True)
                               if item['path'].split('/')[-1].split('.')[0] in expect_api]
                        api_path.extend(tmp)

                    """
                    process the file_path to get the content of swagger file.
                    This will provide the api name and endpoint 
                    api_name = dict{api_detail}
                    e.g. 
                    SubjectService_GetSubjects = dict(SubjectService_GetSubjects)
                    """
                    for p in api_path:
                        # temporary ignore subject api in library services
                        if 'docs/api/library/v1/subject.swagger.json' != p:
                            f = prj.files.get(
                                file_path=p, ref='main', get_all=True)
                            _tmp[p.split(
                                '/')[-1].split('.')[0]] = json.loads(StringUtil.decode_str(f.content))
                        else:
                            pass
                swagger_dict |= _tmp
        return swagger_dict
