from django.utils import timezone

import pytest

from events.models import Event


@pytest.fixture
def unpublished_event():
    _date = timezone.now() - timezone.timedelta(days=1)
    return Event.objects.create(
        title="Event One",
        slug="event-one",
        start_at=_date,
        end_at=_date,
        is_published=False,
        publish_at=timezone.now() + timezone.timedelta(hours=1),
    )


@pytest.fixture
def published_event():
    return Event.objects.create(
        title="Event Two",
        slug="event-two",
        start_at=timezone.now() + timezone.timedelta(days=1),
        is_published=True,
        publish_at=timezone.now() - timezone.timedelta(hours=1),
    )
