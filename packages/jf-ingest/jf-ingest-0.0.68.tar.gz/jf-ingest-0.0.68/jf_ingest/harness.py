import logging
import os
import sys
from datetime import datetime

import pytz
import urllib3
import yaml

from jf_ingest.config import GitAuthConfig, GitConfig
from jf_ingest.jf_git.adapters import load_and_push_git_to_s3
from jf_ingest.jf_jira import IngestionConfig, load_and_push_jira_to_s3
from jf_ingest.jf_jira.auth import JiraDownloadConfig
from jf_ingest.validation import validate_git, validate_jira

logger = logging.getLogger(__name__)

# Start of Epoch Time
_default_datetime_str = '1970-01-01'


def setup_harness_logging(logging_level: int):
    """Helper function to setting up logging in the harness"""
    logging.basicConfig(
        level=logging_level,
        format=(
            "%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s"
            if logging_level == logging.DEBUG
            else "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger(urllib3.__name__).setLevel(logging.WARNING)


def _process_jira_config(general_config_data: dict) -> JiraDownloadConfig:
    jira_config_data = general_config_data["jira_config"]
    # Translate Datetimes first
    jira_config_data["work_logs_pull_from"] = datetime.strptime(
        jira_config_data.get("work_logs_pull_from", _default_datetime_str), "%Y-%m-%d"
    )
    jira_config_data["earliest_issue_dt"] = datetime.strptime(
        jira_config_data.get("earliest_issue_dt", _default_datetime_str), "%Y-%m-%d"
    )
    # Generate object in memory
    jira_config = JiraDownloadConfig(**jira_config_data)
    jira_config.url = os.getenv("JIRA_URL")
    jira_config.user = os.getenv("JIRA_USERNAME")
    jira_config.password = os.getenv("JIRA_PASSWORD")
    return jira_config


def _process_git_configs(general_config_data: dict) -> list[GitConfig]:
    git_config_data = general_config_data["git_configs"][0]
    company_slug = git_config_data['company_slug']
    # Process 'default' time for repos and commits
    git_config_data["default_pull_from_for_commits_and_prs"] = datetime.strptime(
        git_config_data.get("default_pull_from_for_commits_and_prs", _default_datetime_str),
        "%Y-%m-%d",
    ).replace(tzinfo=pytz.UTC)

    def _process_pr_or_commits_pull_from_values(commits_or_prs: str):
        # Translate pull_commits_since_for_repo_in_org
        for org_login in git_config_data.get(
            f'pull_{commits_or_prs}_since_for_repo_in_org', {}
        ).keys():
            for repo_id, date_str in git_config_data[
                f'pull_{commits_or_prs}_since_for_repo_in_org'
            ][org_login].items():
                git_config_data[f'pull_{commits_or_prs}_since_for_repo_in_org'][org_login][
                    repo_id
                ] = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=pytz.UTC)

    _process_pr_or_commits_pull_from_values('commits')
    _process_pr_or_commits_pull_from_values('prs')

    # Create separate auth config
    auth_config = GitAuthConfig(
        company_slug=company_slug,
        token=os.getenv('GITHUB_TOKEN'),
        base_url='',
        verify=False,
        session=None,
    )
    return [GitConfig(git_auth_config=auth_config, **git_config_data)]


if __name__ == "__main__":
    """
    NOTE: This is a work in progress developer debugging tool.
    it is currently run by using the following command:
       pdm run ingest_harness [--debug]
    and it requires you to have a creds.env and a config.yml file at
    the root of this project
    """
    debug_mode = "--debug" in sys.argv
    validate_mode = "--validate" in sys.argv
    run_git_harness = '--git' in sys.argv
    run_jira_harness = '--jira' in sys.argv

    if not run_git_harness and not run_jira_harness:
        # If neither the git or jira arg are supplied, run validation for both
        run_git_harness = True
        run_jira_harness = True

    # Get Config data for Ingestion Config
    with open("./config.yml") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        general_config_data = yaml_data["general"]
        ingest_config = IngestionConfig(
            timestamp=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            jellyfish_api_token=os.getenv("JELLYFISH_API_TOKEN"),
            **general_config_data,
        )
        ingest_config.company_slug = (os.getenv("COMPANY_SLUG"),)
        ingest_config.local_file_path = f"{ingest_config.local_file_path}/{ingest_config.timestamp}"

        # Processes Jira Info
        if run_jira_harness:
            if 'jira_config' in general_config_data:
                ingest_config.jira_config = _process_jira_config(general_config_data)
            else:
                logger.warning(
                    f'Attempted to run Jira Validation but the Jira Config was not found in the config.yml file'
                )

        # Process Git Info
        if run_git_harness:
            if 'git_configs' in general_config_data:
                ingest_config.git_configs = _process_git_configs(general_config_data)
            else:
                logger.warning(
                    f'Attempting to run Git Validation but the Git Config was not found in the config.yml file'
                )

    setup_harness_logging(logging_level=logging.DEBUG if debug_mode else logging.INFO)

    if validate_mode:
        if run_jira_harness and 'jira_config' in general_config_data:
            validate_jira(ingest_config.jira_config)
        if run_git_harness and 'git_configs' in general_config_data:
            validate_git(ingest_config.git_configs)
    else:
        if run_jira_harness:
            load_and_push_jira_to_s3(ingest_config)
        if run_git_harness:
            load_and_push_git_to_s3(ingest_config)
