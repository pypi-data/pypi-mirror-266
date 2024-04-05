import fnmatch
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
from itertools import chain
from typing import Any, Dict, Generator, Iterable, List, Optional

from tqdm import tqdm

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import GitConfig, GitProviderInJellyfishRepo, IngestionConfig
from jf_ingest.constants import Constants
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.jf_git.exceptions import GitProviderUnavailable
from jf_ingest.utils import batch_iterable, batch_iterable_by_bytes_size

logger = logging.getLogger(__name__)

'''

    Constants

'''
# NOTE: ONLY GITHUB IS CURRENTLY SUPPORTED!!!!
BBS_PROVIDER = 'bitbucket_server'
BBC_PROVIDER = 'bitbucket_cloud'
GH_PROVIDER = 'github'
GL_PROVIDER = 'gitlab'
PROVIDERS = [GL_PROVIDER, GH_PROVIDER, BBS_PROVIDER, BBC_PROVIDER]

'''

    Standardized Structure

'''


def _transform_dataclass_list_to_dict(dataclass_objects: List[Any]) -> List[Dict]:
    """Helper function for taking a list of objects that inherit from Dataclass and
    transforming them to a list of dictionary objects

    Args:
        dataclass_objects (List[DataclassInstance]): A list of Dataclass Instances

    Returns:
        List[Dict]: A list of dictionaries
    """
    return [asdict(dc_object) for dc_object in dataclass_objects]


@dataclass
class StandardizedUser:
    id: str
    name: str
    login: str
    email: str = None
    url: str = None
    account_id: str = None


@dataclass
class StandardizedTeam:
    id: str
    slug: str
    name: str
    description: str
    members: list[StandardizedUser]


@dataclass
class StandardizedBranch:
    name: str
    sha: str


@dataclass
class StandardizedOrganization:
    id: str
    name: str
    login: str
    url: str


@dataclass
class StandardizedShortRepository:
    id: int
    name: str
    url: str


@dataclass
class StandardizedRepository:
    id: int
    name: str
    full_name: str
    url: str
    is_fork: bool
    default_branch_name: str
    organization: StandardizedOrganization
    branches: List[StandardizedBranch]

    def short(self):
        # return the short form of Standardized Repository
        return StandardizedShortRepository(id=self.id, name=self.name, url=self.url)


@dataclass
class StandardizedCommit:
    hash: str
    url: str
    message: str
    commit_date: str
    author_date: str
    author: StandardizedUser
    repo: StandardizedShortRepository
    is_merge: bool
    branch_name: str = None


@dataclass
class StandardizedPullRequestComment:
    user: StandardizedUser
    body: str
    created_at: str
    system_generated: bool = None


@dataclass
class StandardizedPullRequestReview:
    user: StandardizedUser
    foreign_id: int
    review_state: str


@dataclass
class StandardizedPullRequest:
    id: any
    additions: int
    deletions: int
    changed_files: int
    is_closed: bool
    is_merged: bool
    created_at: str
    updated_at: str
    merge_date: str
    closed_date: str
    title: str
    body: str
    url: str
    base_branch: str
    head_branch: str
    author: StandardizedUser
    merged_by: StandardizedUser
    commits: List[StandardizedCommit]
    merge_commit: StandardizedCommit
    comments: List[StandardizedPullRequestComment]
    approvals: List[StandardizedPullRequestReview]
    base_repo: StandardizedShortRepository
    head_repo: StandardizedShortRepository


class GitObject(Enum):
    GitOrganizations = "git_organization"
    GitUsers = "git_users"
    GitTeams = "git_teams"
    GitRepositories = "git_repositories"
    GitBranches = "git_branches"
    GitCommits = "git_commits"
    GitPullRequests = "git_pull_requests"


class GitAdapter(ABC):
    config: GitConfig
    PULL_REQUEST_BATCH_SIZE_IN_BYTES = (
        50 * Constants.MB_SIZE_IN_BYTES
    )  # PRs can be huge and of variable size. We need to limit them by batch size in bytes
    NUMBER_OF_COMMITS_PER_BATCH = (
        30000  # Commits are generally uniform in size. This is ~50 MBs per commit batch
    )

    @staticmethod
    def get_git_adapter(config: GitConfig):
        """Static function for generating a GitAdapter from a provided GitConfig object

        Args:
            config (GitConfig): A git configuration data object. The specific GitAdapter
                is returned based on the git_provider field in this object

        Raises:
            GitProviderUnavailable: If the supplied git config has an unknown git provider, this error will be thrown

        Returns:
            GitAdapter: A specific subclass of the GitAdapter, based on what git_provider we need
        """
        from jf_ingest.jf_git.adapters.github import GithubAdapter

        if config.git_provider == GitProviderInJellyfishRepo.GITHUB:
            adapter = GithubAdapter(config)
        else:
            raise GitProviderUnavailable(
                f'Git provider {config.git_provider} is not currently supported'
            )

        adapter.config = config
        return adapter

    @abstractmethod
    def get_api_scopes(self) -> str:
        """Return the list of API Scopes. This is useful for Validation

        Returns:
            str: A string of API scopes we have, given the adapters credentials
        """
        pass

    @abstractmethod
    def get_organizations(self) -> List[StandardizedOrganization]:
        """Get the list of organizations the adapter has access to

        Returns:
            List[StandardizedOrganization]: A list of standardized organizations within this Git Instance
        """
        pass

    @abstractmethod
    def get_users(
        self, standardized_org: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedUser, None, None]:
        """Get the list of users in a given Git Organization

        Args:
            standardized_org (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized User Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_teams(
        self, standardized_org: StandardizedOrganization, limit: int = None
    ) -> Generator[StandardizedTeam, None, None]:
        """Get the list of teams in a given Git Organization

        Args:
            standardized_org (StandardizedOrganization): A standardized Git Organization Object

        Returns:
            List[StandardizedUser]: A standardized Team Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_repos(
        self, standardized_org: StandardizedOrganization
    ) -> Generator[StandardizedRepository, None, None]:
        """Get a list of standardized repositories within a given organization

        Args:
            standardized_org (StandardizedOrganization): A standardized organization

        Returns:
            List[StandardizedRepository]: A list of standardized Repositories
        """
        pass

    @abstractmethod
    def get_commits_for_included_branches(
        self,
        standardized_repo: StandardizedRepository,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the included branches.
        Included branches are found by crawling across the branches pulled/available
        from get_branches_for_standardized_repo

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        pass

    @abstractmethod
    def get_commits_for_default_branch(
        self, standardized_repo: StandardizedRepository, limit: int = None
    ) -> Generator[StandardizedCommit, None, None]:
        """Get a list of commits for the default branch

        Args:
            standardized_repo (StandardizedRepository): A standardized repository object

        Returns:
            List[StandardizedCommit]: A list of standardized commits
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
        """
        pass

    @abstractmethod
    def get_prs(
        self, standardized_repo: StandardizedRepository, limit: int = None
    ) -> Generator[StandardizedPullRequest, None, None]:
        """Get the list of standardized Pull Requests for a Standardized Repository.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        pass

    def get_branches_for_standardized_repo(self, repo: StandardizedRepository) -> set[str]:
        """Return branches for which we should pull commits, specified by customer in git config.
            The repo's default branch will always be included in the returned list.

        Args:
            repo (StandardizedRepository): A standardized repository

        Returns:
            set[str]: A set of branch names (as strings)
        """

        # Helper function
        def get_matching_branches(
            included_branch_patterns: List[str], repo_branch_names: List[str]
        ) -> List[str]:
            # Given a list of patterns, either literal branch names or names with wildcards (*) meant to match a set of branches in a repo,
            # return the list of branches from repo_branches that match any of the branch name patterns.
            # fnmatch is used over regex to support wildcards but avoid complicating the requirements on branch naming in a user's config.
            matching_branches = []
            for repo_branch_name in repo_branch_names:
                if any(
                    fnmatch.fnmatch(repo_branch_name, pattern)
                    for pattern in included_branch_patterns
                ):
                    matching_branches.append(repo_branch_name)
            return matching_branches

        branches_to_process = [repo.default_branch_name] if repo.default_branch_name else []
        additional_branches_for_repo = self.config.included_branches_by_repo.get(repo.name)
        if additional_branches_for_repo:
            repo_branch_names = [b.name for b in repo.branches if b]
            branches_to_process.extend(
                get_matching_branches(additional_branches_for_repo, repo_branch_names)
            )
        return set(branches_to_process)

    def load_and_dump_git(self, ingest_config: IngestionConfig):
        """This is a shared class function that can get called by
        the different types of GitAdapters that extend this class.
        This function handles fetching all the necessary data from
        Git, transforming it, and saving it to local disk and/or S3

        Args:
            ingest_config (IngestionConfig): A valid Ingestion Config
        """
        #######################################################################
        # Init IO Helper
        #######################################################################
        ingest_io_helper = IngestIOHelper(ingest_config=ingest_config)

        # Wrapper function for writing to the IngestIOHelper
        def _write_to_s3_or_local(object_name: str, json_data: list[dict], batch_number: int = 0):
            ingest_io_helper.write_json_to_local_or_s3(
                object_name=object_name,
                json_data=json_data,
                subdirectory=SubDirectory.GIT,
                save_locally=ingest_config.save_locally,
                upload_to_s3=ingest_config.upload_to_s3,
                git_instance_key=self.config.instance_file_key,
                batch_number=batch_number,
            )

        #######################################################################
        # ORGANIZATION DATA
        #######################################################################
        logger.info('Fetching Git Organization Data...')
        standardized_organizations: List[StandardizedOrganization] = self.get_organizations()
        logger.info(
            f'Successfully pulled Git Organizations data for {len(standardized_organizations)} Organizations.'
        )
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitOrganizations.value,
            json_data=_transform_dataclass_list_to_dict(standardized_organizations),
        )

        #######################################################################
        # USER DATA
        #######################################################################
        logger.info('Fetching Git User Data...')
        standardized_users: List[StandardizedUser] = [
            user
            for org in standardized_organizations
            for user in tqdm(self.get_users(org), desc='Processing Users', unit=' users')
        ]
        logger.info(f'Successfully found {len(standardized_users)} users.')
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitUsers.value,
            json_data=_transform_dataclass_list_to_dict(standardized_users),
        )

        #######################################################################
        # TEAM DATA
        #######################################################################
        logger.info('Fetching Git Team Data...')
        standardized_teams: List[StandardizedTeam] = [
            team
            for org in standardized_organizations
            for team in tqdm(self.get_teams(org), desc="Processing Teams", unit=" teams")
        ]
        logger.info(f'Successfully found {len(standardized_teams)} teams.')
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitTeams.value,
            json_data=_transform_dataclass_list_to_dict(standardized_teams),
        )

        #######################################################################
        # REPO DATA
        #######################################################################
        logger.info('Fetching Git Repo Data...')
        standardized_repos: List[StandardizedRepository] = [
            repo
            for org in standardized_organizations
            for repo in tqdm(
                self.get_repos(org), unit=' repos', desc=f'Pulling all available Repositories'
            )
        ]
        repo_count = len(standardized_repos)
        logger.info(f'Successfully pulled Git Repo Data for {repo_count} Repos.')
        # Upload Data
        _write_to_s3_or_local(
            object_name=GitObject.GitRepositories.value,
            json_data=_transform_dataclass_list_to_dict(standardized_repos),
        )

        #######################################################################
        # COMMIT DATA
        #
        # NOTE: Commit data can be quite large, so for better memory handling
        # we will create a chain of generators (get_commits_for_included_branches returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        # NOTE: Commit data is pretty uniform in size (each commit is ~2KB), so we'll upload
        # in batches of 30k commits (roughly 50 MB in data)
        #
        #######################################################################
        total_commits = 0
        logger.info(f'Fetching Git Commit Data for {repo_count} Repos...')
        list_of_commit_generators: List[Generator[StandardizedCommit, None, None]] = []
        for repo in standardized_repos:
            commit_generator_for_repo = self.get_commits_for_included_branches(repo)
            transformed_commit_generator = map(lambda commit: commit, commit_generator_for_repo)
            list_of_commit_generators.append(transformed_commit_generator)

        # Chain together all the generators
        commits_generator = tqdm(
            chain.from_iterable(list_of_commit_generators),
            desc=f'Processing Commits for {repo_count} repos',
            unit=' commits',
        )
        for batch_num, commit_batch in enumerate(
            batch_iterable(commits_generator, batch_size=self.NUMBER_OF_COMMITS_PER_BATCH)
        ):
            total_commits += len(commit_batch)
            commit_batch_as_dict = _transform_dataclass_list_to_dict(commit_batch)
            _write_to_s3_or_local(
                object_name=GitObject.GitCommits.value,
                json_data=commit_batch_as_dict,
                batch_number=batch_num,
            )
        logger.info(f'Successfully process {total_commits} total commits')

        #######################################################################
        # PULL REQUEST DATA
        #
        # NOTE: Pull Request data can be quite large, so for better memory handling
        # we will create a chain of generators (get_prs returns a generator)
        # and process our way through those generators, uploading data ~50 MBs at a time
        #
        #######################################################################
        total_prs = 0
        logger.info(f'Fetching Git Pull Request Data for {repo_count} Repos...')
        list_of_pr_generators: List[Generator[StandardizedPullRequest, None, None]] = []
        for repo in standardized_repos:
            pr_generator_for_repo = self.get_prs(repo)
            transformed_pr_generator = map(lambda pr: asdict(pr), pr_generator_for_repo)
            list_of_pr_generators.append(transformed_pr_generator)

        # Chain together all the generators
        prs_generator = tqdm(
            chain.from_iterable(list_of_pr_generators),
            desc=f'Processing Pull Request Data for {repo_count} repos',
            unit=' PRs',
        )
        for batch_num, pr_batch in enumerate(
            batch_iterable_by_bytes_size(
                prs_generator, batch_byte_size=self.PULL_REQUEST_BATCH_SIZE_IN_BYTES
            )
        ):
            total_prs += len(pr_batch)
            _write_to_s3_or_local(
                object_name=GitObject.GitPullRequests.value,
                json_data=pr_batch,
                batch_number=batch_num,
            )
        logger.info(f'Successfully processed {total_prs} total PRs')

        logger.info(f'Done processing Git Data!')


@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def load_and_push_git_to_s3(ingest_config: IngestionConfig):
    """Handler function for the end to end processing of Git Data.
    This function is responsible for taking in an ingest config,
    creating a git adapter, and then running the Git Adapter function
    for uploading data to S3 (or saving it locally). The function for
    handling that logic is part of the GitAdapter class (see load_and_dump_git)

    Args:
        ingest_config (IngestionConfig): A fully formed IngestionConfig class, with
        valid Git Configuration in it.
    """
    for git_config in ingest_config.git_configs:
        try:
            git_adapter: GitAdapter = GitAdapter.get_git_adapter(git_config)
            git_adapter.load_and_dump_git(ingest_config=ingest_config)
        except GitProviderUnavailable:
            logger.warning(
                f'Git Config for provider {git_config.git_provider} is currently NOT supported!'
            )
            continue
