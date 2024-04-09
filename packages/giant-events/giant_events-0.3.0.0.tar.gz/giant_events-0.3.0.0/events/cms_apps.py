from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class EventsApp(CMSApp):
    """
    App hook for Events app
    """

    app_name = "events"
    name = "Events"

    def get_urls(self, page=None, language=None, **kwargs):
        """
        Return the path to the apps urls module
        """

        return ["events.urls"]
