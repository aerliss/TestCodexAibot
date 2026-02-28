from common.security import WebAppSigner


def test_sign_and_verify_roundtrip():
    signer = WebAppSigner()
    token = signer.sign_tg_id(12345)
    assert signer.verify(token) == 12345


def test_verify_invalid_token():
    signer = WebAppSigner()
    assert signer.verify("invalid") is None
