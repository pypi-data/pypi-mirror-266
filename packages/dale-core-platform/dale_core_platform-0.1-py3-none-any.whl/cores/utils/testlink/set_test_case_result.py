from cores.const.common import CommonTypeUsageConst, StringConst
from cores.const.config import TestCaseExecutionConst

from cores.utils.testlink import BaseTestLink


class TestCaseResultConst:
    PASSED = "p"
    FAILED = "f"
    BLOCKED = "b"
    NOT_RUN = "n"


class SetTestCaseResult:

    def __init__(self, build_name, test_plan_id):
        self.build_name = build_name
        self.test_plan_id = test_plan_id

    def set_test_case_result(self, test_case_external_id, status: str = TestCaseResultConst.NOT_RUN, notes: str = CommonTypeUsageConst.EMPTY):
        # Set the test case result
        BaseTestLink.test_link_client.reportTCResult(
            testcaseexternalid=test_case_external_id,  # External ID of the test case
            testplanid=self.test_plan_id,  # Test plan ID
            buildname=self.build_name,
            status=status,
            notes=notes,
        )

    @staticmethod
    def generate_testcase_execution_status(browser, is_passed: bool = False, error_message: str = StringConst.SPACE_STRING):
        if is_passed:
            return TestCaseResultConst.PASSED, TestCaseExecutionConst.PASSED_MESSAGE.format(browser)
        else:
            return TestCaseResultConst.FAILED, TestCaseExecutionConst.FAILED_MESSAGE.format(browser, error_message)
