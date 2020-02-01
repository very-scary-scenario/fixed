from random import uniform, gauss, choice, choices
from datetime import datetime, timedelta

P_DATE = 0.1
P_FOURTH_DIGIT = 0.05
P_PRE_POST_RELEASE = 0.2
PRE_POST_RELEASE_PREFIXES = ('a', 'alpha', 'b', 'beta', 'u', '.dev')
P_OS_VERSION = 0.01
OS_VERSIONS = {
    'win': {
        'dows': 1,
        '': 2,
        '32': 25,
        '-amd64': 32
    },
    'linux': {
        '': 3,
        '-x86_64': 50,
        '-i686': 10,
        '-armv7l': 4,
        '-armv6l': 1
    },
    'macosx-10.': {
        '6-intel': 4,
        '6-x86_64': 2,
        '7-intel': 2,
        '7-x86_64': 3,
        '8-intel': 2,
        '8-x86_64': 3,
        '9-intel': 1,
        '9-x86_64': 3,
        '10-intel': 3,
        '10-x86_64': 6,
        '11-intel': 7,
        '11-x86_64': 6,
        '12-intel': 8,
        '12-x86_64': 9,
        '13-intel': 8,
        '13-x86_64': 11,
        '14-intel': 10,
        '14-x86_64': 14,
        '15-intel': 8,
        '15-x86_64': 7,
        '16-intel': 6,
        '16-x86_64': 8
    }
}

def random_datetime(p_not_time=0, p_not_day=0, p_not_month=0):
    '''Pick a random datetime and give it back in the form YYYYMMDDhhmmss.
    The time, day, and month can be omitted at random, with probability
    1 - `p_not_time`, 1 - `p_not_day`, and 1 - `p_not_month` respectively.
    By default all are included.
    '''

    # Pick an offset to now, in seconds
    seconds_per_year = 31_557_600
    offset = gauss(0, 20 * seconds_per_year)

    # Don't go too far in the future
    if offset > 0:
        offset /= 10

    target_datetime = datetime.now() + timedelta(seconds=offset)

    timestamp_format = '%Y'

    if not p_not_month or uniform(0, 1) > p_not_month:
        timestamp_format += '%m'

        if not p_not_day or uniform(0, 1) > p_not_day:
            timestamp_format += '%d'

            if not p_not_time or uniform(0, 1) > p_not_time:
                timestamp_format += '%H%M%S'

    return datetime.strftime(target_datetime, timestamp_format)


def random_version():
    '''Generate a random version number.'''

    # Decide if this should be a dotted or a date version number
    if uniform(0, 1) < P_DATE:
        has_date = True
        version = random_datetime(0.2, 0.2, 0.5)
    else:
        has_date = False

        version_components = [
            int(gauss(1.2, 1) ** 2),
            int(gauss(2, 1) ** 2),
            int(gauss(3, 2) ** 2)
        ]
        if uniform(0, 1) < P_FOURTH_DIGIT:
            version_components.append(int(gauss(1, 1) ** 2))
        if uniform(0, 1) < P_DATE:
            version_components.append(random_datetime(0.5))

        version = '.'.join(map(str, version_components))

    if uniform(0, 1) < P_PRE_POST_RELEASE:
        if uniform(0, 1) < P_DATE:
            suffix = random_datetime()
        else:
            suffix = int(gauss(2, 2) ** 2)
        version += '{}{}'.format(
            choice(PRE_POST_RELEASE_PREFIXES),
            suffix
        )

    if uniform(0, 1) < P_OS_VERSION:
        os = choice(list(OS_VERSIONS.keys()))
        revisions = list(OS_VERSIONS[os].keys())
        revision_probs = list(OS_VERSIONS[os].values())

        version += '.{}{}'.format(os, choices(revisions, revision_probs)[0])

    return version
