import json
import re

import requests


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
        jobs = requests.get(self.SOURCES[source])
        json.dump(
            self.info_from_markdown_remoteintech(jobs.text.split("\n")),
            open(f"{source}.json", "w+"),
            indent=2,
        )
