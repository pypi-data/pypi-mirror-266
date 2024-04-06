from ..__const import Const


class TestLinkMsgConst(Const):
    ERROR_GET_PROJECT_ID = "TestLink : get project id from {} failed. {}"
    ERROR_GET_TESTPLAN_NAME = "TestLink : get test plan name from {} failed. {}"
    ERROR_CREATE_BUILD = "TestLink : warning to create build/release in {} failed. {}"
    ERROR_ADD_TC_EXECUTE_STATUS = "TestLink : warning to add test case to execution failed. {}"
    ERROR_SET_TC_EXECUTE_STATUS = "TestLink : warning to set test case status failed. {}"
    PASSED_MESSAGE = "Passed at {} browser"
    FAILED_MESSAGE = "Failed at {} browser.\nErr {}"
