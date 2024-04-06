from ...utils.common.assertion_util import MultiAssertsUtil
from ...model.request import ResponseObjModel
from ...const.api import RequestConst


class VerifyResultUtil:

    @staticmethod
    def verify_request_succesfully(response: ResponseObjModel):
        verify = MultiAssertsUtil()
        verify.assert_equal(response.status_code, RequestConst.StatusCode.OK)
        verify.assert_equal(response.message, RequestConst.Message.OK)
