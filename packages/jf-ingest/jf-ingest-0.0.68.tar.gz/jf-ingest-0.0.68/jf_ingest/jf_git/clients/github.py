import json
import logging
import time
from datetime import datetime, timezone
from typing import Generator

import jwt
import requests
from dateutil import parser
from requests.utils import default_user_agent

from jf_ingest.config import GithubAuthConfig
from jf_ingest.constants import Constants
from jf_ingest.graphql_utils import GQL_PAGE_INFO_BLOCK, get_raw_gql_result, page_results_gql
from jf_ingest.utils import retry_session

logger = logging.getLogger(__name__)

GIT_DEFAULT_API_ENDPOINT = 'https://api.github.com'


def parse_date(dt):
    if dt is None:
        return None
    return parser.parse(dt)


class GithubClient:
    # This uses GQL to hit the Github API!

    GITHUB_GQL_USER_FRAGMENT = "... on User {login, id: databaseId, email, name, url}"
    # Need to make a second, special actor fragment to make sure we grab
    # the proper ID from either a bot or a User
    GITHUB_GQL_ACTOR_FRAGMENT = """
        ... on Actor 
            { 
                login 
                ... on User { id: databaseId, email, name } 
                ... on Bot { id: databaseId}
            }
    """
    # NOTE: On the author block here, we have a type GitActor
    # We cannot always get the email from the nested user object,
    # so pull whatever email we can from the gitActor top level object.
    # (we can't get the email from the user object bc of variable privacy configuration)
    GITHUB_GQL_COMMIT_FRAGMENT = f"""
        ... on Commit {{
            sha: oid
            url
            author {{
                ... on GitActor {{
                    email
                    name
                    user {{ id: databaseId, login }}
                }}
            }}
            message
            committedDate
            authoredDate
            parents {{totalCount}}
        }}
    """
    GITHUB_GQL_SHORT_REPO_FRAGMENT = "... on Repository {name, id:databaseId, url}"

    # The PR query is HUGE, we shouldn't query more than about 25 at a time
    MAX_PAGE_SIZE_FOR_PR_QUERY = 25

    def __init__(
        self, github_auth_config: GithubAuthConfig, **kwargs,
    ):
        """This is a wrapper class for interacting with the Github GQL endpoint. It supports
        both cloud and enterprise. It works by either accepting a provided token or by using
        the other args to set up JWT authentication (see: https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/)

        Args:
            token (str, optional): An optional authentication token. If not provided we will use the other args to get a JWT token. See GithubClient._get_app_access_token. Defaults to None.
            installation_id (str, optional): A client provided installation ID, used for JWT authentication. Defaults to None.
            app_id (str, optional): A client provided App Id, used for JWT authentication. Defaults to None.
            private_key (str, optional): A user provided private key, used for JWT authentication. Defaults to None.
            base_url (str, optional): An optional base url, used by Github Enterprise customers. Defaults to None.
            verify (bool, optional): Session arg. Defaults to True.
            session (requests.Session, optional): An optional session to pass this client, if you've already set up an authenticated session. Defaults to None.
            company_slug (str, optional): An optional str giving this class context what company this client is for. Defaults to None.
        """

        self.company_slug = github_auth_config.company_slug
        self.gql_base_url = self.get_github_gql_base_url(base_url=github_auth_config.base_url)
        # We need to hit the REST API for some API calls, see get_organization_by_name and _get_app_access_token
        self.rest_api_url = github_auth_config.base_url or GIT_DEFAULT_API_ENDPOINT

        if github_auth_config.token is None:
            self.installation_id = github_auth_config.installation_id
            self.app_id = github_auth_config.app_id
            self.private_key = github_auth_config.private_key
            self.token, self.token_expiration = self._get_app_access_token()
            self.uses_jwt = True
        else:
            self.token = github_auth_config.token
            self.token_expiration = None
            self.uses_jwt = False

        self.session = github_auth_config.session or retry_session(**kwargs)
        self.session.verify = True
        self.session.headers.update(
            {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github+json',
                'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
            }
        )

    @staticmethod
    def datetime_to_gql_str_format(_datetime: datetime) -> str:
        return _datetime.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def get_github_gql_base_url(base_url: str) -> str:
        # the URL for GQL things is different from what we need to get a token
        if base_url and 'api/v3' in base_url:
            # Github server clients provide an API with a trailing '/api/v3'
            # replace this with the graphql endpoint
            return base_url.replace('api/v3', 'api/graphql')
        else:
            return f'{GIT_DEFAULT_API_ENDPOINT}/graphql'

    @staticmethod
    def create_jwt_token(app_id, private_key):
        now = int(time.time()) - 60
        payload = {"iat": now, "exp": now + 600, "iss": app_id}
        jwt_token = jwt.encode(payload, key=private_key, algorithm="RS256")
        jwt_token = jwt_token.decode('utf-8')
        return jwt_token

    def get_raw_result(self, query_body: str) -> dict:
        """This is a wrapper function for the get_raw_gql_result utility funcion

        Args:
            query_body (str): A query body to hit GQL with

        Returns:
            dict: A dict that GQL returns
        """
        return get_raw_gql_result(
            session=self.session, gql_base_url=self.gql_base_url, query_body=query_body
        )

    def page_results_gql(self, query_body: str, path_to_page_info: str) -> dict:
        """This is a wrapper function for the page_results_gql utility funcion

        Args:
            query_body (str): A query body to hit GQL with
            path_to_page_info (str): A string of period separated words that lead
            to the part of the query that we are trying to page. Example: data.organization.userQuery

        Returns:
            dict: A dict that GQL returns
        """
        return page_results_gql(
            session=self.session,
            gql_base_url=self.gql_base_url,
            query_body=query_body,
            path_to_page_info=path_to_page_info,
        )

    def _get_app_access_token(self):
        """
        Authenticating a github app requires encoding the installation id, and private key
        into a JWT token in order to request a access_token from the server.
        See: https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/
        """

        base_url = self.rest_api_url

        # create the jwt_token to authenticate request
        jwt_token = GithubClient.create_jwt_token(app_id=self.app_id, private_key=self.private_key)

        # fetch token from the server
        response = requests.post(
            url=f'{base_url}/app/installations/{self.installation_id}/access_tokens',
            headers={
                'Accept': 'application/vnd.github.machine-man-preview+json',
                'Authorization': f'Bearer {jwt_token}',
                'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
            },
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code in (403, 404):
                msg = (
                    f"Got HTTP {e.response.status_code} when attempting to create a GithubClient the this address: {base_url}. "
                    "This means our app does not have permission to access the customer's github instance. "
                    "This usually happens when either permissions have intentionally revoked or if an access token expires. "
                    "Set the JFGithubInstance to enabled=False to skip this GitHub instance but allow pulling from any other instances to complete successfully. "
                )
                raise Exception(msg)

            raise

        response_data = response.json()
        token = response_data['token']
        token_expiration = parse_date(response_data['expires_at'])
        logger.info(
            f'Obtained token successfully - new token will expire in 60m at {token_expiration}'
        )
        return token, token_expiration

    def _check_token_expiration(self):
        if self.token_expiration:
            mins_until_expiration = (
                self.token_expiration - datetime.now(timezone.utc)
            ).total_seconds() / 60
            if mins_until_expiration < 10:
                logger.info(
                    f'Token is going to expire in {mins_until_expiration:.1f} minutes -- obtaining a new token.'
                )
                # refresh token
                self.token, self.token_expiration = self._get_app_access_token()
                self.session.headers.update(
                    {
                        'Accept': 'application/json',
                        'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
                        'Authorization': f'token {self.token}',
                    }
                )

    # This is for commits, specifically the 'author' block within them.
    # On the GQL side of things, these are specifically a distinct type of object,
    # GitActor. It has a nested user object, but the quality of data within it
    # is variable due to a users privacy settings. Email, for example, is often
    # not present in the child user block, so we always grab it from the top level.
    @staticmethod
    def _process_git_actor_gql_object(author: dict) -> dict:
        user: dict = author.get('user') or {}
        return {
            'id': user.get('id'),
            'login': user.get('login'),
            'email': author['email'],
            'name': author['name'],
        }

    def get_scopes_of_api_token(self):
        # Make an empty call against the orgs API to be quick
        # and get the OAuth scopes
        url = f'{self.rest_api_url}/orgs/'
        result = self.session.get(url)
        return result.headers.get('X-OAuth-Scopes')

    # This is for commits, specifically the 'author' block within them.
    # On the GQL side of things, these are specifically a distinct type of object,
    # GitActor. It has a nested user object, but the quality of data within it
    # is variable due to a users privacy settings. Email, for example, is often
    # not present in the child user block, so we always grab it from the top level.
    @staticmethod
    def _process_git_actor_gql_object(author: dict) -> dict:
        user: dict = author.get('user') or {}
        return {
            'id': user.get('id'),
            'login': user.get('login'),
            'email': author['email'],
            'name': author['name'],
        }

    # HACK: This call will actually use the REST endpoint
    # Agent clients are supposed to have the [org:read] scope,
    # but many of them don't. This wasn't a problem before
    # because the REST org API doesn't actually hide behind any perms...
    # TODO: Once we straighten out everybody's permissions we can sunset
    # this function
    def get_organization_by_login(self, login: str):
        # NOTE: We are hitting a different base url here!
        url = f'{self.rest_api_url}/orgs/{login}'

        result = self.session.get(url)

        # HACK: This appears to happen after we have been
        # rate-limited when hitting certain URLs, there is
        # likely a more elegant way to solve this but it takes
        # about an hour to test each time and it works.
        # NOTE: This is unlikely for this call, because we are only hitting
        # the org once for an entire git config
        if result.status_code == 403:
            result = self.session.get(url)

        result.raise_for_status()
        return result.json()

    def get_users(self, login: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                userQuery: membersWithRole(first: 100, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    users: nodes {{
                        {self.GITHUB_GQL_USER_FRAGMENT}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.userQuery'
        ):
            for user in page['data']['organization']['userQuery']['users']:
                yield user

    def get_team_members(self, login: str, team_slug: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                team(slug: \"{team_slug}\") {{
                    membersQuery: members(first: 100, after: %s) {{
                        {GQL_PAGE_INFO_BLOCK}
                        members: nodes {{
                            {self.GITHUB_GQL_USER_FRAGMENT}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.team.membersQuery'
        ):
            for member in page['data']['organization']['team']['membersQuery']['members']:
                yield member

    def get_teams(self, login: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                teamsQuery: teams(first: 100, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    teams: nodes {{
                        id
                        slug
                        name
                        description
                        membersQuery: members(first: 100) {{
                            {GQL_PAGE_INFO_BLOCK}
                            members: nodes {{
                                {self.GITHUB_GQL_USER_FRAGMENT}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.teamsQuery'
        ):
            for team in page['data']['organization']['teamsQuery']['teams']:
                if team['membersQuery']['pageInfo']['hasNextPage']:
                    logger.debug(
                        f'Team {team["name"]} was detected as having more than {len(team["membersQuery"]["members"])} members, we need to page for additional members'
                    )
                    team['members'] = [
                        member
                        for member in self.get_team_members(login=login, team_slug=team['slug'])
                    ]
                else:
                    team['members'] = team['membersQuery']['members']

                yield team

    def get_repos(
        self, login: str, repo_filters: list[filter] = None
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repoQuery: repositories(first: 50, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    repos: nodes {{
                        ... on Repository {{
                            id: databaseId
                            name
                            fullName: nameWithOwner
                            url
                            isFork
                            defaultBranch: defaultBranchRef {{
                                    name
                                    target {{
                                        ... on Commit {{
                                            mostRecentCommits: history(first: 1, after: null) {{
                                                commits: nodes {{ committedDate }}
                                            }}
                                        }}
                                    }}
                            }}
                            prQuery: pullRequests(first: 1, after: null, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                                prs: nodes {{ updatedAt }}
                            }}
                            # This should be broken out into a separate query if 
                            # hasNextPage is True.
                            branchQuery: refs(refPrefix:"refs/heads/", first: 50) {{
                                {GQL_PAGE_INFO_BLOCK}
                                branches: nodes {{
                                    ... on Ref {{
                                        name
                                        target {{sha: oid}}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repoQuery'
        ):
            for api_repo in page['data']['organization']['repoQuery']['repos']:
                # Skip over excluded or ignore non-included
                if not all(filt(api_repo) for filt in repo_filters):
                    continue
                else:
                    # Potentially process more branches
                    if api_repo['branchQuery']['pageInfo']['hasNextPage']:
                        api_repo['branches'] = [
                            branch
                            for branch in self.get_branches(login=login, repo_name=api_repo['name'])
                        ]
                    else:
                        api_repo['branches'] = api_repo['branchQuery']['branches']
                    yield api_repo

    def get_branches(self, login: str, repo_name: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branchQuery: refs(refPrefix:"refs/heads/", first: 100, after: %s) {{
                            {GQL_PAGE_INFO_BLOCK}
                            branches: nodes {{
                                ... on Ref {{
                                    name
                                    target {{sha: oid}}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repository.branchQuery'
        ):
            for api_branch in page['data']['organization']['repository']['branchQuery']['branches']:
                yield api_branch

    def get_commits_count(
        self, login: str, repo_name: str, branch_name: str, since: datetime
    ) -> int:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branch: ref(qualifiedName: "{branch_name}") {{
                            target {{
                                ... on Commit {{
                                    history(first: 0, since: "{self.datetime_to_gql_str_format(since)}") {{
                                        totalCount
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return self.get_raw_result(query_body)['data']['organization']['repo']['branch']['target'][
            'history'
        ]['totalCount']

    def get_commits(
        self, login: str, repo_name: str, branch_name: str, since: datetime
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branch: ref(qualifiedName: "{branch_name}") {{
                            target {{
                                ... on Commit {{
                                    history(first: 100, since: "{self.datetime_to_gql_str_format(since)}", after: %s) {{
                                        {GQL_PAGE_INFO_BLOCK}
                                        commits: nodes {{
                                            {self.GITHUB_GQL_COMMIT_FRAGMENT}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.branch.target.history'
        ):
            for api_commit in page['data']['organization']['repo']['branch']['target']['history'][
                'commits'
            ]:
                # Overwrite Author block for backwards compatibility
                api_commit['author'] = self._process_git_actor_gql_object(api_commit['author'])
                yield api_commit

    #
    # PR Queries are HUGE, so pull out reusable blocks (comments, reviews, commits, etc)
    #
    def _get_pr_comments_query_block(self, enable_paging: bool = False):
        return f"""
            commentsQuery: comments(first: 100{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}
                
                comments: nodes {{
                    author {{
                        {self.GITHUB_GQL_ACTOR_FRAGMENT}
                    }}
                    body
                    createdAt
                }}
            }}
        """

    # NOTE: There are comments associated with reviews that we need to fetch as well
    def _get_pr_reviews_query_block(self, enable_paging: bool = False):
        return f"""
            reviewsQuery: reviews(first: 25{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}
                
                reviews: nodes {{
                    ... on PullRequestReview {{
                        author {{
                            {self.GITHUB_GQL_ACTOR_FRAGMENT}
                        }}
                        id: databaseId
                        state
                        # NOTE! We are paging for comments here as well!
                        {self._get_pr_comments_query_block()}
                    }}
                }}
            }}
        """

    def _get_pr_commits_query_block(self, enable_paging: bool = False):
        return f"""
            commitsQuery: commits(first: 50{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}
                
                commits: nodes {{
                    ... on PullRequestCommit {{
                        commit {{
                            {self.GITHUB_GQL_COMMIT_FRAGMENT}
                        }}
                    }}
                }}
            }}
        """

    def get_prs_count(self, login: str, repo_name: str) -> int:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    prQuery: pullRequests(first: 1, orderBy: {{direction: DESC, field: UPDATED_AT}}) {{
                        totalCount
                    }}
                }}
            }}
        }}
        """
        return self.get_raw_result(query_body=query_body)['data']['organization']['repo'][
            'prQuery'
        ]['totalCount']

    # PR query is HUGE, see above GITHUB_GQL_PR_* blocks for reused code
    # page_size is optimally variable. Most repos only have a 0 to a few PRs day to day,
    # so sometimes the optimal page_size is 0. Generally, we should never go over 25
    def get_prs(
        self,
        login: str,
        repo_name: str,
        include_top_level_comments: bool = False,
        page_size: int = MAX_PAGE_SIZE_FOR_PR_QUERY,
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    prQuery: pullRequests(first: {page_size}, orderBy: {{direction: DESC, field: UPDATED_AT}}, after: %s) {{
                        {GQL_PAGE_INFO_BLOCK}
                        prs: nodes {{
                            ... on PullRequest {{
                                id: number
                                number
                                additions
                                deletions
                                changedFiles
                                state
                                merged
                                createdAt
                                updatedAt
                                mergedAt
                                closedAt
                                title
                                body
                                url
                                baseRefName
                                headRefName
                                baseRepository {{ {self.GITHUB_GQL_SHORT_REPO_FRAGMENT} }}
                                headRepository {{ {self.GITHUB_GQL_SHORT_REPO_FRAGMENT} }}
                                author {{
                                    {self.GITHUB_GQL_ACTOR_FRAGMENT}
                                }}
                                mergedBy {{
                                    {self.GITHUB_GQL_ACTOR_FRAGMENT}
                                }}
                                mergeCommit {{
                                    {self.GITHUB_GQL_COMMIT_FRAGMENT}
                                }}
                                {self._get_pr_comments_query_block(enable_paging=False) if include_top_level_comments else ''}
                                {self._get_pr_reviews_query_block(enable_paging=False)}
                                {self._get_pr_commits_query_block(enable_paging=False)}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.prQuery'
        ):
            for api_pr in page['data']['organization']['repo']['prQuery']['prs']:
                # Process and add related PR data (comments, reviews, commits)
                # This may require additional API calls
                pr_number = api_pr['number']

                # Load reviews first because we use them in both reviews and comments
                reviews = (
                    [r for r in self.get_pr_reviews(login, repo_name, pr_number=pr_number)]
                    if api_pr['reviewsQuery']['pageInfo']['hasNextPage']
                    else api_pr['reviewsQuery']['reviews']
                )

                # NOTE: COMMENTS ARE WEIRD! They exist in there own API endpoint (these
                # are typically top level comments in a PR, considered an IssueComment)
                # but there are also comments associated with each review (typically only one)
                # The baseline for what we care about is the Review Level comment, pulled from
                # the reviews endpoint. Grabbing Top Level Comments is an optional feature flag

                # Grab the comments pulled from reviews. We ALWAYS want these!
                api_pr['comments'] = [
                    comment for review in reviews for comment in review['commentsQuery']['comments']
                ]

                # Grab the potentially optional top level comments
                if include_top_level_comments:
                    top_level_comments = (
                        [
                            comment
                            for comment in self.get_pr_top_level_comments(
                                login, repo_name, pr_number=pr_number
                            )
                        ]
                        if api_pr['commentsQuery']['pageInfo']['hasNextPage']
                        else api_pr['commentsQuery']['comments']
                    )
                    api_pr['comments'].extend(top_level_comments)

                api_pr['reviews'] = reviews

                api_pr['commits'] = (
                    [
                        commit
                        for commit in self.get_pr_commits(login, repo_name, pr_number=pr_number)
                    ]
                    if api_pr['commitsQuery']['pageInfo']['hasNextPage']
                    else [commit['commit'] for commit in api_pr['commitsQuery']['commits']]
                )

                # Do some extra processing on commits to clean up their weird author block
                for commit in api_pr['commits']:
                    commit['author'] = self._process_git_actor_gql_object(commit['author'])

                if api_pr['mergeCommit'] and api_pr['mergeCommit']['author']:
                    api_pr['mergeCommit']['author'] = self._process_git_actor_gql_object(
                        api_pr['mergeCommit']['author']
                    )

                yield api_pr

    def get_pr_top_level_comments(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_comments_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.commentsQuery'
        ):
            for api_pr_comment in page['data']['organization']['repo']['pr']['commentsQuery'][
                'comments'
            ]:
                yield api_pr_comment

    def get_pr_reviews(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_reviews_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.reviewsQuery'
        ):
            for api_pr_review in page['data']['organization']['repo']['pr']['reviewsQuery'][
                'reviews'
            ]:
                yield api_pr_review

    def get_pr_commits(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_commits_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.commitsQuery'
        ):
            for api_pr_commit in page['data']['organization']['repo']['pr']['commitsQuery'][
                'commits'
            ]:
                # Commit blocks are nested within the 'commits' block
                commit = api_pr_commit['commit']
                commit['author'] = self._process_git_actor_gql_object(commit['author'])
                yield commit

    def get_users_count(self, login: str) -> int:
        query_body = f"""{{
            organization(login: "{login}"){{
                    users: membersWithRole {{
                        totalCount
                    }}
                }}
            }}
        """
        # TODO: Maybe serialize the return results so that we don't have to do this crazy nested grabbing?
        return self.get_raw_result(query_body=query_body)['data']['organization']['users'][
            'totalCount'
        ]

    def get_repos_count(self, login: str) -> int:
        query_body = f"""{{
            organization(login: "{login}"){{
                    repos: repositories {{
                        totalCount
                    }}
                }}
            }}
        """
        # TODO: Maybe serialize the return results so that we don't have to do this crazy nested grabbing?
        return self.get_raw_result(query_body=query_body)['data']['organization']['repos'][
            'totalCount'
        ]

    def get_repo_manifest_data(
        self, login: str, page_size: int = 10
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                    repositories(first: {page_size}, after: %s) {{
                        pageInfo {{
                            endCursor
                            hasNextPage
                            
                        }}
                        repos: nodes {{
                            id: databaseId
                            name
                            url
                            defaultBranch: defaultBranchRef {{
                                name
                                target {{
                                    ... on Commit {{
                                        history {{
                                            totalCount
                                        }}
                                    }}
                                }}
                            }}
                            users: assignableUsers{{
                                totalCount
                            }}
                            prs: pullRequests {{
                                totalCount
                            }}
                            branches: refs(refPrefix:"refs/heads/") {{
                                totalCount
                            }}
                        }}
                    }}
                }}
            }}
        """
        path_to_page_info = 'data.organization.repositories'
        for result in self.page_results_gql(
            query_body=query_body, path_to_page_info=path_to_page_info
        ):
            for repo in result['data']['organization']['repositories']['repos']:
                yield repo

    def get_pr_manifest_data(
        self, login: str, repo_name: str, page_size=100
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
                organization(login: "{login}") {{
                        repository(name: "{repo_name}") {{
                            name
                            id: databaseId
                            prs_query: pullRequests(first: {page_size}, after: %s) {{
                                pageInfo {{
                                    endCursor
                                    hasNextPage
                                }}
                                totalCount
                                prs: nodes {{
                                    updatedAt
                                    id: databaseId
                                    title
                                    number
                                    repository {{id: databaseId, name}}
                                }}
                            }}
                        }}
                    }}
                }}
        """

        path_to_page_info = 'data.organization.repository.prs_query'
        for result in self.page_results_gql(
            query_body=query_body, path_to_page_info=path_to_page_info
        ):
            for pr in result['data']['organization']['repository']['prs_query']['prs']:
                yield pr
