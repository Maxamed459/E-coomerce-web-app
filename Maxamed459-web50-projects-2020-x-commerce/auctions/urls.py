from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name="create"),
    path("displayCategory", views.displayCategory, name="displayCategory"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("removeWachlist/<int:id>", views.removeWachlist, name="removeWachlist"),
    path("addWachlist/<int:id>", views.addWachlist, name="addWachlist"),
    path("displayWachlist", views.displayWachlist, name="displayWachlist"),
    path("addComment/<int:id>", views.addComment, name="addComment"),
    path("addBid/<int:id>", views.addBid, name="addBid"),
    path("closeAuction/<int:id>", views.closeAuction, name="closeAuction"),
]
