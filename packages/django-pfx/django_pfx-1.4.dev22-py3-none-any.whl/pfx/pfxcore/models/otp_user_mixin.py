from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class OtpUserMixin(models.Model):
    otp_secret_token = models.CharField(
        _("OTP secret token"), max_length=32, null=True,
        blank=True, unique=True)
    otp_secret_token_tmp = models.CharField(
        _("Temporary OTP secret token"), max_length=32, null=True, blank=True)

    class Meta:
        abstract = True

    def enable_otp(self):
        import pyotp
        self.otp_secret_token_tmp = pyotp.random_base32()
        self.save(update_fields=['otp_secret_token_tmp'])

    def confirm_otp(self, otp_code):
        if self.is_otp_valid(otp_code, tmp=True):
            self.otp_secret_token = self.otp_secret_token_tmp
            self.otp_secret_token_tmp = None
            self.save(update_fields=[
                'otp_secret_token', 'otp_secret_token_tmp'])
            return True
        return False

    def disable_otp(self):
        self.otp_secret_token = None
        self.save(update_fields=['otp_secret_token'])

    def get_otp_setup_uri(self, tmp=False):
        import pyotp
        return pyotp.totp.TOTP(
            tmp and self.otp_secret_token_tmp or
            self.otp_secret_token).provisioning_uri(
                name=self.email, issuer_name=settings.PFX_SITE_NAME)

    def is_otp_valid(self, otp_code, tmp=False):
        import pyotp
        totp = pyotp.parse_uri(self.get_otp_setup_uri(tmp=tmp))
        return totp.verify(otp_code)

    def get_user_jwt_signature_key(self):
        return super().get_user_jwt_signature_key() + (
            self.otp_secret_token or "")
