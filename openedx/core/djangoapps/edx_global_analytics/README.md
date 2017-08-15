# edX global analytics

`EdX global analytics` is part of edx-platform as Django application. It has arisen out of [Open edX](https://open.edx.org)
requirement to collect edx-platform installations statistics data from all over the world.

Once at 24 hours this application fetches and sends edX installation statistics to [OLGA](https://github.com/raccoongang/OLGA) developed by @raccoongang team.
OLGA is required to be able to collect, visualize and process this data. It provides possibilities for analysing trends of platform usage
and users engagement in e-learning process per country and globally around the world.
It is currently carried out via graphs, world map and activity metrics.

## Sent statistics to OLGA looks like

![olga_world_map](https://user-images.githubusercontent.com/22666467/27970248-d015fd9c-6356-11e7-906c-8c052cd65b08.png)

## Types of statistics sent, and dependence on statistics level

Firstly, `statistic level` is a string constant in settings (`lms.env.json`) which regulates size of statistics platform sends.
It is optional point, if you leave blank string there, it will work on `Paranoid` level (described below).

`Paranoid` level with paranoid constant allows platform to transfer:
1. Access token for OLGA server.
2. Active students amount per last calendar day, week and month (active student is a student whose last login datetime
value is included in particular calendar period).
3. Courses amount.

`Enthusiast` level and the last one with `enthusiast` constant extends `Paranoid` level with:
1. Platform URL and platform name.
2. Platform's latitude and longitude.
3. Active students per country accordance for last calendar day.

\*active student is a student whose last login datetime value is included in particular calendar periods (day, week or month).

## Settings of application

Platform's administrator (developer, devops) is able to configure `EdX global analytics` settings in `lms.env.json`.
This settings already exist after default platform installation, developer just needs to change it.

Settings context:

```
...,
"OPENEDX_LEARNERS_GLOBAL_ANALYTICS": {
    "ACCEPTOR_URL": "",
    "ACCEPTOR_URL_DEVELOP": "http://192.168.1.10:7000",
    "CELERY_TIMEZONE": "Europe/Kiev",
    "PLATFORM_CITY_NAME": "Kiev",
    "STATISTICS_LEVEL": "paranoid"
}, ...
```

`CELERY_TIMEZONE`: Time zone in edx-platform is enabled by default, platform's developer can set time zone in `lms.env.json` for `TIME_ZONE` key.

`EdX global analytics` supports own time zone setting — time zone platform will fetch and send statistics to OLGA.
It is needed because server with platform can be located in one place, but organization (for example university and students), that owns this platform, in another.

`OLGA_ACCEPTOR_PERIODIC_TASK_URL` and `OLGA_ACCEPTOR_PERIODIC_TASK_URL_LOCAL_DEV` are URLs that platform transfer statistics to. It depends on platform status: development or production.

`PLATFORM_CITY_NAME` — set city name platform located in for gathering latitude and longitude.
It will be callected only if statistics level is `enthusiast`.

`STATISTICS_LEVEL` — direct statistics level (explained above).

## Production

To turn on sharing extended statistics, change `STATISTICS_LEVEL` to `enthusiast` (it is `paranoid` by default).

## Development details

Developer is able to change `ACCEPTOR_URL_DEVELOP` point to local enviroment host (for example `localhost`).

### Tests

You are able to run unit tests from `edx-platform` directory with command:

```
paver test_system -t openedx/core/djangoapps/edx_global_analytics/tests
```

### Celery

Run celery task locally with command:

```
./manage.py lms celery worker -B --settings=devstack_with_worker
```

## Application's architecture

### Celery

Celery run one task once per day at time between `00:01` and `00:59` for sending statistics.

Celery settings located in `lms/envs/aws.py`:

```
For scheduling tasks, need to be added to this dict.
CELERYBEAT_SCHEDULE = {
    """
    'collect_stats' is the celery periodic task that gathers information about the
    students amount, geographical coordinates of the platform, courses amount and
    makes a POST request with the data to the appropriate service.
    """

    'collect_stats': {
        'task': 'openedx.core.djangoapps.edx_global_analytics.tasks.collect_stats',
        'schedule': crontab(hour=0, minute=random.randint(1, 59)),
    }
}
```

Random exists for OLGA server, that can receive statistics not at one moment from bunch of servers.

### API

Task explained above uses [OLGA API endpoints](https://github.com/raccoongang/OLGA#api) for dispatching statistics:
1. Registers itself on OLGA server if did not do it earlier.
2. Authorizes on server with access token, which it got after registration.
3. Sends platform statistics.
