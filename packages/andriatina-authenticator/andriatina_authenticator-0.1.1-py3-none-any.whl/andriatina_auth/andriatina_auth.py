import pyotp
def get_auth(secret, issuer):
    totp = pyotp.TOTP(secret, issuer=issuer)
    otp_code = totp.now()
    return otp_code