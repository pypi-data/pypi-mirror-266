from unittest.mock import Mock

from githubapp.events.event import Event
from tests.conftest import event_action_request
from tests.mocks import EventTest, SubEventTest


# noinspection PyUnresolvedReferences
def test_init(event_action_request):
    headers, body = event_action_request
    SubEventTest(gh=Mock(), requester=Mock(), headers=headers, **body)
    assert Event.github_event == "event"
    assert Event.hook_id == 1
    assert Event.delivery == "a1b2c3d4"
    assert Event.hook_installation_target_type == "type"
    assert Event.hook_installation_target_id == 2


def test_normalize_dicts():
    d1 = {"a": "1"}
    d2 = {"X-Github-batata": "Batata"}

    union_dict = Event.normalize_dicts(d1, d2)
    assert union_dict == {"a": "1", "batata": "Batata"}


def test_get_event(event_action_request):
    headers, body = event_action_request
    assert Event.get_event(headers, body) == SubEventTest
    body.pop("action")
    assert Event.get_event(headers, body) == EventTest


def test_match():
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2}
    d3 = {"a": 1, "b": 1}

    class LocalEventTest(Event):
        pass

    LocalEventTest.event_identifier = d2
    assert LocalEventTest.match(d1) is True
    assert LocalEventTest.match(d3) is False
    LocalEventTest.event_identifier = d1
    assert LocalEventTest.match(d3) is False


def test_lazy_fix_url():
    attributes = {"url": "https://github.com/potato"}
    Event.fix_attributes(attributes)
    assert attributes["url"] == "https://api.github.com/repos/potato"


def test_lazy_fix_url_when_is_correct():
    attributes = {"url": "correct_url"}
    Event.fix_attributes(attributes)
    assert attributes["url"] == "correct_url"


# noinspection PyTypeChecker
def test_parse_object():
    mocked_class = Mock()
    self = Mock(requester="requester")
    EventTest._parse_object(self, mocked_class, {"a": 1})
    self.fix_attributes.assert_called_with({"a": 1})
    mocked_class.assert_called_with(requester="requester", headers={}, attributes={"a": 1}, completed=False)


# noinspection PyTypeChecker
def test_parse_object_when_value_is_none():
    mocked_class = Mock()
    self = Mock(requester="requester")
    EventTest._parse_object(self, mocked_class, None)
    self.fix_attributes.assert_not_called()
    mocked_class.assert_not_called()


def test_start_check_run(event):
    event.start_check_run("name", "sha", "title")
    event.repository.create_check_run.assert_called_with(
        "name", "sha", status="in_progress", output={"title": "title", "summary": ""}
    )


def test_start_check_run_with_summary_and_text(event):
    event.start_check_run("name", "sha", "title", summary="summary", text="text")
    event.repository.create_check_run.assert_called_with(
        "name",
        "sha",
        status="in_progress",
        output={"title": "title", "summary": "summary", "text": "text"},
    )


def test_update_check_run_with_only_status(event):
    event.start_check_run("name", "sha", "title")
    event.update_check_run(status="status")
    event.check_run.edit.assert_called_with(status="status")


def test_update_check_run_with_only_conclusion(event):
    event.start_check_run("name", "sha", "title")
    event.update_check_run(conclusion="conclusion")
    event.check_run.edit.assert_called_with(status="completed", conclusion="conclusion")


def test_update_check_run_with_output(event):
    event.start_check_run("name", "sha", "title", "summary")
    event.update_check_run(title="new_title", summary="new_summary")
    event.check_run.edit.assert_called_with(output={"title": "new_title", "summary": "new_summary"})


def test_update_check_run_with_only_output_text(event):
    event.start_check_run("name", "sha", "title")
    event.check_run.output.title = "title"
    event.check_run.output.summary = "summary"
    event.update_check_run(text="text")
    event.check_run.edit.assert_called_with(output={"title": "title", "summary": "summary", "text": "text"})


def test_update_check_run_with_nothing(event):
    event.start_check_run("name", "sha", "title")
    event.update_check_run()
    event.check_run.edit.assert_not_called()
