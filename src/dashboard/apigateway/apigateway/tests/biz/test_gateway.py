#
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - API 网关(BlueKing - APIGateway) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.
#
from unittest import mock

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django_dynamic_fixture import G

from apigateway.apps.monitor.models import AlarmStrategy
from apigateway.apps.support.models import ReleasedResourceDoc
from apigateway.biz.gateway import GatewayHandler
from apigateway.common.contexts.context import GatewayFeatureFlagContext
from apigateway.core.constants import (
    ContextScopeTypeEnum,
    ContextTypeEnum,
    GatewayStatusEnum,
    GatewayTypeEnum,
    StageStatusEnum,
)
from apigateway.core.models import JWT, APIRelatedApp, Context, Gateway, Release, Resource, Stage


class TestGatewayHandler:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self):
        self.gateway = G(Gateway, created_by="admin")

    def test_get_stages_with_release_status(self, fake_gateway):
        Gateway.objects.filter(id=fake_gateway.id).update(status=GatewayStatusEnum.ACTIVE.value)
        stage_1 = G(Stage, api=fake_gateway, status=StageStatusEnum.ACTIVE.value)
        stage_2 = G(Stage, api=fake_gateway, status=StageStatusEnum.ACTIVE.value)

        G(Release, gateway=fake_gateway, stage=stage_1)
        expected = {
            fake_gateway.id: [
                {
                    "id": stage_1.id,
                    "name": stage_1.name,
                    "released": True,
                },
                {
                    "id": stage_2.id,
                    "name": stage_2.name,
                    "released": False,
                },
            ]
        }

        result = GatewayHandler().get_stages_with_release_status([fake_gateway.id])
        assert result == expected

    @pytest.mark.parametrize(
        "user_conf, api_type, allow_update_api_auth, unfiltered_sensitive_keys, expected",
        [
            # update user_conf
            (
                {
                    "from_username": False,
                },
                None,
                None,
                None,
                {
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.CLOUDS_API.value,
                    "allow_update_api_auth": True,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_username": False,
                    },
                    "unfiltered_sensitive_keys": [],
                },
            ),
            # update api_type
            (
                None,
                GatewayTypeEnum.OFFICIAL_API,
                None,
                None,
                {
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.OFFICIAL_API.value,
                    "allow_update_api_auth": True,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_username": True,
                    },
                    "unfiltered_sensitive_keys": [],
                },
            ),
            # update allow_update_api_auth
            (
                None,
                None,
                False,
                None,
                {
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.CLOUDS_API.value,
                    "allow_update_api_auth": False,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_username": True,
                    },
                    "unfiltered_sensitive_keys": [],
                },
            ),
            (
                {
                    "from_username": False,
                    "not_exist_field": True,
                },
                GatewayTypeEnum.OFFICIAL_API,
                False,
                None,
                {
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.OFFICIAL_API.value,
                    "allow_update_api_auth": False,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_username": False,
                    },
                    "unfiltered_sensitive_keys": [],
                },
            ),
            # update unfiltered_sensitive_keys
            (
                None,
                None,
                None,
                ["bk_token", "bk_app_secret"],
                {
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.CLOUDS_API.value,
                    "allow_update_api_auth": True,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_username": True,
                    },
                    "unfiltered_sensitive_keys": ["bk_token", "bk_app_secret"],
                },
            ),
        ],
    )
    def test_save_auth_config(
        self, mocker, fake_gateway, user_conf, api_type, allow_update_api_auth, unfiltered_sensitive_keys, expected
    ):
        mocker.patch(
            "apigateway.biz.gateway.GatewayHandler.get_current_gateway_auth_config",
            return_value={
                "user_auth_type": "default",
                "api_type": GatewayTypeEnum.CLOUDS_API.value,
                "unfiltered_sensitive_keys": [],
                "allow_update_api_auth": True,
                "user_conf": {
                    "user_type": "default",
                    "from_bk_token": True,
                    "from_username": True,
                },
            },
        )

        result, _ = GatewayHandler().save_auth_config(
            fake_gateway.id,
            user_auth_type="default",
            user_conf=user_conf,
            api_type=api_type,
            allow_update_api_auth=allow_update_api_auth,
            unfiltered_sensitive_keys=unfiltered_sensitive_keys,
        )
        assert result.scope_type == ContextScopeTypeEnum.GATEWAY.value
        assert result.type == ContextTypeEnum.GATEWAY_AUTH.value
        assert result.scope_id == fake_gateway.id
        assert result.config == expected

    def test_save_related_data(self, mocker, fake_gateway):
        mocker.patch(
            "apigateway.biz.gateway.APIAuthConfig.config",
            new_callable=mock.PropertyMock(
                return_value={
                    "user_auth_type": "default",
                    "api_type": GatewayTypeEnum.CLOUDS_API.value,
                    "unfiltered_sensitive_keys": [],
                    "allow_update_api_auth": True,
                    "user_conf": {
                        "user_type": "default",
                        "from_bk_token": True,
                        "from_bk_username": False,
                    },
                }
            ),
        )
        GatewayHandler().save_related_data(fake_gateway, "default", "admin", "test")

        assert Context.objects.filter(
            scope_type=ContextScopeTypeEnum.GATEWAY.value,
            type=ContextTypeEnum.GATEWAY_AUTH.value,
            scope_id=fake_gateway.id,
        ).exists()

        assert JWT.objects.filter(api=fake_gateway).exists()
        assert Stage.objects.filter(api=fake_gateway).exists()
        assert AlarmStrategy.objects.filter(api=fake_gateway).exists()
        assert APIRelatedApp.objects.filter(api=fake_gateway, bk_app_code="test").exists()

    def test_delete_gateway(
        self,
        fake_gateway,
        fake_stage,
        fake_resource,
        fake_resource_version,
        fake_release,
        rate_limit_access_strategy,
        rate_limit_access_strategy_stage_binding,
        rate_limit_access_strategy_resource_binding,
        echo_plugin,
        echo_plugin_stage_binding,
        echo_plugin_resource_binding,
        fake_ssl_certificate,
    ):
        GatewayHandler.delete_gateway(gateway_id=fake_gateway.pk)

        for model in [
            fake_stage,
            fake_resource,
            fake_resource_version,
            fake_release,
            rate_limit_access_strategy,
            rate_limit_access_strategy_stage_binding,
            rate_limit_access_strategy_resource_binding,
            echo_plugin,
            echo_plugin_stage_binding,
            echo_plugin_resource_binding,
            fake_ssl_certificate,
        ]:
            with pytest.raises(ObjectDoesNotExist):
                model.refresh_from_db()

    def test_get_feature_flag(self, settings, fake_gateway):
        settings.GLOBAL_GATEWAY_FEATURE_FLAG = {"FOO": False, "BAR": True}
        GatewayFeatureFlagContext().save(fake_gateway.id, {"FOO": True})

        feature_flag = GatewayHandler.get_feature_flag(fake_gateway.id)
        assert feature_flag == {"FOO": True, "BAR": True}

    def test_get_docs_url(self, settings, fake_gateway):
        settings.API_DOCS_URL_TMPL = "http://apigw.example.com/docs/{api_name}"
        result = GatewayHandler.get_docs_url(fake_gateway)
        assert result == ""

        G(ReleasedResourceDoc, gateway=fake_gateway)
        result = GatewayHandler.get_docs_url(fake_gateway)
        assert result == f"http://apigw.example.com/docs/{fake_gateway.name}"

    def test_get_resource_count(self):
        gateway_1 = G(Gateway)
        gateway_2 = G(Gateway)
        gateway_3 = G(Gateway)

        G(Resource, api=gateway_1)
        G(Resource, api=gateway_1)
        G(Resource, api=gateway_2)

        data = [
            {
                "gateway_ids": [gateway_1.id, gateway_2.id, gateway_3.id],
                "expected": {
                    gateway_1.id: 2,
                    gateway_2.id: 1,
                },
            },
            {
                "gateway_ids": [gateway_1.id, gateway_2.id],
                "expected": {
                    gateway_1.id: 2,
                    gateway_2.id: 1,
                },
            },
        ]

        for test in data:
            result = GatewayHandler.get_resource_count(test["gateway_ids"])
            assert result == test["expected"]

    @pytest.mark.parametrize(
        "gateway_name, expected",
        [
            ("app1", 30),
            ("app2", 50),
            ("app3", 20),
        ],
    )
    def test_get_max_resource_count(self, settings, gateway_name, expected):
        settings.API_GATEWAY_RESOURCE_LIMITS = {
            "max_resource_count_per_gateway": 20,
            "max_resource_count_per_gateway_whitelist": {
                "app1": 30,
                "app2": 50,
            },
        }

        result = GatewayHandler.get_max_resource_count(gateway_name)
        assert result == expected
