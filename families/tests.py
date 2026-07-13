from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import FamilyRelation


User = get_user_model()


class FamilyAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="minseo",
            email="minseo@example.com",
            password="StrongPass123!",
            name="김민서",
        )
        self.target = User.objects.create_user(
            username="parent",
            email="parent@example.com",
            password="StrongPass123!",
            name="보호자",
        )
        self.other = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
            name="타인",
        )

    def login(self, user=None):
        self.client.force_login(user or self.user)

    def create_relation(self, requester=None, target=None, relation_status=None):
        requester = requester or self.user
        target = target or self.target
        user1, user2 = sorted([requester, target], key=lambda user: user.pk)
        return FamilyRelation.objects.create(
            user1=user1,
            user2=user2,
            requester=requester,
            status=relation_status or FamilyRelation.Status.PENDING,
        )

    def test_family_users_requires_login(self):
        response = self.client.get(reverse("families:user-search"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_search_users_by_username_excludes_self(self):
        self.login()

        response = self.client.get(
            reverse("families:user-search"),
            {"username": "parent"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["username"], "parent")
        self.assertNotIn("password", response.data["data"][0])

    def test_search_users_without_username_returns_empty_list(self):
        self.login()

        response = self.client.get(reverse("families:user-search"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], [])

    def test_create_family_request(self):
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.target.pk},
            format="json",
        )
        relation = FamilyRelation.objects.get()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(relation.user1_id, min(self.user.pk, self.target.pk))
        self.assertEqual(relation.user2_id, max(self.user.pk, self.target.pk))
        self.assertEqual(relation.requester, self.user)
        self.assertEqual(relation.status, FamilyRelation.Status.PENDING)

    def test_create_family_request_rejects_self(self):
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.user.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(FamilyRelation.objects.count(), 0)

    def test_create_family_request_rejects_duplicate_pending(self):
        self.create_relation()
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.target.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FamilyRelation.objects.count(), 1)

    def test_create_family_request_rejects_reverse_duplicate_pending(self):
        self.create_relation(requester=self.target, target=self.user)
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.target.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FamilyRelation.objects.count(), 1)

    def test_create_family_request_rejects_duplicate_accepted(self):
        self.create_relation(relation_status=FamilyRelation.Status.ACCEPTED)
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.target.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FamilyRelation.objects.count(), 1)

    def test_create_family_request_reuses_rejected_relation(self):
        relation = self.create_relation(
            requester=self.target,
            target=self.user,
            relation_status=FamilyRelation.Status.REJECTED,
        )
        self.login()

        response = self.client.post(
            reverse("families:request-create"),
            {"target_user_id": self.target.pk},
            format="json",
        )
        relation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FamilyRelation.objects.count(), 1)
        self.assertEqual(relation.status, FamilyRelation.Status.PENDING)
        self.assertEqual(relation.requester, self.user)

    def test_received_requests(self):
        self.create_relation(requester=self.target, target=self.user)
        self.create_relation(requester=self.user, target=self.other)
        self.login()

        response = self.client.get(reverse("families:request-received-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["requester"]["username"], "parent")

    def test_sent_requests(self):
        self.create_relation(requester=self.user, target=self.target)
        self.create_relation(requester=self.other, target=self.user)
        self.login()

        response = self.client.get(reverse("families:request-sent-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["user"]["username"], "parent")

    def test_requester_cannot_accept_own_request(self):
        relation = self.create_relation(requester=self.user, target=self.target)
        self.login()

        response = self.client.patch(
            reverse("families:request-accept", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        relation.refresh_from_db()
        self.assertEqual(relation.status, FamilyRelation.Status.PENDING)

    def test_non_participant_cannot_accept_request(self):
        relation = self.create_relation(requester=self.user, target=self.target)
        self.login(self.other)

        response = self.client.patch(
            reverse("families:request-accept", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_family_request(self):
        relation = self.create_relation(requester=self.user, target=self.target)
        self.login(self.target)

        response = self.client.patch(
            reverse("families:request-accept", kwargs={"relation_id": relation.pk}),
        )
        relation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(relation.status, FamilyRelation.Status.ACCEPTED)

    def test_reject_family_request(self):
        relation = self.create_relation(requester=self.user, target=self.target)
        self.login(self.target)

        response = self.client.patch(
            reverse("families:request-reject", kwargs={"relation_id": relation.pk}),
        )
        relation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(relation.status, FamilyRelation.Status.REJECTED)

    def test_cannot_decide_non_pending_request(self):
        relation = self.create_relation(relation_status=FamilyRelation.Status.ACCEPTED)
        self.login(self.target)

        response = self.client.patch(
            reverse("families:request-reject", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_family_list_only_returns_accepted_relations(self):
        accepted = self.create_relation(relation_status=FamilyRelation.Status.ACCEPTED)
        self.create_relation(requester=self.user, target=self.other)
        self.login()

        response = self.client.get(reverse("families:family-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], accepted.pk)

    def test_delete_family_relation(self):
        relation = self.create_relation(relation_status=FamilyRelation.Status.ACCEPTED)
        self.login()

        response = self.client.delete(
            reverse("families:family-delete", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(FamilyRelation.objects.filter(pk=relation.pk).exists())

    def test_non_participant_cannot_delete_family_relation(self):
        relation = self.create_relation(relation_status=FamilyRelation.Status.ACCEPTED)
        self.login(self.other)

        response = self.client.delete(
            reverse("families:family-delete", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(FamilyRelation.objects.filter(pk=relation.pk).exists())

    def test_cannot_delete_pending_relation(self):
        relation = self.create_relation()
        self.login()

        response = self.client.delete(
            reverse("families:family-delete", kwargs={"relation_id": relation.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(FamilyRelation.objects.filter(pk=relation.pk).exists())

    def test_all_family_apis_require_login(self):
        relation = self.create_relation()
        urls_and_methods = [
            ("get", reverse("families:user-search")),
            ("post", reverse("families:request-create")),
            ("get", reverse("families:request-received-list")),
            ("get", reverse("families:request-sent-list")),
            (
                "patch",
                reverse("families:request-accept", kwargs={"relation_id": relation.pk}),
            ),
            (
                "patch",
                reverse("families:request-reject", kwargs={"relation_id": relation.pk}),
            ),
            ("get", reverse("families:family-list")),
            (
                "delete",
                reverse("families:family-delete", kwargs={"relation_id": relation.pk}),
            ),
        ]

        for method, url in urls_and_methods:
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, format="json")

                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertFalse(response.data["success"])
