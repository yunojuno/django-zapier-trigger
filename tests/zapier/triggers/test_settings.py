from typing import Any

import pytest

from tests.conftest import uf
from tests.factories import UserFactory
from zapier.triggers.settings import import_from_path, trigger_exists


@pytest.mark.parametrize(
    "path,target",
    [("tests.factories.UserFactory", UserFactory), ("tests.conftest.uf", uf)],
)
def test_import_from_path(path: str, target: Any) -> None:
    assert import_from_path(path) == target


def test_trigger_exists() -> None:
    assert trigger_exists("new_book")
    assert not trigger_exists("old_book")
