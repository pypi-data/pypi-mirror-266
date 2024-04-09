#!/usr/bin/env python

"""Tests for `scim_client` package."""
import json
import unittest
from unittest.mock import patch


from scim_client import scim_client, SCIMResponse, User
from scim_client.resources import UserSearch


class TestSCIMClient(unittest.TestCase):
    def setUp(self):
        self.scim_base_url = "https://localhost:8000/scim/v2"
        self.client = scim_client.SCIMClient(
            base_url=self.scim_base_url, token="random token"
        )
        self.mock_user = User(
            user_name="someusername",
            id="23o4uoqiweu",
            external_id="oi1234qur90w",
            timezone="Asia/Kolkata",
            name={
                "given_name": "Raj",
                "family_name": "Kumar",
                "middle_name": None,
                "name_prefix": None,
                "name_suffix": None,
                "phonetic_representation": None,
                "formatted": "Raj Kumar",
            },
            emails=[{"value": "raj.kumar@localhost.local", "primary": True}],
            active=True,
            display_name="Raj Kumar",
            meta={
                "resource_type": "User",
                "created": "2024-01-19T00:03:02.634696",
                "last_modified": "2024-01-19T00:03:02.634696",
                "location": "%s/Users/23o4uoqiweu" % self.scim_base_url,
            },
        )

    def get_resource_url(self, resource: str):
        return "%s/%s" % (self.scim_base_url, resource)

    def test_read_user(self) -> None:
        user_id = "3423yer89qw6d9"
        scim_response = SCIMResponse(
            url=self.get_resource_url("Users/%s" % user_id),
            status_code=200,
            headers={},
            raw_body=json.dumps(self.mock_user.to_dict()),
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            user = self.client.read_user(user_id=user_id)
            self.client._make_request.assert_called_once_with(
                method="GET", resource="Users/%s" % user_id
            )

            assert user.to_dict() == self.mock_user.to_dict()

    def test_search_users(self) -> None:
        search_q = "search string"
        mock_sreach_result = UserSearch(
            resources=[self.mock_user.to_snake_cased_dict()],
            total_results=1,
            items_per_page=10,
            start_index=0,
        )
        scim_response = SCIMResponse(
            url=self.get_resource_url("Users"),
            status_code=200,
            headers={},
            raw_body=json.dumps(mock_sreach_result.to_dict()),
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            user_search = self.client.search_users(search_q)
            self.client._make_request.assert_called_once_with(
                method="GET",
                resource="Users",
                query_params={"filter": "search string", "count": 20, "startIndex": 0},
            )

            assert user_search.to_dict() == mock_sreach_result.to_dict()

    def test_create_user(self) -> None:
        scim_response = SCIMResponse(
            url=self.get_resource_url("Users"),
            status_code=200,
            headers={},
            raw_body=json.dumps(self.mock_user.to_dict()),
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            user = self.client.create_user(user=self.mock_user)
            self.client._make_request.assert_called_once_with(
                method="POST", resource="Users", data=self.mock_user.to_dict()
            )

            assert user.to_dict() == self.mock_user.to_dict()

    def test_delete_user(self) -> None:
        # when user_id is provided
        user_id = "3423yer89qw6d9"
        scim_response = SCIMResponse(
            url=self.get_resource_url("Users/%s" % user_id),
            status_code=200,
            headers={},
            raw_body="",
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            resp = self.client.delete_user(user_id=user_id)
            self.client._make_request.assert_called_once_with(
                method="DELETE", resource="Users/%s" % user_id
            )

            assert resp == scim_response

        # when user object is provided
        scim_response = SCIMResponse(
            url=self.get_resource_url("Users/%s" % self.mock_user.id),
            status_code=200,
            headers={},
            raw_body="",
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            resp = self.client.delete_user(user=self.mock_user)
            self.client._make_request.assert_called_once_with(
                method="DELETE", resource="Users/%s" % self.mock_user.id
            )

        # without any argument, delete_user should raise assertion error
        assert resp == scim_response
        self.assertRaises(AssertionError, self.client.delete_user)

    def test_user_schema_extension(self):
        mock_enterprise_user = User(
            user_name="someusername",
            id="23o4uoqiweu",
            external_id="oi1234qur90w",
            name={
                "given_name": "Raj",
                "family_name": "Kumar",
                "middle_name": None,
                "name_prefix": None,
                "name_suffix": None,
                "phonetic_representation": None,
                "formatted": "Raj Kumar",
            },
            emails=[{"value": "raj.kumar@localhost.local", "primary": True}],
            active=True,
            display_name="Raj Kumar",
            meta={
                "resource_type": "User",
                "created": "2024-01-19T00:03:02.634696",
                "last_modified": "2024-01-19T00:03:02.634696",
                "location": "%s/Users/23o4uoqiweu" % self.scim_base_url,
            },
            enterprise_user={
                "employee_number": "234",
                "department": "Engineering",
            },
            schemas=[
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
            ],
        )

        scim_response = SCIMResponse(
            url=self.get_resource_url("Users"),
            status_code=200,
            headers={},
            raw_body=json.dumps(mock_enterprise_user.to_dict()),
        )
        with patch.object(self.client, "_make_request", return_value=scim_response):
            user = self.client.create_user(user=mock_enterprise_user)
            self.client._make_request.assert_called_once_with(
                method="POST", resource="Users", data=mock_enterprise_user.to_dict()
            )

            assert user.to_dict() == mock_enterprise_user.to_dict()
