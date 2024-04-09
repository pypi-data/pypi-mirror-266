from django.conf import settings
from django.views.generic import DetailView, ListView

from .models import Event


class EventIndex(ListView):
    """
    Index view for events queryset
    """

    model = Event
    context_object_name = "events"
    template_name = "events/index.html"
    paginate_by = settings.PAGINATE_EVENTS_BY

    class TimeDirection:
        FUTURE = "future"
        PAST = "past"
        ANYTIME = "anytime"

    @property
    def time_direction(self):
        if self.TimeDirection.PAST in self.request.GET:
            return self.TimeDirection.PAST
        elif self.TimeDirection.FUTURE in self.request.GET:
            return self.TimeDirection.FUTURE
        else:
            return settings.DEFAULT_TIME_DIRECTION

    def get_queryset(self):
        """
        Override get method here to allow us to filter using tags
        """
        time_direction_queryset_mapping = {
            self.TimeDirection.PAST: Event.objects.past(user=self.request.user).order_by(
                "-start_at", "-publish_at",
            ),
            self.TimeDirection.FUTURE: Event.objects.future(user=self.request.user).order_by(
                "start_at", "-publish_at",
            ),
            "default": Event.objects.published(user=self.request.user).order_by("-publish_at"),
        }
        default = time_direction_queryset_mapping.get("default")
        return time_direction_queryset_mapping.get(self.time_direction, default)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_direction"] = self.time_direction

        return context


class EventDetail(DetailView):
    """
    Detail view for an events object
    """

    template_name = "events/detail.html"

    def get_queryset(self):
        """
        Override the default queryset method so that we can access the request.user
        """
        if self.queryset is None:
            return Event.objects.published(user=self.request.user)
        return self.queryset
