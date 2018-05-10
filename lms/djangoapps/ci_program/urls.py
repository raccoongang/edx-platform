from django.conf.urls import patterns, url

urlpatterns = patterns(
    'ci_program.views',

    url(r'^(?P<program_name>[\w\-]+)', 'show_programs'),
)