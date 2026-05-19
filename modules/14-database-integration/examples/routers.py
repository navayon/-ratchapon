# routers.py — Module 14 example
# Place this file at: analytics/routers.py
#
# Register in settings.py:
#   DATABASE_ROUTERS = ['analytics.routers.AnalyticsRouter']
#
# How it works:
#   • Models inside the 'analytics' Django app are always read from / written to
#     the 'analytics' database alias.
#   • All other models continue to use the 'default' database.
#   • Cross-database relations are blocked to avoid integrity errors.


class AnalyticsRouter:
    """
    Route all database operations for models in the 'analytics' app to the
    'analytics' database alias.
    """

    ANALYTICS_APP = 'analytics'

    def db_for_read(self, model, **hints):
        """Point reads for analytics models to the analytics database."""
        if model._meta.app_label == self.ANALYTICS_APP:
            return 'analytics'
        return None  # fall through to the next router / default

    def db_for_write(self, model, **hints):
        """Point writes for analytics models to the analytics database."""
        if model._meta.app_label == self.ANALYTICS_APP:
            return 'analytics'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only when both objects live in the same database tier.
        Blocks FK / M2M relations that would span across the two databases.
        """
        analytics_set = {self.ANALYTICS_APP}
        in_analytics = {obj1._meta.app_label, obj2._meta.app_label}
        if in_analytics <= analytics_set:
            return True          # both in analytics DB — allow
        if not in_analytics & analytics_set:
            return True          # neither in analytics DB — allow
        return False             # mixed — block

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure analytics app migrations only run against the analytics database,
        and that all other migrations run only against the default database.
        """
        if app_label == self.ANALYTICS_APP:
            return db == 'analytics'
        return db == 'default'
