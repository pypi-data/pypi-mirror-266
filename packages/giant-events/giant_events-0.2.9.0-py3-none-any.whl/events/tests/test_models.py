import pytest
from events.models import Event, Tag

from .conftest import *


class TestTag:
    """
    Test case for the EventTag model
    """

    def test_str_method(self):
        """
        Testing object str method by asserting against a known tag string
        """

        tag = Tag(name="Test Tag")
        assert str(tag) == "Test Tag"


class TestEvent:
    """
    Test case for the Event model
    """

    def test_str_method(self):
        """
        Testing object str method by asserting against a known title string
        """

        event = Event(title="Test Title")
        assert str(event) == "Test Title"

    @pytest.mark.django_db
    def test_get_absolute_url_method(self):
        """
        Testing the get absolute url method on the Event model
        """

        event = Event(title="Test Title", slug="test-title")
        assert event.get_absolute_url() == "/events/test-title/"


@pytest.mark.django_db
class TestEventQuerySet:
    """
    Test case for the EventQuerySet class
    """

    def test_published_queryset(self, unpublished_event, published_event):
        """
        Test that the .published method returns the correct queryset objects
        """

        expected_number_of_objects = 1
        assert Event.objects.published().count() == expected_number_of_objects
        assert published_event in Event.objects.published()
        assert unpublished_event not in Event.objects.published()

    def test_future_queryset(self, published_event, unpublished_event):
        """
        Test that the future method returns only items with a future date
        """

        future_event = published_event
        past_event = unpublished_event
        past_event.is_published = True
        past_event.publish_at = timezone.now()

        expected_number_of_objects = 1

        assert Event.objects.future().count() == expected_number_of_objects
        assert future_event in Event.objects.future()
        assert past_event not in Event.objects.future()

    def test_past_queryset(self, published_event, unpublished_event):
        """
        Test that the past method returns only items with a date in the past
        """

        future_event = published_event
        past_event = unpublished_event
        past_event.is_published = True
        past_event.publish_at = timezone.now()
        past_event.save()

        expected_number_of_objects = 1

        assert Event.objects.future().count() == expected_number_of_objects
        assert future_event not in Event.objects.past()
        assert past_event in Event.objects.past()
