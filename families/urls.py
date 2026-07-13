from django.urls import path

from . import views


app_name = "families"

urlpatterns = [
    path("users/", views.FamilyUserSearchView.as_view(), name="user-search"),
    path("requests/", views.FamilyRequestCreateView.as_view(), name="request-create"),
    path(
        "requests/received/",
        views.ReceivedFamilyRequestListView.as_view(),
        name="request-received-list",
    ),
    path(
        "requests/sent/",
        views.SentFamilyRequestListView.as_view(),
        name="request-sent-list",
    ),
    path(
        "requests/<int:relation_id>/accept/",
        views.FamilyRequestAcceptView.as_view(),
        name="request-accept",
    ),
    path(
        "requests/<int:relation_id>/reject/",
        views.FamilyRequestRejectView.as_view(),
        name="request-reject",
    ),
    path("", views.FamilyListView.as_view(), name="family-list"),
    path("<int:relation_id>/", views.FamilyRelationDeleteView.as_view(), name="family-delete"),
]
