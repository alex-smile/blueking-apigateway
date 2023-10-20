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
import pytest
from pydantic import parse_obj_as

from apigateway.biz.gateway import GatewayHandler
from apigateway.biz.gateway.synchronizer import GatewaySyncData, GatewaySynchronizer
from apigateway.common.contexts import GatewayAuthContext
from apigateway.core.constants import GatewayTypeEnum
from apigateway.core.models import Gateway, GatewayRelatedApp


class TestGatewaySyncData:
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                {
                    "name": "foo",
                    "status": 1,
                },
                {
                    "name": "foo",
                    "description": "",
                    "description_en": None,
                    "maintainers": [],
                    "status": 1,
                    "is_public": False,
                    "gateway_type": None,
                    "user_config": None,
                },
            ),
            (
                {
                    "name": "foo",
                    "description": "desc",
                    "description_en": "desc en",
                    "maintainers": ["admin"],
                    "status": 0,
                    "is_public": True,
                    "gateway_type": 1,
                    "user_config": {"foo": "bar"},
                    "not_exist_key": "",
                },
                {
                    "name": "foo",
                    "description": "desc",
                    "description_en": "desc en",
                    "maintainers": ["admin"],
                    "status": 0,
                    "is_public": True,
                    "gateway_type": GatewayTypeEnum.OFFICIAL_API,
                    "user_config": {"foo": "bar"},
                },
            ),
        ],
    )
    def test(self, data, expected):
        gateway_data = parse_obj_as(GatewaySyncData, data)
        assert gateway_data.dict() == expected


class TestGatewaySynchronizer:
    def test_sync(self, unique_gateway_name):
        # create
        synchronizer = GatewaySynchronizer(None, GatewaySyncData(name=unique_gateway_name, status=0))
        gateway = synchronizer.sync()

        assert gateway.id == Gateway.objects.get(name=unique_gateway_name).id
        assert gateway.status == 0

        # update
        synchronizer = GatewaySynchronizer(gateway, GatewaySyncData(name=unique_gateway_name, status=1))
        gateway = synchronizer.sync()

        assert gateway.id == Gateway.objects.get(name=unique_gateway_name).id
        assert gateway.status == 0

    def test_create(self, settings, unique_gateway_name):
        settings.DEFAULT_USER_AUTH_TYPE = "default"
        settings.SPECIAL_GATEWAY_AUTH_CONFIGS = {unique_gateway_name: {"unfiltered_sensitive_keys": ["bar"]}}

        synchronizer = GatewaySynchronizer(
            None,
            GatewaySyncData(
                name=unique_gateway_name,
                description="desc",
                description_en="desc en",
                maintainers=["admin"],
                status=1,
                is_public=True,
                gateway_type=GatewayTypeEnum.OFFICIAL_API.value,
                user_config={"from_bk_token": False},
            ),
            bk_app_code="app1",
        )
        synchronizer._create_gateway()
        assert synchronizer.gateway.id

        gateway = Gateway.objects.get(name=unique_gateway_name)
        assert gateway.id == synchronizer.gateway.id
        assert gateway.description == "desc"
        assert gateway.description_en == "desc en"
        assert gateway.maintainers == ["admin"]
        assert gateway.status == 1
        assert gateway.is_public is True

        auth_config = GatewayHandler.get_gateway_auth_config(gateway.id)
        assert auth_config["user_auth_type"] == "default"
        assert auth_config["api_type"] == 1
        assert auth_config["user_conf"]["from_bk_token"] is False
        assert auth_config["unfiltered_sensitive_keys"] == ["bar"]

        assert GatewayRelatedApp.objects.filter(gateway=gateway).count() == 1

    def test_update(self, settings, fake_gateway):
        settings.DEFAULT_USER_AUTH_TYPE = "default"
        settings.SPECIAL_GATEWAY_AUTH_CONFIGS = {fake_gateway.name: {"unfiltered_sensitive_keys": ["bar"]}}
        GatewayAuthContext().save(fake_gateway.id, {"user_auth_type": "default"})

        synchronizer = GatewaySynchronizer(
            fake_gateway,
            GatewaySyncData(
                name="",
                description="desc",
                description_en="desc en",
                maintainers=["admin", "admin2"],
                status=0,
                is_public=True,
                gateway_type=GatewayTypeEnum.OFFICIAL_API.value,
                user_config={"from_bk_token": False},
            ),
            bk_app_code="app1",
        )
        synchronizer._update_gateway()
        assert synchronizer.gateway.id

        gateway = Gateway.objects.get(name=fake_gateway.name)
        assert gateway.id == synchronizer.gateway.id
        assert gateway.description == "desc"
        assert gateway.description_en == "desc en"
        assert gateway.maintainers == ["admin", "admin2"]
        assert gateway.status == 1
        assert gateway.is_public is True

        auth_config = GatewayHandler.get_gateway_auth_config(gateway.id)
        assert auth_config["api_type"] == 1
        assert auth_config["user_conf"]["from_bk_token"] is False
        assert auth_config["unfiltered_sensitive_keys"] == ["bar"]

        assert GatewayRelatedApp.objects.filter(gateway=gateway).count() == 0

    def test_get_gateway_unfiltered_sensitive_keys(self, settings):
        settings.SPECIAL_GATEWAY_AUTH_CONFIGS = {"foo": {"unfiltered_sensitive_keys": ["bar"]}}

        synchronizer = GatewaySynchronizer(None, GatewaySyncData(name="foo", status=0))

        assert synchronizer._get_gateway_unfiltered_sensitive_keys("foo") == ["bar"]
        assert synchronizer._get_gateway_unfiltered_sensitive_keys("bar") is None
