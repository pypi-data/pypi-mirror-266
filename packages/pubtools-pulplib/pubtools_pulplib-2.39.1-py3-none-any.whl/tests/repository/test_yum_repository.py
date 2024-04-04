import pytest
import logging
import requests

from pubtools.pulplib import Repository, YumRepository, DetachedException, YumImporter


def test_from_data_gives_yum_repository():
    """Repository.from_data maps to YumRepository subclass when needed"""
    repo = Repository.from_data({"id": "my-repo", "notes": {"_repo-type": "rpm-repo"}})
    assert isinstance(repo, YumRepository)


def test_default_mutable_urls():
    """mutable_urls has expected default value"""
    assert YumRepository(id="foo").mutable_urls == ["repodata/repomd.xml"]


def test_can_hash():
    """a default YumRepository is hashable"""
    repo = YumRepository(id="foo")
    reposet = set()
    reposet.add(repo)
    assert repo in reposet


def test_from_data_relative_url():
    """relative_url is initialized from distributors when possible"""
    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {"_repo-type": "rpm-repo"},
            "distributors": [
                {
                    "id": "yum_distributor",
                    "distributor_type_id": "yum_distributor",
                    "config": {"relative_url": "some/publish/path"},
                }
            ],
        }
    )

    assert repo.relative_url == "some/publish/path"


def test_from_data_skip_rsync_repodata():
    """skip_rsync_repodata is initialized from distributors when possible"""
    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {"_repo-type": "rpm-repo"},
            "distributors": [
                {
                    "id": "cdn_distributor",
                    "distributor_type_id": "rpm_rsync_distributor",
                    "config": {"skip_repodata": True},
                }
            ],
        }
    )
    assert repo.skip_rsync_repodata


def test_from_data_importer():
    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {"_repo-type": "rpm-repo"},
            "importers": [
                {
                    "importer_type_id": "yum_importer",
                    "config": {"foo": "bar"},
                }
            ],
        }
    )

    assert repo.importer.type_id == "yum_importer"
    assert repo.importer.config == {"foo": "bar"}


def test_populate_attrs():
    """test populate attributes are correctly parsed from repo notes"""
    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {
                "_repo-type": "rpm-repo",
                "content_set": "fake_content_set",
                "include_in_download_service": "True",
                "include_in_download_service_preview": "True",
                "population_sources": ["populate_repo1", "populate_repo2"],
                "provisioning": True,
                "ubi_config_version": "fake_ubi_config_version",
                "ubi_population": True,
            },
            "distributors": [],
        }
    )
    assert repo.content_set == "fake_content_set"
    assert repo.include_in_download_service
    assert repo.include_in_download_service_preview
    assert repo.population_sources == ["populate_repo1", "populate_repo2"]
    assert repo.provisioning
    assert repo.ubi_config_version == "fake_ubi_config_version"
    assert repo.ubi_population


def test_productid_attrs():
    """All attributes relating to productid are correctly parsed from repo notes."""

    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {
                "_repo-type": "rpm-repo",
                "arch": "x86_64",
                "product_versions": '["1.4", "1.100", "1.2"]',
                "platform_full_version": "whatever",
                "eng_product": "123",
            },
            "distributors": [],
        }
    )

    assert repo.arch == "x86_64"
    assert repo.eng_product_id == 123
    assert repo.platform_full_version == "whatever"

    # Note the version-aware sorting: 1.100 is larger than 1.4
    assert repo.product_versions == ["1.2", "1.4", "1.100"]


def test_product_versions_unusual_attrs():
    """Odd values in product_versions are tolerated."""

    repo = Repository.from_data(
        {
            "id": "my-repo",
            "notes": {
                "_repo-type": "rpm-repo",
                "product_versions": '["1.4", 234, "1.100", "not numeric"]',
            },
            "distributors": [],
        }
    )

    assert repo.product_versions == ["1.100", "1.4", "234", "not numeric"]


def test_related_repositories(client, requests_mocker):
    """test Repository.get_*_repository returns expected objects"""

    repo_binary_test = YumRepository(id="repo_binary", relative_url="some/repo/os")
    repo_binary_test.__dict__["_client"] = client

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/distributors/search/",
        [
            {
                "json": [
                    {
                        "id": "yum_distributor",
                        "distributor_type_id": "yum_distributor",
                        "repo_id": "repo_debug",
                        "config": {"relative_url": "some/repo/debug"},
                    }
                ]
            },
            {
                "json": [
                    {
                        "id": "yum_distributor",
                        "distributor_type_id": "yum_distributor",
                        "repo_id": "repo_source",
                        "config": {"relative_url": "some/repo/SRPMS"},
                    }
                ]
            },
        ],
    )

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/search/",
        [{"json": [{"id": "repo_debug"}]}, {"json": [{"id": "repo_source"}]}],
    )

    # Request for binary repo should return identical object
    assert repo_binary_test is repo_binary_test.get_binary_repository().result()
    assert repo_binary_test.get_binary_repository().id == "repo_binary"
    # Requests for debug and source repositories return correct repositories
    assert repo_binary_test.get_debug_repository().id == "repo_debug"
    assert repo_binary_test.get_source_repository().id == "repo_source"


def test_related_repositories_not_found(client, requests_mocker):
    """test Repository.get_*_repository returns Future[None] if repository is not found"""

    repo_binary_test = YumRepository(id="repo_binary", relative_url="some/repo/os")
    repo_binary_test.__dict__["_client"] = client

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/distributors/search/", json=[]
    )

    repo = repo_binary_test.get_source_repository()
    assert repo.result() is None


def test_related_repositories_detached_client():
    repo_binary_test = YumRepository(id="repo_binary", relative_url="some/repo/os")
    repo_binary_test.__dict__["_client"] = None

    with pytest.raises(DetachedException):
        repo_binary_test.get_binary_repository()


def test_create_repository(client, requests_mocker):
    repo = YumRepository(id="yum_repo_new")

    # create request
    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/",
        json={},
    )

    # repo search request
    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/search/",
        json=[
            {
                "id": "yum_repo_new",
                "notes": {"_repo-type": "rpm-repo"},
                "importers": [
                    {
                        "importer_type_id": "yum_importer",
                        "config": {},
                    }
                ],
            }
        ],
    )

    out = client.create_repository(repo)
    # check return value of create_repository() call
    assert out.result() == repo

    hist = requests_mocker.request_history
    # there should be exactly 2 requests sent - create and search
    assert len(hist) == 2

    create_query = hist[0].json()
    # check id of repository sent in request body
    assert create_query["id"] == "yum_repo_new"
    # check importer data sent in request body that
    # are automatically added for yum repository
    assert create_query["importer_type_id"] == "yum_importer"
    assert create_query["importer_config"] == {}

    # check the search request for created repo
    search_query = hist[1].json()
    assert search_query == {
        "criteria": {
            "skip": 0,
            "limit": 2000,
            "filters": {"id": {"$eq": "yum_repo_new"}},
        },
        "distributors": True,
        "importers": True,
    }


def test_create_repository_already_exists(client, requests_mocker, caplog):
    repo = YumRepository(id="yum_repo_existing")

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/",
        status_code=409,
        text="Conflict 409 status",
    )

    # repo search request
    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/search/",
        json=[
            {
                "id": "yum_repo_existing",
                "notes": {"_repo-type": "rpm-repo"},
                "importers": [
                    {
                        "importer_type_id": "yum_importer",
                        "config": {},
                    }
                ],
            }
        ],
    )

    with caplog.at_level(logging.WARNING):
        out = client.create_repository(repo)
        # check return value of create_repository() call
        assert out.result() == repo

        hist = requests_mocker.request_history
        # there should be 2 request sent - attempt to create and search for repo,
        # 409 status is never retried
        assert len(hist) == 2

        query = hist[0].json()
        # check id of repository sent in request body
        assert query["id"] == "yum_repo_existing"
        # check importer data sent in request body that
        # are automatically added for yum repository
        assert query["importer_type_id"] == "yum_importer"
        assert query["importer_config"] == {}
        # check logged information about existing repository
        assert "Repository yum_repo_existing already exists" in caplog.text

        # check the search request for existing repo
        search_query = hist[1].json()
        assert search_query == {
            "criteria": {
                "skip": 0,
                "limit": 2000,
                "filters": {"id": {"$eq": "yum_repo_existing"}},
            },
            "distributors": True,
            "importers": True,
        }


def test_create_repository_wrong_data(client, requests_mocker, caplog):
    repo = YumRepository(
        id="yum_repo_existing", importer=YumImporter(config={"new": "value"})
    )

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/",
        status_code=409,
        text="Conflict 409 status",
    )

    # repo search request
    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/search/",
        json=[
            {
                "id": "yum_repo_existing",
                "notes": {"_repo-type": "rpm-repo"},
                "importers": [
                    {
                        "importer_type_id": "yum_importer",
                        "config": {"current": "value"},
                    }
                ],
            }
        ],
    )
    with caplog.at_level(logging.WARNING):
        with pytest.raises(AssertionError):
            client.create_repository(repo).result()

        for text in (
            "Repository yum_repo_existing already exists",
            "Repository yum_repo_existing contains wrong importer config",
            "Repository yum_repo_existing exists on server and contains unexpected values",
        ):
            assert text in caplog.text


def test_create_repository_raises_exception(client, requests_mocker):
    repo = YumRepository(id="yum_repo")

    requests_mocker.post(
        "https://pulp.example.com/pulp/api/v2/repositories/",
        status_code=400,
        text="Client error 400",
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.create_repository(repo).result()
