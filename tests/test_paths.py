from porygon.paths import files_to_purge, normalize_path, user_id_from_path

UID = "3f2b8c1e-aaaa-bbbb-cccc-1234567890ab"


def test_user_id_extracted() -> None:
    assert user_id_from_path(f"/Volumes/c/bronze/landing/{UID}/march.xlsx") == UID


def test_dbfs_scheme_ignored() -> None:
    assert user_id_from_path(f"dbfs:/Volumes/c/bronze/landing/{UID}/a.csv") == UID


def test_no_user_prefix_returns_none() -> None:
    assert user_id_from_path("/Volumes/c/bronze/landing/stray.csv") is None
    assert user_id_from_path("/Volumes/c/bronze/landing/short/a.csv") is None


def test_normalize_path() -> None:
    assert normalize_path("dbfs:/x") == "/x"
    assert normalize_path("/x") == "/x"


def test_purge_only_committed_files() -> None:
    landed = ["/v/landing/u1/a.csv", "/v/landing/u1/b.csv"]
    committed = {"dbfs:/v/landing/u1/a.csv"}
    assert files_to_purge(landed, committed) == ["/v/landing/u1/a.csv"]


def test_purge_nothing_when_nothing_committed() -> None:
    assert files_to_purge(["/v/landing/u1/a.csv"], set()) == []
