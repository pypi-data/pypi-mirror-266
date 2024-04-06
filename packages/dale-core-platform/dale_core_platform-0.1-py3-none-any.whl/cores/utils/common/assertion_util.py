from unittest import TestCase
import traceback
from typing import Any
# from jsondiff import diff


class AssertionErrorData(object):

    def __init__(self, stacktrace, message):
        super(AssertionErrorData, self).__init__()
        self.stacktrace = stacktrace
        self.message = message


class AssertUtil(TestCase):

    @staticmethod
    def true(expected_value: bool, message: str = None) -> object:
        TestCase().assertTrue(expected_value, message)

    @staticmethod
    def false(expected_value: bool, message: str = None):
        TestCase().assertFalse(expected_value, message)

    @staticmethod
    def equal(expected_value: Any, actual_value: Any, message: str = None):
        TestCase().assertEqual(str(expected_value), str(actual_value), message if message else
                               f'Expected: {expected_value} - Actual: {actual_value}')

    @staticmethod
    def assert_equal_or_lower(expected_value: Any, actual_value: Any, message: str = None):
        TestCase().assertLessEqual(expected_value, actual_value, message)

    @staticmethod
    def not_equal(expected_value: Any, actual_value: Any, message: str = None):
        TestCase().assertNotEqual(expected_value, actual_value, message)

    @staticmethod
    def contain(expected_value: str, actual_value: str, message: str = None):
        result = expected_value in actual_value
        TestCase().assertTrue(result, message)

    # @staticmethod
    # def assert_json_compare(expected_value: str, actual_value: str, message: str = None):
    #     result = diff(expected_value, actual_value)
    #     TestCase().assertEqual(0, len(result),
    #                            message if message else f'Actual {actual_value}\n-Expected {expected_value}')


class MultiAssertsUtil(TestCase):

    def __init__(self, *args, **kwargs):
        self.verificationErrors = []
        super(MultiAssertsUtil, self).__init__(*args, **kwargs)

    def _good_stack_traces(self):
        """
            Get only the relevant part of stacktrace.
        """
        stop = False
        found = False
        good_traces = []
        stacktrace = traceback.extract_stack()

        for stack in stacktrace:
            filename = stack.filename

            if found and not stop and \
                    not filename.find('lib') < filename.find('unittest'):
                stop = True

            if not found and filename.find('lib') < filename.find('unittest'):
                found = True

            if stop and found:
                stackline = '  File "%s", line %s, in %s\n    %s' % (
                    stack.filename, stack.lineno, stack.name, stack.line)
                good_traces.append(stackline)
        return good_traces

    def assert_equal(self, expected_value: Any = '', actual_value: Any = '', message: str = None):
        try:
            super(MultiAssertsUtil, self).assertEqual(
                expected_value, actual_value, message)
        except TestCase.failureException as error:
            good_traces = self._good_stack_traces()
            self.verificationErrors.append(
                AssertionErrorData("\n".join(good_traces[:-2]), error))

    def assert_true(self, actual_value: bool, message: str = None):
        try:
            super(MultiAssertsUtil, self).assertTrue(
                actual_value is True, msg=message)
        except TestCase.failureException as error:
            good_traces = self._good_stack_traces()
            self.verificationErrors.append(
                AssertionErrorData("\n".join(good_traces[:-2]), error))

    def assert_false(self, actual_value: bool, message: str = None):
        try:
            super(MultiAssertsUtil, self).assertFalse(
                actual_value is False, msg=message)

        except TestCase.failureException as error:
            good_traces = self._good_stack_traces()
            self.verificationErrors.append(
                AssertionErrorData("\n".join(good_traces[:-2]), error))

    def tearDown(self):
        super(MultiAssertsUtil, self).tearDown()
        if self.verificationErrors:
            index = 0
            errors = []
            for error in self.verificationErrors:
                index += 1
                errors.append("%s\nAssertionError %s: %s" %
                              (error.stacktrace, index, error.message))
            self.fail('\n' + "\n".join(errors))
        else:
            pass
