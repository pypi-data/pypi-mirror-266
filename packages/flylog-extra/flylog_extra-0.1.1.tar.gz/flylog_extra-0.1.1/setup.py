from setuptools import setup, find_packages
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    REQUIRE_PACK = ['slackclient>=1.3.2']
    __version__ = "0.1.1"

else:
    REQUIRE_PACK = ['slack_sdk>=3.19.5']
    __version__ = "0.1.1"



setup(
    name="flylog_extra",
    version=__version__,
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    scripts=['flylog_extra/bin/run_flylog.py'],
    url="https://github.com/dkxx00/flylog-extra",
    license="BSD",
    author="dkxx00",
    author_email="hymanxx6@gmail.com",
    description="make log fly to mail or other(slack)",
)
