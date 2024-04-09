import configparser
import os
import random
import re
from datetime import datetime, timedelta

import humanize
import requests

from apptrackr.model.model import Applications


class FetchJobs:
    SOURCES = {
        "remote-jobs": "https://raw.githubusercontent.com/remoteintech/remote-jobs/main/README.md"
    }

    def info_from_markdown_remoteintech(self, lines: list[str]):
        company_info = {}

        for line in lines:
            match_name = re.search(r"\[(.*?)\]", line)
            match_link = re.search(r"(https?://\S+)", line)

            if match_name and match_link:
                company_info[match_name.group(1)] = match_link.group(1).strip()

        return company_info

    def get(self, source: str) -> dict[str, str]:
        jobs = requests.get(self.SOURCES[source], timeout=3)
        return self.info_from_markdown_remoteintech(jobs.text.split("\n"))


def check_recommendations() -> bool:
    BASE_PATH = os.path.join(
        os.path.expanduser("~"), r"Library/Application Support/apptrackr.toml"
    )
    config = configparser.ConfigParser()
    config.read(BASE_PATH)
    return config.has_option("NETWORK", "enable-recommendations")


def get_last_applied_on() -> str:
    application = (
        Applications.select(Applications.date)
        .order_by(Applications.application_id.desc())
        .limit(1)
        .get()
    )

    company = None
    link = None
    application_date = datetime.strptime(application.date, "%Y-%m-%d %H:%M:%S.%f")
    current_time = datetime.now()
    time_difference = current_time - application_date

    if check_recommendations() and time_difference > timedelta(hours=6):
        company, link = get_new_job()

    return humanize.naturaltime(time_difference), company, link


def get_new_job() -> tuple[str, str]:
    jobs = FetchJobs().get(source="remote-jobs")
    return random.choice(list(jobs.items()))
