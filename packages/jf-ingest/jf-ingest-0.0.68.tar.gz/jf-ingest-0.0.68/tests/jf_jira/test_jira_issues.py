import json
import logging
import math
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import pytz
import requests_mock
from jira import JIRAError

from jf_ingest.constants import Constants
from jf_ingest.jf_jira.downloaders import (
    IssueMetadata,
    _download_issue_page,
    _expand_changelog,
    _filter_changelogs,
    _get_all_project_issue_counts,
    _get_issue_count_for_jql,
    detect_issues_needing_re_download,
    download_all_issue_metadata,
    download_issues,
    generate_jql_for_batch_of_ids,
    generate_project_pull_from_jql,
    get_fields_spec,
    get_ids_from_difference_of_issue_metadata,
    get_jira_search_batch_size,
    get_out_of_date_issue_ids,
    pull_all_jira_issues_by_date,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.utils import batch_iterable
from tests.jf_jira.utils import (
    _register_jira_uri,
    _register_jira_uri_with_file,
    get_fixture_file_data,
    get_jira_mock_connection,
)

logger = logging.getLogger(__name__)


def _generate_mock_address_for_issue_jql(
    m: requests_mock.Mocker,
    jql_query: str,
    issue_count: int,
    start_at: int,
    max_results: int,
    issues: list[dict],
):
    _issues = [issue for issue in issues[start_at : min(start_at + max_results, len(issues))]]
    jira_return_val = f'{{"expand":"names,schema","startAt":{start_at},"maxResults":{max_results},"total":{issue_count},"issues":{json.dumps(_issues)}}}'

    endpoint = (
        f"search?jql={jql_query}&startAt={start_at}&validateQuery=True&maxResults={max_results}"
    )
    _register_jira_uri(
        m,
        endpoint=endpoint,
        return_value=jira_return_val,
    )


def _mock_jira_issue_by_date_endpoints(
    m: requests_mock.Mocker,
    project_keys_to_issue_counts: dict[str, int],
    pull_from: datetime,
    batch_size: int,
    issues_updated_value: datetime = pytz.utc.localize(datetime.min),
    expand_fields: list[str] = ["*all"],
):
    def generate_issues(project_key, count):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
                "id": f"{i}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"{project_key}-{i}",
                "fields": _fields,
            }
            for i in range(count)
        ]

    for project_key, count in project_keys_to_issue_counts.items():
        issues = generate_issues(project_key=project_key, count=count)
        jql_query = generate_project_pull_from_jql(
            project_key=project_key, earliest_issue_dt=pull_from
        )
        # Generate one call for getting hte 'first' page (for issue counts)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=count,
            start_at=0,
            issues=issues,
            max_results=1,
        )
        for start_at in range(0, count, batch_size):
            _generate_mock_address_for_issue_jql(
                m=m,
                jql_query=jql_query,
                issue_count=count,
                start_at=start_at,
                max_results=batch_size,
                issues=issues,
            )


def test_get_issue_count_for_jql():
    earliest_issue_dt = datetime.min
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 5123
    project_key_to_count = {PROJECT_KEY: PROJECT_ISSUE_COUNT}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_key_to_count,
            pull_from=earliest_issue_dt,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=generate_project_pull_from_jql(
                project_key=PROJECT_KEY, earliest_issue_dt=earliest_issue_dt
            ),
        )
        assert count_for_jql == project_key_to_count[PROJECT_KEY]


def test_get_issue_count_for_jql_400_level_error_handling():
    """Assert that when we raise 400 level errors, we always return 0"""
    for status_code in range(400, 500):
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_429s",
            side_effect=JIRAError(status_code=status_code),
        ):
            logger.info(
                f"Attempting to test _get_issue_count_for_jql when a {status_code} error is thrown"
            )
            count_for_jql = _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")
            assert count_for_jql == 0


def test_get_issue_count_for_jql_500_level_error_handling():
    for status_code in range(500, 600):
        logger.info(f"Checking to see if we raise 500 level errors...")
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_429s",
            side_effect=JIRAError(status_code=status_code),
        ):
            with pytest.raises(JIRAError):
                _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")


def test_get_all_project_issue_counts():
    earliest_issue_dt = datetime.min
    project_keys_to_counts = {"PROJ": 151, "COLLAGE": 512}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_keys_to_counts,
            pull_from=earliest_issue_dt,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )

        project_issue_counts = _get_all_project_issue_counts(
            get_jira_mock_connection(mocker),
            project_keys=project_keys_to_counts.keys(),
            earliest_issue_dt=earliest_issue_dt,
            num_parallel_threads=1,
        )

        assert project_issue_counts == project_keys_to_counts


def _mock_jira_issue_by_ids(
    m: requests_mock.Mocker(),
    issue_ids: list[str],
    batch_size: int,
    issues_updated_value: datetime = datetime.min,
    expand_fields: list[str] = ["*all"],
):
    def _generate_issues(ids_batch):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.isoformat()
            _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.isoformat()
            if "parent" in expand_fields:
                _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}

        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
                "id": f"{id}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"PROJ-{i}",
                "fields": _fields,
            }
            for i, id in enumerate(ids_batch)
        ]

    for id_batch in batch_iterable(sorted(issue_ids, key=int), batch_size=batch_size):
        jql_query = generate_jql_for_batch_of_ids(id_batch)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=len(id_batch),
            start_at=0,
            issues=_generate_issues(id_batch),
            max_results=batch_size,
        )


def test_get_jira_batch_size():
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search?jql=&startAt=0&validateQuery=True&maxResults={requested_batch_size}",
                return_value=jira_return_val,
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            jira_issues_batch_size = get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )

            assert jira_issues_batch_size == jira_batch_size_return


def test_get_fields_spec():
    assert get_fields_spec(include_fields=[], exclude_fields=[]) == ["*all"]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=[]) == ["updated"]
    assert get_fields_spec(include_fields=["updated", "parent"], exclude_fields=[]) == [
        "updated",
        "parent",
    ]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=["parent"]) == [
        "updated",
        "-parent",
    ]


def get_issues_through_test_fixture():
    issue_ids = sorted(["18447", "18404", "18031", "18018", "18016"], key=int)
    jql_query = generate_jql_for_batch_of_ids(issue_ids)
    with requests_mock.Mocker() as m:
        # Register one endpoint that this will hit
        uri = f"search?jql={jql_query}&startAt=0&validateQuery=True&fields=%2Aall&expand=renderedFields%2Cchangelog&maxResults=5"
        _register_jira_uri_with_file(m, endpoint=uri, fixture_path="api_responses/issues.json")

        return [
            i
            for i in pull_jira_issues_by_jira_ids(
                jira_connection=get_jira_mock_connection(),
                jira_ids=issue_ids,
                num_parallel_threads=10,
                batch_size=len(issue_ids),
                expand_fields=["renderedFields", "changelog"],
                include_fields=[],
                exclude_fields=[],
            )
        ]


def test_filter_changelogs_no_filtering():
    issues = get_issues_through_test_fixture()
    issues_without_filtering = _filter_changelogs(issues, [], [])

    custom_fields = ["customfield_10051", "customfield_10057", "customfield_10009"]
    for issue in issues_without_filtering:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) != 0
            for item in history["items"]:
                if "fieldId" in item:
                    assert item["fieldId"] in custom_fields


def test_filter_changelogs_inclusion_filtering_for_madeup_field():
    issues = get_issues_through_test_fixture()
    issues_with_filtering_field_in = _filter_changelogs(issues, ["madeup_field"], [])
    for issue in issues_with_filtering_field_in:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) == 0


def test_expand_changelog():
    total_changelog_histories = 5
    batch_size = 1

    def _mock_api_endpoint_for_changelog(m: requests_mock.Mocker, change_log_num: int):
        mock_return = {
            "self": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=1",
            "nextPage": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=2",
            "maxResults": batch_size,
            "startAt": change_log_num - 1,
            "total": total_changelog_histories,
            "isLast": False,
            "values": [
                {
                    "id": f"{change_log_num}",
                    "author": {},
                    "created": "2020-06-29T16:01:51.141-0400",
                    "items": [
                        {
                            "field": "Spelunking CustomField v2",
                            "fieldtype": "custom",
                            "fieldId": "customfield_10057",
                            "from": None,
                            "fromString": None,
                            "to": "10072",
                            "toString": "hello",
                        }
                    ],
                }
            ],
        }
        _register_jira_uri(
            m,
            endpoint=f"issue/1/changelog?startAt={change_log_num - 1}&maxResults={batch_size}",
            return_value=json.dumps(mock_return),
        )

    with requests_mock.Mocker() as m:
        for change_log_num in range(0, total_changelog_histories + 1):
            _mock_api_endpoint_for_changelog(m, change_log_num)
        spoofed_issue_raw: dict = {
            "id": "1",
            "key": "spoof-1",
            "changelog": {
                "total": total_changelog_histories,
                "maxResults": 0,
                "histories": [],
            },
        }

        spoofed_issue_no_more_results_raw: dict = {
            "id": "2",
            "key": "spoof-2",
            "changelog": {"total": 0, "maxResults": 0, "histories": []},
        }

        _expand_changelog(
            get_jira_mock_connection(),
            jira_issues=[spoofed_issue_raw, spoofed_issue_no_more_results_raw],
            batch_size=1,
        )

        assert len(spoofed_issue_raw["changelog"]["histories"]) == total_changelog_histories
        assert len(spoofed_issue_no_more_results_raw["changelog"]["histories"]) == 0


def test_get_out_of_date_issue_ids() -> set[str]:
    updated_base_line = datetime(2020, 1, 1, tzinfo=timezone.utc)
    issue_metadata = [
        IssueMetadata(id=str(_id), key=f"PROJ-{_id}", project_id="1", updated=updated_base_line)
        for _id in range(0, Constants.MAX_ISSUE_API_BATCH_SIZE)
    ]
    out_of_date_ids = get_out_of_date_issue_ids(
        issue_metadata_from_jira=issue_metadata,
        issue_metadata_from_jellyfish=issue_metadata,
        full_redownload=False,
    )
    print("Asserting that we get no out of date IDs for a matching set of issue metadata")
    assert len(out_of_date_ids) == 0

    # Update Jira Meta Data to mark all of the data as updated
    jira_issue_metadata = [
        IssueMetadata(
            id=(_im.id),
            key=_im.key,
            project_id=_im.project_id,
            updated=updated_base_line + timedelta(days=1),
        )
        for _im in issue_metadata
    ]

    out_of_date_ids = get_out_of_date_issue_ids(
        issue_metadata_from_jira=jira_issue_metadata,
        issue_metadata_from_jellyfish=issue_metadata,
        full_redownload=False,
    )
    print("Asserting that we should pull all Jira Data")
    assert len(issue_metadata) == len(out_of_date_ids)

    # Test what happens when we have a mismatch of metadata
    jira_issue_metadata = jira_issue_metadata[0 : len(jira_issue_metadata) // 2]
    out_of_date_ids = get_out_of_date_issue_ids(
        issue_metadata_from_jira=jira_issue_metadata,
        issue_metadata_from_jellyfish=issue_metadata,
        full_redownload=False,
    )
    print("Asserting that we don't break when we are short on Jira Issue Metadata")
    assert len(out_of_date_ids) == len(jira_issue_metadata)


def test_get_ids_from_difference_of_issue_metadata():
    updated_base_line = datetime(2020, 1, 1, tzinfo=timezone.utc)
    total_issues = Constants.MAX_ISSUE_API_BATCH_SIZE
    issue_metadata = [
        IssueMetadata(id=str(_id), key=f"PROJ-{_id}", project_id="1", updated=updated_base_line)
        for _id in range(total_issues)
    ]
    id_difference = get_ids_from_difference_of_issue_metadata(issue_metadata, issue_metadata)

    print("Asserting there is no difference between two identical sets")
    assert len(id_difference) == 0

    id_difference = get_ids_from_difference_of_issue_metadata(
        issue_metadata, issue_metadata[0 : total_issues // 2]
    )
    print("Asserting that we are missing half of the data")
    assert len(id_difference) == total_issues // 2

    id_difference = get_ids_from_difference_of_issue_metadata(issue_metadata, [])
    print("Asserting that subtracting nothing gives you the full source set")
    assert len(id_difference) == total_issues

    id_difference = get_ids_from_difference_of_issue_metadata([], issue_metadata)
    print("Asserting that subtracting nothing from nothing gives you nothing")
    assert len(id_difference) == 0

    # Test what happens when no IDs match
    issue_metadata_offset = [
        IssueMetadata(id=str(_id), key=f"PROJ-{_id}", project_id="1", updated=updated_base_line)
        for _id in range(total_issues, total_issues * 2)
    ]

    id_difference = get_ids_from_difference_of_issue_metadata(issue_metadata, issue_metadata_offset)
    print("Asserting that we are really checking by IDs")
    assert len(id_difference) == total_issues

    id_difference = get_ids_from_difference_of_issue_metadata(issue_metadata_offset, issue_metadata)
    print("Asserting that we are really checking by IDs (with inverse of original test)")
    assert len(id_difference) == total_issues


def test_detect_issues_needing_re_download_rekey_case():
    OLD_PROJECT_KEY = "PROJ-3"
    NEW_PROJECT_KEY = "NEWPROJ-3"

    AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_ITS_EPIC_FIELD_LINK = "4"
    AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_PARENT_FIELD_LINK = "5"

    jira_issue_metadata = [
        IssueMetadata(id="1", key="PROJ-1", updated=datetime.min),
        IssueMetadata(id="2", key="PROJ-2", updated=datetime.min),
        # Mark one issue as 'rekeyed', which will flag a redownload
        IssueMetadata(id="3", key=NEW_PROJECT_KEY, updated=datetime.min),
        IssueMetadata(id="4", key="PROJ-4", updated=datetime.min),
        IssueMetadata(id="5", key="PROJ-5", updated=datetime.min),
    ]

    jellyfish_issue_metadata = [
        IssueMetadata(id="1", key="PROJ-1", updated=datetime.min),
        IssueMetadata(id="2", key="PROJ-2", updated=datetime.min),
        # This ISSUE HAS BEEN REKEYED!!!!
        IssueMetadata(
            id="3",
            key=OLD_PROJECT_KEY,
            updated=datetime.min,
            epic_link_field_issue_key="PROJ-4",
            parent_field_issue_key="PROJ-5",
        ),
        # THESE ISSUES HAVE A DEPENDENCY ON THE REKEYED ISSUE, AND WILL NEED TO BE REDOWNLOADED
        IssueMetadata(
            id=AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_ITS_EPIC_FIELD_LINK,
            key="PROJ-4",
            updated=datetime.min,
            epic_link_field_issue_key=OLD_PROJECT_KEY,
            parent_field_issue_key="PROJ-1",
        ),
        IssueMetadata(
            id=AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_PARENT_FIELD_LINK,
            key="PROJ-5",
            updated=datetime.min,
            epic_link_field_issue_key="PROJ-1",
            parent_field_issue_key=OLD_PROJECT_KEY,
        ),
    ]

    ids_to_redownload = detect_issues_needing_re_download(
        jira_issue_metadata, jellyfish_issue_metadata
    )
    assert len(ids_to_redownload) == len(
        [
            AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_ITS_EPIC_FIELD_LINK,
            AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_PARENT_FIELD_LINK,
        ]
    )
    assert AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_ITS_EPIC_FIELD_LINK in ids_to_redownload
    assert AN_ISSUE_ID_THAT_HAS_A_REKEY_AS_PARENT_FIELD_LINK in ids_to_redownload


@contextmanager
def _mock_for_full_issue_test(
    jf_issue_metadata: list[IssueMetadata],
    project_key: str = "PROJ",
    earliest_issue_dt: datetime = datetime.min,
    issues_updated_value: datetime = datetime(2020, 1, 1),
    batch_size: int = Constants.MAX_ISSUE_API_BATCH_SIZE,
):
    expand_fields = ["*all"]

    with requests_mock.Mocker() as mocker:
        # Register the 'Batch Size' query return
        _register_jira_uri(
            mocker,
            endpoint=f"search?jql=&startAt=0&validateQuery=True&fields=%2Aall&maxResults={Constants.MAX_ISSUE_API_BATCH_SIZE}",
            return_value=f'{{"expand":"schema,names","startAt":0,"maxResults":{batch_size},"total":{len(jf_issue_metadata)},"issues":[]}}',
        )

        # Register the 'pull from' dates
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts={project_key: len(jf_issue_metadata)},
            pull_from=earliest_issue_dt,
            issues_updated_value=issues_updated_value,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )

        _mock_jira_issue_by_ids(
            m=mocker,
            issue_ids=[
                issue_metadata.id
                for issue_metadata in jf_issue_metadata
                if issues_updated_value > issue_metadata.updated
            ],
            batch_size=batch_size,
            issues_updated_value=issues_updated_value,
            expand_fields=expand_fields,
        )
        yield mocker


def _download_issues_and_metadata_wrapper(
    mocker, earliest_issue_dt: datetime, jf_issue_metadata: list[IssueMetadata]
):
    jira_conn = get_jira_mock_connection(mocker)
    issue_metadata_from_jira: list[IssueMetadata] = download_all_issue_metadata(
        jira_connection=jira_conn,
        project_keys=["PROJ"],
        earliest_issue_dt=earliest_issue_dt,
        num_parallel_threads=5,
        batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
    )

    jira_issues = [
        i
        for i in download_issues(
            jira_connection=jira_conn,
            full_redownload=False,
            jira_issues_batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
            issue_download_concurrent_threads=5,
            issue_metadata_from_jellyfish=jf_issue_metadata,
            issue_metadata_from_jira=issue_metadata_from_jira,
            include_fields=[],
            exclude_fields=[],
        )
    ]
    return jira_issues, issue_metadata_from_jira


def test_download_issues_no_updates():
    # Test when ALL issues have been updated since the earliest_issue_dt
    batch_size = Constants.MAX_ISSUE_API_BATCH_SIZE
    earliest_issue_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    issue_ids = [str(i) for i in range((batch_size * 2) + 19)]

    jf_issue_metadata_datetime = earliest_issue_dt
    jf_issue_metadata = [
        IssueMetadata(
            issue_id,
            key=f"PROJ-{issue_id}",
            updated=jf_issue_metadata_datetime,
            project_id="PROJ",
        )
        for issue_id in issue_ids
    ]

    with _mock_for_full_issue_test(
        jf_issue_metadata,
        earliest_issue_dt=earliest_issue_dt,
        # Mark all datetimes as being updated ONE DAY BEFORE the datetime we set for JF Issue Metadata,
        # which will force us to pull NO ISSUES
        issues_updated_value=jf_issue_metadata_datetime + timedelta(days=-1),
        batch_size=batch_size,
    ) as mocker:
        jira_issues, issue_metadata_from_jira = _download_issues_and_metadata_wrapper(
            mocker, earliest_issue_dt=earliest_issue_dt, jf_issue_metadata=jf_issue_metadata
        )

        # Assert we pull NONE !
        assert 0 == len(jira_issues)


def test_download_issues_all_missing_data():
    # Test when ALL issues have been updated since the earliest_issue_dt
    batch_size = Constants.MAX_ISSUE_API_BATCH_SIZE
    earliest_issue_dt = pytz.utc.localize(datetime.min)
    issue_ids = [str(i) for i in range((batch_size * 2) + 19)]

    jf_issue_metadata_datetime = earliest_issue_dt
    jf_issue_metadata = [
        IssueMetadata(
            issue_id,
            key=f"PROJ-{issue_id}",
            updated=jf_issue_metadata_datetime,
            project_id="PROJ",
        )
        for issue_id in issue_ids
    ]

    issue_metadata_from_jira = []
    with _mock_for_full_issue_test(
        # Spoof that the Jira instance has no data
        issue_metadata_from_jira,
        earliest_issue_dt=earliest_issue_dt,
        # Mark all datetimes as being updated ONE DAY passed the datetime we set for JF Issue Metadata,
        # which will force us to pull all issues
        issues_updated_value=jf_issue_metadata_datetime + timedelta(days=1),
        batch_size=batch_size,
    ) as mocker:
        jira_issues, issue_metadata_from_jira = _download_issues_and_metadata_wrapper(
            mocker, earliest_issue_dt=earliest_issue_dt, jf_issue_metadata=jf_issue_metadata
        )
        # Assert that we pull all issue data, because we intentionally
        # spoofed the 'missing' data case by reducing the size of jellyfish_issue_metadata
        assert len(jira_issues) == 0
        deleted_issue_ids = set([jfim.id for jfim in jf_issue_metadata]) - set(
            [i['id'] for i in jira_issues]
        )
        assert len(issue_ids) == len(deleted_issue_ids)
        for issue_id in deleted_issue_ids:
            assert type(issue_id) == str


def test_download_issue_page_ensure_error_never_raised():
    """
    The _download_issue_page should NEVER raise an error.
    """
    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_429s",
        side_effect=JIRAError(status_code=500),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0

    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_429s",
        side_effect=Exception('random exception'),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0
