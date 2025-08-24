from django_rq import job
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@job("default", timeout=300)
def send_activation_email(user_id, uid, token):
    """
    Send an account activation email to the user.
    """
    try:
        user = User.objects.get(pk=user_id)
        activation_link = (
            f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
        )

        subject = "Activate your account"
        message = f"""Hi {user.email},

        Please activate your account using the link below:
        {activation_link}

        If you did not create an account, please ignore this email.
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Activation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending activation email to user_id={user_id}: {e}")
        raise


@job("default", timeout=300)
def send_password_reset_email(email, reset_url, *args, **kwargs):
    """
    Send a password reset email to the user.
    """
    try:
        subject = "Password Reset Request"
        message = (
            "You requested a password reset for your Videoflix account.\n\n"
            f"Please click the link below to reset your password:\n{reset_url}\n\n"
            "If you did not request this, just ignore this email.\n"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise