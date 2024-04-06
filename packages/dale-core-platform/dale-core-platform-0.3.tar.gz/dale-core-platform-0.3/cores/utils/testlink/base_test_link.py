from testlink import TestLinkHelper, TestlinkAPIClient
import configparser

from cores.const.common import EnvConst as const

from cores.utils.common import PathUtil


class BaseTestLink:
    test_link_client = None

    def __init__(self):
        # Connect to BaseTestLink using the API client
        config = configparser.RawConfigParser()
        config.read(PathUtil.join_prj_root_path(
            const.ConfigPath.TESTLINK_CONFIG))
        tl_helper = TestLinkHelper(
            config[const.Testlink.NAME].get(const.Testlink.TESTLINK_API_URL),
            config[const.Testlink.NAME].get(const.Testlink.TESTLINK_API_KEY))
        BaseTestLink.test_link_client = tl_helper.connect(TestlinkAPIClient)

    @staticmethod
    def get_project_id_by_project_name(project_name):
        # Get the project ID based on the project name
        project_info = BaseTestLink.test_link_client.getTestProjectByName(
            testprojectname=project_name)
        return project_info['id']
