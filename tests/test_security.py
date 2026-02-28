from common.security import WebAppSigner


def test_signer() -> None:
    signer = WebAppSigner()
    token = signer.issue(42)
    assert signer.parse(token) == 42
    assert signer.parse("bad") is None
