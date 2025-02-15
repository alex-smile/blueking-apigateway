# -*- coding: utf-8 -*-
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
from ddf import G

from apigateway.apis.open.stage import views
from apigateway.core.constants import StageStatusEnum
from apigateway.core.models import Gateway, Stage
from apigateway.tests.utils.testing import get_response_json

pytestmark = pytest.mark.django_db


class TestStageViewSet:
    def test_list(self, request_factory, fake_gateway):
        request = request_factory.get("/")
        request.gateway = fake_gateway

        s1 = G(Stage, name="prod", api=fake_gateway, status=StageStatusEnum.ACTIVE.value)
        s2 = G(Stage, name="test", api=fake_gateway, status=StageStatusEnum.ACTIVE.value)
        G(Stage, name="stag", api=fake_gateway, status=StageStatusEnum.ACTIVE.value, is_public=False)

        # have 2 active stages
        view = views.StageViewSet.as_view({"get": "list"})
        response = view(request)
        result = get_response_json(response)

        assert result["code"] == 0
        assert result["data"] == [
            {
                "id": s1.id,
                "name": s1.name,
                "description": s1.description,
            },
            {
                "id": s2.id,
                "name": s2.name,
                "description": s2.description,
            },
        ]

        # have 1 active stages
        s2.status = StageStatusEnum.INACTIVE.value
        s2.save()

        view = views.StageViewSet.as_view({"get": "list"})
        response = view(request)
        result = get_response_json(response)

        assert result["code"] == 0
        assert result["data"] == [
            {
                "id": s1.id,
                "name": s1.name,
                "description": s1.description,
            },
        ]

    def test_list_by_gateway_name(self, request_to_view, request_factory, fake_gateway):
        request = request_factory.get("")
        request.gateway = fake_gateway

        stage = G(Stage, name="prod", api=fake_gateway, status=StageStatusEnum.ACTIVE.value)

        response = request_to_view(
            request, view_name="openapi.stage.list_by_gateway_name", path_params={"gateway_name": fake_gateway.name}
        )

        result = get_response_json(response)

        assert result["code"] == 0
        assert result["data"] == [
            {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
            },
        ]


class TestStageV1ViewSet:
    def list_stages_with_resource_version(self, request_to_view, request_factory, fake_release):
        request = request_factory.get("")
        request.gateway = fake_release.api

        G(Stage, name="test", api=request.gateway, status=StageStatusEnum.ACTIVE.value)

        response = request_to_view(
            request,
            view_name="openapi.stage.list_stages_with_resource_version",
            path_params={"gateway_name": request.gateway.name},
        )

        result = get_response_json(response)

        assert result["code"] == 0
        assert result["data"] == [
            {
                "name": fake_release.stage.name,
                "released": True,
                "resource_version": {
                    "version": fake_release.resource_version.version,
                },
            },
            {
                "name": "test",
                "released": False,
                "resource_version": None,
            },
        ]


class TestStageSyncViewSet:
    def test_sync(self, mocker, unique_gateway_name, request_factory):
        mocker.patch(
            "apigateway.apis.open.stage.views.GatewayRelatedAppPermission.has_permission",
            return_value=True,
        )

        api = G(Gateway, name=unique_gateway_name, is_public=False)

        request = request_factory.post(
            f"/api/v1/apis/{unique_gateway_name}/stages/sync/",
            data={
                "name": "prod",
                "description": "desc",
                "vars": {},
                "proxy_http": {
                    "timeout": 30,
                    "upstreams": {
                        "loadbalance": "roundrobin",
                        "hosts": [
                            {
                                "host": "http://www.a.com",
                            }
                        ],
                    },
                    "transform_headers": {
                        "set": {"k1": "v1"},
                    },
                },
                "rate_limit": {
                    "enabled": True,
                    "rate": {
                        "tokens": 100,
                        "period": 60,
                    },
                },
            },
        )
        request.gateway = api

        view = views.StageSyncViewSet.as_view({"post": "sync"})
        response = view(request, gateway_name=unique_gateway_name)

        result = get_response_json(response)
        stage = Stage.objects.get(api=api, name="prod")
        assert result["code"] == 0
        assert stage.status == 0
