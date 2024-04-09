from setuptools import setup

__version__ = "1.23.0"

if __name__ == "__main__":
    setup(
        install_requires=[
            "hiredis",
            "louie",
            "numpy",
            "scipy",
            "msgpack",
            "requests",
            "typeguard>=4.0.1",
            "pyyaml",
            "redis",
            "toolz",
            "rich",
            "pylint",
            "loguru",
            "psutil",
            "fpdf",
            "fastjsonschema",
            "lmfit",
        ],
        extras_require={
            "dev": [
                "pytest",
                "pytest-random-order",
                "pytest-redis",
                "pytest-timeout",
                "coverage",
                "pandas",
                "black",
                "isort",
                "pylint",
                "fakeredis",
            ]
        },
        entry_points={
            "console_scripts": ["bec-channel-monitor = bec_lib:channel_monitor_launch"],
            "pytest11": [
                "bec_lib_end2end_fixtures = bec_lib.tests.end2end_fixtures",
                "bec_lib_fixtures = bec_lib.tests.fixtures",
            ],
        },
        package_data={"bec_lib.tests": ["*.yaml"], "bec_lib.configs": ["*.yaml", "*.json"]},
        version=__version__,
    )
