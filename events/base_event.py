# Base event class
# Do not modify!
class BaseEvent:
    def __init__(self, trigger_mode, kwargs):
        # follow https://apscheduler.readthedocs.io/en/stable/py-modindex.html
        # https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html#module-apscheduler.triggers.cron
        # https://apscheduler.readthedocs.io/en/stable/modules/triggers/date.html#module-apscheduler.triggers.date
        # https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html#module-apscheduler.triggers.interval
        # https://apscheduler.readthedocs.io/en/stable/modules/triggers/combining.html#module-apscheduler.triggers.combining

        self.trigger_mode = trigger_mode
        self.kwargs = kwargs

    # Every event must override this method
    async def run(self, client):
        raise NotImplementedError  # To be defined by every event
