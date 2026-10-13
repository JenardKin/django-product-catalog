from django.contrib.auth import views as auth_views
from django.urls import path

# Login/Logout views for the site.

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="catalog/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
