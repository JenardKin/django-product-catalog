from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

# Display a login/logout success message using django messages framework
# and signal receivers


@receiver(user_logged_in)
def announce_login(sender, request, user, **kwargs):
    if request is None or user is None:
        return
    name = user.get_full_name() or user.get_username()
    messages.success(request, f"Login successful as {name}.", fail_silently=True)


@receiver(user_logged_out)
def announce_logout(sender, request, user, **kwargs):
    if request is None or user is None:
        return
    messages.info(request, "Logout successful.", fail_silently=True)
