import logging
import time
from typing import Union

from jira import JIRA, JIRAError
from jira.resources import GreenHopperResource

from jf_ingest.config import JiraAuthConfig, JiraAuthMethod, JiraDownloadConfig
from jf_ingest.jf_jira.exceptions import JiraRetryLimitExceeded
from jf_ingest.utils import get_wait_time
from typing import Optional

logger = logging.getLogger(__name__)


class JiraAuthenticationException(Exception):
    def __init__(self, *args, original_exception: Optional[Exception] = None):
        self.original_exception = original_exception
        super().__init__(*args)


def get_jira_connection(
    config: Union[JiraAuthConfig, JiraDownloadConfig],
    auth_method: JiraAuthMethod = JiraAuthMethod.BasicAuth,
    max_retries=3,
) -> JIRA:
    """Get a JIRA connection object

    Args:
        config (JiraAuthConfig | JiraDownloadConfig): A JIRA Configuration Object that contains authentication information
        auth_method (JiraAuthMethod, optional): The Authentication method used. BasicAuth and AtlassianConnect are currently supported. Defaults to JiraAuthMethod.BasicAuth.
        max_retries (int, optional): The retry limit used by the JiraConnection.ResilientSession object. Defaults to 3.

    Raises:
        Several Errors can be raised by this class. Please ensure your config is properly set up

    Returns:
        JIRA: A JIRA connection object
    """
    should_ssl_verify = not config.bypass_ssl_verification
    # This is the base Jira Connection KWARGs. For different
    # authentication methods, we will need to add specific fields
    jira_conn_kwargs = {
        "server": config.url,
        "max_retries": max_retries,
        "options": {
            "agile_rest_path": GreenHopperResource.AGILE_BASE_REST_PATH,
            "verify": should_ssl_verify,
            "headers": {
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "Accept": "application/json,*/*;q=0.9",
                "X-Atlassian-Token": "no-check",
            },
        },
    }
    if auth_method.value == JiraAuthMethod.AtlassianConnect.value:
        if not config.connect_app_active:
            raise RuntimeError(
                f'Atlassian connect integration for {config.company_slug} is disabled. Check "connect_app_active" flag state.'
            )

        # The customer has installed our Atlassian Connect app; we authenticate to the Jira
        # API using the JWT attributes
        shared_secret = config.jwt_attributes.get("sharedSecret")
        client_key = config.jwt_attributes.get("clientKey")
        key = config.jwt_attributes.get("key")

        if not (shared_secret and client_key and key):
            raise RuntimeError(
                f"Atlassian connect integration for {config.company_slug} is misconfigured"
            )

        logger.info(f"Authenticating to Jira API at {config.url} using JWT attributes")
        jira_conn_kwargs['jwt'] = {
            "secret": shared_secret,
            "payload": {"iss": key, "aud": client_key},
        }
        jira_conn = JIRA(**jira_conn_kwargs)

    elif auth_method.value == JiraAuthMethod.BasicAuth.value:
        if config.user:
            logger.info(
                f"Authenticating to Jira API at {config.url} "
                f"using the username and password secrets for {config.user} of company {config.company_slug}"
            )
            # Add in basic auth infor
            jira_conn_kwargs['basic_auth'] = (config.user, config.password)
        elif config.personal_access_token:
            logger.info(
                f"Authenticating to Jira API at {config.url} "
                f"using the personal_access_token secret for {config.company_slug}"
            )
            # Add in personal access token
            jira_conn_kwargs['options']['headers'][
                'Authorization'
            ] = f"Bearer {config.personal_access_token}"
        else:
            raise RuntimeError(
                f"No valid basic authentication mechanism for {config.url} - need a username/password combo or a personal access token"
            )

        retries = 0
        while True:
            try:
                jira_conn = JIRA(**jira_conn_kwargs)
                break
            except JIRAError as e:  # catch generic error raised from JIRA
                if hasattr(e, "status_code") and e.status_code in (401, 403):
                    raise JiraAuthenticationException(
                        f"Jira authentication (HTTP ERROR CODE {e.status_code}) failed for {config.url} using {config.user} and the jira_password secret for {config.company_slug}",
                        original_exception=e
                    )
                elif hasattr(e, "status_code") and e.status_code == 429:
                    if retries < max_retries:
                        retries += 1
                        sleep_secs = get_wait_time(e, retries)
                        logger.info(
                            f"Caught JIRAError with a {e.status_code} return code during get_jira_connection. "
                            f"Hopefully transient; sleeping for {sleep_secs} secs then may retry ({retries} of {max_retries})."
                        )
                        time.sleep(sleep_secs)
                    else:
                        raise JiraRetryLimitExceeded(
                            f"Jira Authentication returned status code {e.status_code}. We attempted {retries} retries before raising this exception"
                        )
                else:
                    raise
    else:
        raise RuntimeError(
            f"No valid authentication mechanism for {config.url} (Auth Method: {auth_method})."
        )

    # set user-agent
    jira_conn._session.headers[
        "User-Agent"
    ] = f'{config.user_agent} ({jira_conn._session.headers["User-Agent"]})'

    return jira_conn
