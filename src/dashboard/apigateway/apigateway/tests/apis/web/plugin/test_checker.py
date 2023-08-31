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
from contextlib import nullcontext as does_not_raise

import pytest

from apigateway.apis.web.plugin.checker import (
    BkCorsChecker,
    BkIPRestrictionChecker,
    HeaderRewriteChecker,
    PluginConfigYamlChecker,
)
from apigateway.utils.yaml import yaml_dumps


class TestBkCorsChecker:
    @pytest.mark.parametrize(
        "data",
        [
            {
                "allow_origins": "**",
                "allow_methods": "**",
                "allow_headers": "**",
                "expose_headers": "",
                "max_age": 100,
                "allow_credential": True,
            },
            {
                "allow_origins_by_regex": ["^http://.*\\.example\\.com$"],
                "allow_methods": "**",
                "allow_headers": "**",
                "expose_headers": "",
                "max_age": 100,
                "allow_credential": True,
            },
            {
                "allow_origins": "*",
                "allow_methods": "*",
                "allow_headers": "*",
                "expose_headers": "*",
                "max_age": 100,
                "allow_credential": False,
            },
        ],
    )
    def test_check(self, data):
        checker = BkCorsChecker()
        result = checker.check(yaml_dumps(data))
        assert result is None

    @pytest.mark.parametrize(
        "data",
        [
            {
                "allow_origins": "*",
                "allow_methods": "*",
                "allow_headers": "*",
                "expose_headers": "*",
                "max_age": 100,
                "allow_credential": True,  # 当 'allow_credential' 为 True 时，allow_origins 不能为 '*'
            },
            {
                "allow_origins_by_regex": ["\\"],  # invalid regex
                "allow_methods": "*",
                "allow_headers": "*",
                "expose_headers": "*",
                "max_age": 100,
                "allow_credential": False,
            },
            {
                "allow_origins": "*",
                "allow_origins_by_regex": "http://.*.example.com",  # should be a list
                "allow_methods": "*",
                "allow_headers": "*",
                "expose_headers": "*",
                "max_age": 100,
                "allow_credential": False,
            },
            {
                "allow_origins": "",
                "allow_origins_by_regex": [],  # allow_origins, allow_origins_by_regex 不能同时为空
                "allow_methods": "**",
                "allow_headers": "**",
                "expose_headers": "**",
                "max_age": 100,
                "allow_credential": False,
            },
            {
                "allow_origins": "http://foo.com",
                "allow_methods": "GET,POST,PUT,GET",  # duplicated, invalid
                "allow_headers": "**",
                "expose_headers": "**",
                "max_age": 100,
                "allow_credential": False,
            },
            {
                "allow_origins": "http://foo.com",
                "allow_methods": "**",
                "allow_headers": "x-token,x-token",  # duplicated, invalid
                "expose_headers": "",
                "max_age": 100,
                "allow_credential": False,
            },
        ],
    )
    def test_check__error(self, data):
        checker = BkCorsChecker()
        with pytest.raises(ValueError):
            checker.check(yaml_dumps(data))

    @pytest.mark.parametrize(
        "allow_methods",
        [
            "*",
            "**",
            "GET,POST,PUT,DELETE,PATCH,HEAD,OPTIONS,CONNECT,TRACE",
            "GET,POST,OPTIONS",
            "GET",
        ],
    )
    def test_check_allow_methods(self, allow_methods):
        checker = BkCorsChecker()
        assert checker._check_allow_methods(allow_methods) is None

    @pytest.mark.parametrize(
        "allow_methods",
        [
            "GET,POST,GET",  # duplicate GET
        ],
    )
    def test_check_allow_methods__error(self, allow_methods):
        checker = BkCorsChecker()
        with pytest.raises(ValueError):
            checker._check_allow_methods(allow_methods)

    @pytest.mark.parametrize(
        "headers",
        [
            "Bk-Token",
            "Bk-Token,X-Token",
            "BK-TOKEN",
        ],
    )
    def test_check_headers(self, headers):
        checker = BkCorsChecker()
        assert checker._check_headers(headers, "key") is None

    @pytest.mark.parametrize(
        "headers",
        [
            "Bk-Token,Bk-Token",  # duplicate
        ],
    )
    def test_check_headers__error(self, headers):
        checker = BkCorsChecker()
        with pytest.raises(ValueError):
            checker._check_headers(headers, "key")

    @pytest.mark.parametrize(
        "data",
        [
            ["a", "b"],
        ],
    )
    def test_check_duplicate_items(self, data):
        checker = BkCorsChecker()
        result = checker._check_duplicate_items(data, "key")
        assert result is None

    @pytest.mark.parametrize(
        "data",
        [
            ["a", "b", "a"],
        ],
    )
    def test_check_duplicate_items__error(self, data):
        checker = BkCorsChecker()
        with pytest.raises(ValueError):
            checker._check_duplicate_items(data, "key")


class TestBkIPRestrictionChecker:
    @pytest.mark.parametrize(
        "data",
        [
            "whitelist: |-\n 1.1.1.1",
            "blacklist: |-\n 1.1.1.1",
            "whitelist: |-\n 1.1.1.1/24",
            "whitelist: |-\n 2002::1234:abcd:ffff:c0a8:101",
            "whitelist: |-\n 2002::1234:abcd:ffff:c0a8:101/64",
            "whitelist: |-\n 1.1.1.1\n 2.2.2.2",
            "whitelist: |-\n 1.1.1.1\n 2.2.2.2\r\n 3.3.3.3",
            "whitelist: |-\n 1.1.1.1\n # comment\r\n 3.3.3.3",
        ],
    )
    def test_check(self, data):
        checker = BkIPRestrictionChecker()
        result = checker.check(data)
        assert result is None

    @pytest.mark.parametrize(
        "data",
        [
            "",
            "abc: |-\n 1.1.1.1",
            "whitelist: |-\n a",
            "blacklist: |-\n a",
        ],
    )
    def test_check__error(self, data):
        checker = BkIPRestrictionChecker()
        with pytest.raises(ValueError):
            checker.check(data)


class TestPluginConfigYamlChecker:
    @pytest.mark.parametrize(
        "type_code, data",
        [
            (
                "bk-test",
                {"foo": "bar", "colors": ["green"]},
            ),
            (
                "bk-cors",
                {
                    "allow_origins": "",
                    "allow_origins_by_regex": ["^http://.*\\.example\\.com$"],
                    "allow_methods": "**",
                    "allow_headers": "**",
                    "expose_headers": "",
                    "max_age": 100,
                    "allow_credential": True,
                },
            ),
        ],
    )
    def test_check(self, type_code, data):
        checker = PluginConfigYamlChecker(type_code)
        result = checker.check(yaml_dumps(data))
        assert result is None

    @pytest.mark.parametrize(
        "type_code, data",
        [
            (
                "bk-cors",
                {
                    "allow_origins": "*",
                    "allow_methods": "*",
                    "allow_headers": "*",
                    "expose_headers": "*",
                    "max_age": 100,
                    "allow_credential": True,
                },
            ),
        ],
    )
    def test_check__error(self, type_code, data):
        checker = PluginConfigYamlChecker(type_code)
        with pytest.raises(ValueError):
            checker.check(yaml_dumps(data))


class TestHeaderRewriteChecker:
    @pytest.mark.parametrize(
        "data, ctx",
        [
            (
                {"set": [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}], "remove": []},
                does_not_raise(),
            ),
            (
                {"set": [{"key": "key1", "value": "value1"}, {"key": "key1", "value": "value2"}], "remove": []},
                pytest.raises(ValueError),
            ),
        ],
    )
    def test_check(self, data, ctx):
        checker = HeaderRewriteChecker()
        with ctx:
            checker.check(yaml_dumps(data))

    @pytest.mark.parametrize(
        "type_code, data, ctx",
        [
            (
                "bk-header-rewrite",  # set key 无重复
                {"set": [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}], "remove": []},
                does_not_raise(),
            ),
            (
                "bk-header-rewrite",  # set key 重复
                {"set": [{"key": "key1", "value": "value1"}, {"key": "key1", "value": "value2"}], "remove": []},
                pytest.raises(ValueError),
            ),
            (
                "bk-header-rewrite",  # remove key 无重复
                {
                    "set": [],
                    "remove": [{"key": "key1"}, {"key": "key2"}],
                },
                does_not_raise(),
            ),
            (
                "bk-header-rewrite",  # remove key 重复
                {
                    "set": [],
                    "remove": [{"key": "key1"}, {"key": "key1"}],
                },
                pytest.raises(ValueError),
            ),
        ],
    )
    def test_check_plugin(self, type_code, data, ctx):
        checker = PluginConfigYamlChecker(type_code)

        with ctx:
            checker.check(yaml_dumps(data))
