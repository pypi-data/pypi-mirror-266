from events.cms_apps import EventsApp


class TestEventsApp:
    """
    Test case for the EventsApp
    """

    def test_get_urls_method(self):
        """
        Test get_urls method on the EventsApp class
        """
        assert EventsApp().get_urls() == ["events.urls"]
