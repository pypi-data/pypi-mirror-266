
from ...const.common import StringFormatConst
from ...utils.common.string_util import StringUtil
from ..common.logger_util import logger
from .base_test_link import BaseTestLink


class AddRemoveTestCase:

    def __init__(self, project_id, test_plan_id):
        self.project_id = project_id
        self.test_plan_id = test_plan_id

    def add_all_test_cases_to_test_plan(self, test_case_external_ids):
        # Add test cases to the test plan
        for external_id in test_case_external_ids:
            output_string = StringUtil.format_string_with_re(re_format=StringFormatConst.FORMAT_AB_123_PATTERN,
                                                             repl=StringFormatConst.FORMAT_AB_123_REPL,
                                                             value=external_id)
            self.add_test_case_to_test_plan(external_id=output_string)

    def add_test_case_to_test_plan(self, external_id):
        test_case_info = BaseTestLink.test_link_client.getTestCase(
            None, testcaseexternalid=external_id)[0]
        external_id = test_case_info['full_tc_external_id']
        test_case_version = int(test_case_info['version'])
        BaseTestLink.test_link_client.addTestCaseToTestPlan(testprojectid=self.project_id,
                                                            testplanid=self.test_plan_id,
                                                            testcaseexternalid=external_id,
                                                            version=test_case_version)
        logger.debug(
            f"Test case '{external_id}' added to test plan id '{self.test_plan_id}'")

    def get_test_cases_for_test_project(self, project_id: int = None):
        list_test_cases = []
        # Get all the test suites for the project
        test_suites = BaseTestLink.test_link_client.getFirstLevelTestSuitesForTestProject(
            testprojectid=project_id if project_id else self.project_id)

        # Function to retrieve test cases within a test suite
        def get_test_cases_in_suite(suite_id):
            suite = BaseTestLink.test_link_client.getTestSuiteByID(
                testsuiteid=suite_id)
            test_cases = BaseTestLink.test_link_client.getTestCasesForTestSuite(
                testsuiteid=suite_id)
            return suite, test_cases

        for suite in test_suites:
            suite_id = suite['id']

            suite_info, suite_test_cases = get_test_cases_in_suite(suite_id)
            list_test_cases += suite_test_cases

        return list_test_cases
