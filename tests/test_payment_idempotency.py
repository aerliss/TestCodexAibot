import inspect

from bot.app.services import repository


def test_complete_payment_имеет_защиту_идемпотентности() -> None:
    source = inspect.getsource(repository.complete_payment)
    assert 'payment.status == "paid"' in source
