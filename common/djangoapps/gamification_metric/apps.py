from django.apps import AppConfig


class GamificationMetricConfig(AppConfig):
    name = 'gamification_metric'
    verbose_name = "Gamification Metric"

    def ready(self):
        import gamification_metric.signals  # pylint: disable=unused-import
