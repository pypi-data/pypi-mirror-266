from django.test import Client
from django.urls import reverse

import pytest
from events import models
from events.views import EventIndex

from .conftest import *


@pytest.mark.django_db
class TestEventView:
    """
    Test case for the Event app views
    """

    @pytest.fixture
    def future_event_instance(self):
        return models.Event.objects.create(
            title="Future Event",
            slug="future-event",
            start_at=timezone.now() + timezone.timedelta(days=1),
            is_published=True,
            publish_at=timezone.now() - timezone.timedelta(hours=1),
        )

    @pytest.fixture
    def past_event_instance(self):
        return models.Event.objects.create(
            title="Past Event",
            slug="past-event",
            start_at=timezone.now() - timezone.timedelta(days=1),
            is_published=True,
            publish_at=timezone.now() - timezone.timedelta(hours=1),
        )

    def test_event_detail(self, future_event_instance):
        """
        Test the detail view returns the correct status code
        """

        client = Client()
        event = future_event_instance
        response = client.get(reverse("events:detail", kwargs={"slug": event.slug}))
        assert response.status_code == 200

    def test_event_index(self):
        """
        Test the index view returns the correct status code
        """
        client = Client()
        response = client.get(reverse("events:index"))
        assert response.status_code == 200

    def test_unpublished_returns_404(self, unpublished_event):
        """
        Test to check that an unpublished event returns a 404
        """
        client = Client()
        response = client.get(
            reverse("events:detail", kwargs={"slug": unpublished_event.slug})
        )

        assert response.status_code == 404

    def test_update_context(self, future_event_instance):
        """
        Test the context update returns published events queryset
        """
        client = Client()
        event = future_event_instance
        response = client.get(reverse("events:index"))

        assert event in response.context["object_list"]
        assert event in models.Event.objects.published()

    def test_time_direction(self, client):
        """
        Test the context update returns published events queryset
        """

        url = f"{reverse('events:index')}?{EventIndex.TimeDirection.PAST}"
        response = client.get(url)

        event_index = EventIndex()
        event_index.request = response.wsgi_request

        assert event_index.time_direction == EventIndex.TimeDirection.PAST

    def test_get_queryset(self, client, future_event_instance, past_event_instance):
        """
        Test the context update returns published events queryset
        """

        url = f"{reverse('events:index')}?{EventIndex.TimeDirection.FUTURE}"
        response = client.get(url)

        event_index = EventIndex()
        event_index.request = response.wsgi_request

        event_queryset = event_index.get_queryset()
        assert (
            future_event_instance in event_queryset
            and past_event_instance not in event_queryset
        )
