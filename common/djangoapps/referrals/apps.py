from django.apps import AppConfig


class ReferralsConfig(AppConfig):
    name = 'referrals'
    verbose_name = "Referrals"

    def ready(self):
        import referrals.signals  # pylint: disable=unused-import
