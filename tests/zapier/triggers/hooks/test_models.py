import pytest


@pytest.mark.django_db
class TestRestHookSubscription:

    def test_unsubscribe(self) -> None:
        raise NotImplementedError

    def test_resubscribe(self) -> None:
        raise NotImplementedError

    def test_push(self) -> None:
        raise NotImplementedError
