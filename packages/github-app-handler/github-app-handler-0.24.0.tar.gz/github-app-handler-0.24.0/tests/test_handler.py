from unittest.mock import ANY, patch

import pytest

from githubapp import webhook_handler
from githubapp.webhook_handler import _validate_signature, handle
from tests.mocks import EventTest, SubEventTest


@pytest.fixture(autouse=True)
def auto_mock_auth(mock_auth):
    yield


def test_add_handler_sub_event(method):
    webhook_handler.register_method_for_event(SubEventTest, method)

    assert len(webhook_handler.handlers) == 1
    assert webhook_handler.handlers.get(SubEventTest) == [method]


def test_add_handler_event(method):
    webhook_handler.register_method_for_event(EventTest, method)

    assert len(webhook_handler.handlers) == 1
    assert EventTest not in webhook_handler.handlers
    assert webhook_handler.handlers.get(SubEventTest) == [method]


def test_add_handler_event_and_sub_event(method):
    webhook_handler.register_method_for_event(EventTest, method)
    webhook_handler.register_method_for_event(SubEventTest, method)

    assert len(webhook_handler.handlers) == 1
    assert EventTest not in webhook_handler.handlers
    assert webhook_handler.handlers.get(SubEventTest) == [method] * 2


def test_handle_sub_event(method, event_action_request):
    webhook_handler.register_method_for_event(SubEventTest, method)
    handle(*event_action_request)
    method.assert_called_once()
    assert isinstance(method.call_args_list[0].args[0], SubEventTest)


def test_handle_event(method, event_action_request):
    webhook_handler.register_method_for_event(EventTest, method)
    handle(*event_action_request)
    method.assert_called_once()
    assert isinstance(method.call_args_list[0].args[0], SubEventTest)


def test_handle_event_and_sub_event(method, event_action_request):
    webhook_handler.register_method_for_event(EventTest, method)
    webhook_handler.register_method_for_event(SubEventTest, method)
    handle(*event_action_request)
    assert method.call_count == 2
    assert all(isinstance(args, SubEventTest) for args in method.call_args_list[0].args)


def test_event_handler_method_validation():
    def method_right(event):
        return event

    def method_wrong():
        return None

        # noinspection PyTypeChecker

    _validate_signature(method_right)
    with pytest.raises(webhook_handler.SignatureError) as err:
        # noinspection PyTypeChecker
        _validate_signature(method_wrong)

    expected_message = (
        "Method test_event_handler_method_validation.<locals>.method_wrong() "
        "signature error. The method must accept only one argument of the Event type"
    )
    assert str(err.value.message) == expected_message


def test_handle_with_load_config(event, event_action_request):
    def method(event):
        return event

    webhook_handler.register_method_for_event(EventTest, method)
    with patch("githubapp.webhook_handler.Config") as config:
        handle(*event_action_request, config_file="file")
        config.load_config_from_file.assert_called_once_with("file", ANY)
