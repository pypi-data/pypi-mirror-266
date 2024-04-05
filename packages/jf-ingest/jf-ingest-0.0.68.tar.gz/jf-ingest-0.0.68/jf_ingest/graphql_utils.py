import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator

import requests
from requests import Response, Session

from jf_ingest.jf_git.exceptions import GqlRateLimitExceededException
from jf_ingest.utils import retry_for_429s

logger = logging.getLogger(__name__)


GQL_PAGE_INFO_BLOCK = "pageInfo {hasNextPage, endCursor}"
GQL_RATE_LIMIT_QUERY_BLOCK = "rateLimit {remaining, resetAt}"


@dataclass
class GQLRateLimit:
    remaining: int
    reset_at: datetime


class GqlRateLimitedExceptionInner(Exception):
    pass


def gql_format_to_datetime(datetime_str: str) -> datetime:
    """Attempt to formate a datetime str from the GQL format to a python Datetime Object
    NOTE: This currently is only verified to support the github GQL format. It is NOT YET
    GENERALIZED

    Args:
        datetime_str (str): The datetime from graphql

    Returns:
        datetime: A valid, timezone aware datetime
    """
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def get_gql_rate_limit(session: Session, base_url: str) -> GQLRateLimit:
    """Attempt to pull the current rate limit information from GQL
    NOTE: Getting the rate limit info is never affected by the current rate limit

    Args:
        session (Session): A valid session connecting us to the GQL API
        base_url (str): The base URL we are hitting

    Returns:
        dict: A dictionary object containing rate limit information (remaing and resetAt)
    """
    query_body = f"{{{GQL_RATE_LIMIT_QUERY_BLOCK}}}"
    # NOTE: DO NOT CALL get_raw_gql_result TO GET THE RESULTS HERE! IT'S A RECURSIVE TRAP
    response: Response = retry_for_429s(session.post, url=base_url, json={'query': query_body})
    response.raise_for_status()
    json_str = response.content.decode()
    raw_data: dict = json.loads(json_str)['data']['rateLimit']
    return GQLRateLimit(
        remaining=int(raw_data['remaining']), reset_at=gql_format_to_datetime(raw_data['resetAt'])
    )


def get_raw_gql_result(
    session: Session, gql_base_url: str, query_body: str, max_attempts: int = 7
) -> dict:
    """Gets the raw results from a Graphql Query.

    Args:
        session (Session): A valid session object connecting us to the GQL API
        gql_base_url (str): The base URL for the GQL API
        query_body (str): A query body to hit GQL with
        max_attempts (int, optional): The number of retries we should make when we specifically run into GQL Rate limiting. This value is important if the GQL endpoint doesn't give us (or gives us a malformed) rate limit header. Defaults to 7.

    Raises:
        GqlRateLimitExceededException: A custom exception if we run into GQL rate limiting and we run out of attempts (based on max_attempts)
        Exception: Any other random exception we encounter, although the big rate limiting use cases are generally covered

    Returns:
        dict: A raw dictionary result from GQL
    """
    attempt_number = 1
    while True:
        try:
            response: Response = retry_for_429s(
                session.post, url=gql_base_url, json={'query': query_body}
            )
            response.raise_for_status()
            json_str = response.content.decode()
            json_data = json.loads(json_str)
            if 'errors' in json_data:
                if len(json_data['errors']) == 1:
                    error_dict: dict = json_data['errors'][0]
                    if error_dict.get('type') == 'RATE_LIMITED':
                        raise GqlRateLimitedExceptionInner(
                            error_dict.get('message', 'Rate Limit hit in GQL')
                        )
                raise Exception(
                    f'Exception encountered when trying to query: {query_body}. Error: {json_data["errors"]}'
                )
            return json_data
        # We can get transient 403 level errors that have to do with rate limiting,
        # but aren't directly related to the above GqlRateLimitedExceptionInner logic.
        # Do a simple retry loop here
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 403:
                raise
            if attempt_number > max_attempts:
                raise

            sleep_time = attempt_number**2
            # Overwrite sleep time if github gives us a specific wait time
            if e.response.headers.get('retry-after') and attempt_number == 1:
                retry_after = int(e.response.headers.get('retry-after'))
                if retry_after > (60 * 5):
                    # if the given wait time is more than 5 minutes, call their bluff
                    # and try the experimental backoff approach
                    pass
                elif retry_after <= 0:
                    # if the given wait time is negative ignore their suggestion
                    pass
                else:
                    # Add three seconds for gracetime
                    sleep_time = retry_after + 3

            logger.warning(
                f'A secondary rate limit was hit. Sleeping for {sleep_time} seconds. (attempt {attempt_number}/{max_attempts})',
            )
            time.sleep(sleep_time)
        except GqlRateLimitedExceptionInner:
            if attempt_number > max_attempts:
                raise GqlRateLimitExceededException(
                    f'Exceeded maximum retry limit ({max_attempts})'
                )

            rate_limit_info: GQLRateLimit = get_gql_rate_limit(
                session=session, base_url=gql_base_url
            )
            reset_at: datetime = rate_limit_info.reset_at
            reset_at_timestamp = reset_at.timestamp()
            curr_timestamp = datetime.utcnow().timestamp()

            sleep_time = reset_at_timestamp - curr_timestamp

            # Sometimes github gives a reset time way in the
            # future. But rate limits reset each hour, so don't
            # wait longer than that
            sleep_time = min(sleep_time, 3600)

            # Sometimes github gives a reset time in the
            # past. In that case, wait for 5 mins just in case.
            if sleep_time <= 0:
                sleep_time = 300
            logger.warning(
                f'GQL Rate Limit hit. Sleeping for {sleep_time} seconds',
            )
            time.sleep(sleep_time)
        finally:
            attempt_number += 1


def page_results_gql(
    session: Session,
    gql_base_url: str,
    query_body: str,
    path_to_page_info: str,
    cursor: str = 'null',
) -> Generator[dict, None, None]:
    """This is a helper function for paging results from GraphQL. It expects
    a query body to hit Graphql with that has a %s marker after the "after:"
    key word, so that we can inject a cursor into the query. This will allow
    us to page results in GraphQL.
    To use this function properly, the section you are trying to page MUST
    INCLUDE VALID PAGE INFO (including the hasNext and endCursor attributes)

    Args:
        query_body (str): The query body to hit GraphQL with
        path_to_page_info (str): A string of period separated words that lead
        to the part of the query that we are trying to page. Example: data.organization.userQuery
        cursor (str, optional): LEAVE AS NULL - this argument is use recursively to page. The cursor
        will continuously go up, based on the endCursor attribute in the GQL call. Defaults to 'null'.

    Yields:
        Generator[dict, None, None]: This function yields each item from all the pages paged, item by item
    """
    hasNextPage = True
    while hasNextPage:
        # Fetch results
        result = get_raw_gql_result(
            session=session, gql_base_url=gql_base_url, query_body=(query_body % cursor)
        )

        yield result

        # Get relevant data and yield it
        path_tokens = path_to_page_info.split('.')
        for token in path_tokens:
            result = result[token]

        page_info = result['pageInfo']
        # Need to grab the cursor and wrap it in quotes
        _cursor = page_info['endCursor']
        # If endCursor returns null (None), break out of loop
        hasNextPage = page_info['hasNextPage'] and _cursor
        cursor = f'"{_cursor}"'
