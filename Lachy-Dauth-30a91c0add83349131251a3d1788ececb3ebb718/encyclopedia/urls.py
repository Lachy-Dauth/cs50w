from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.new, name="new"),
    path("edit", views.edit, name="edit"),
    path("random", views.random_entry, name="random"),
    path("<str:name>", views.entry, name="new")
]
