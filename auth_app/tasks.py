from django_rq import job
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

import logging

User = get_user_model()
logger = logging.getLogger(__name__)

logo_url = f"{settings.FRONTEND_URL}/assets/icons/logo_icon.svg"


@job("default", timeout=300)
def send_activation_email(user_id, uid, token, *args, **kwargs):
    """
    Send an account activation email to the user with HTML template.
    """
    try:
        user = User.objects.get(pk=user_id)
        activation_link = (
            f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
        )

        subject = "Confirm your email"
        from_email = f"Videoflix <{settings.DEFAULT_FROM_EMAIL}>"
        to = [user.email]

        text_content = f"""
        Hi {user.email},

        Please activate your account using the link below:
        {activation_link}

        If you did not create an account, please ignore this email.
        """

        html_content = f"""
          <div style="font-family:Arial,sans-serif;line-height:1.5;color:#333;">
          <div style="text-align:center;margin-bottom:20px;">
              <img src="{logo_url}" alt="Videoflix Logo" style="height:48px;" />
          </div>
          
          <h2 style="color:#222;">Confirm your email</h2>
          <p>Dear {user.first_name or 'User'},</p>
          <p>Thank you for registering with <b>Videoflix</b>. 
          To complete your registration and verify your email address, please click the link below:</p>
          
          <a href="{activation_link}" 
             style="display:inline-block;padding:12px 24px;margin:16px 0;
                    background-color:#2563eb;color:white;text-decoration:none;
                    border-radius:8px;font-weight:bold;">
             Activate account
          </a>

          <p>If you did not create an account with us, please disregard this email.</p>
          <p>Best regards,<br>Your Videoflix Team</p>
        </div>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Activation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending activation email to user_id={user_id}: {e}")
        raise



@job("default", timeout=300)
def send_password_reset_email(email, reset_url, *args, **kwargs):
    """
    Send a password reset email to the user with HTML template.
    """
    try:
        subject = "Reset your Password"
        from_email = f"Videoflix <{settings.DEFAULT_FROM_EMAIL}>"
        to = [email]

        text_content = f"""
        You requested a password reset for your Videoflix account.

        Please click the link below to reset your password:
        {reset_url}

        If you did not request this, just ignore this email.
        """

        html_content = f"""
          <div style="font-family:Arial,sans-serif;line-height:1.5;color:#333;">
          <div style="text-align:center;margin-bottom:20px;">
              <img src="{logo_url}" alt="Videoflix Logo" style="height:48px;" />
          </div>
          
          <h2 style="color:#222;">Reset your Password</h2>
          <p>Hello,</p>
          <p>We recently received a request to reset your password. 
          If you made this request, please click on the following link to reset your password:</p>

          <a href="{reset_url}" 
             style="display:inline-block;padding:12px 24px;margin:16px 0;
                    background-color:#2563eb;color:white;text-decoration:none;
                    border-radius:8px;font-weight:bold;">
             Reset password
          </a>

          <p><small>Please note that for security reasons, this link is only valid for 24 hours.</small></p>
          <p>If you did not request a password reset, please ignore this email.</p>
          <p>Best regards,<br>Your Videoflix Team</p>
        </div>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise
