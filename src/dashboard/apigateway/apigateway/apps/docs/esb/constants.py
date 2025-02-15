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
# from blue_krill.data_types.enum import EnumField, StructuredEnum

# from django.utils.translation import gettext_lazy as _

# 组件API模糊搜索时，结果数据限制大小
COMPONENT_SEARCH_LIMIT = 30


# class PermissionLevelEnum(StructuredEnum):
#     UNLIMITED = EnumField("unlimited", label=_("无限制"))
#     NORMAL = EnumField("normal", label=_("普通"))
#     SENSITIVE = EnumField("sensitive", label=_("敏感"))
#     SPECIAL = EnumField("special", label=_("特殊"))


# class LanguageEnum(StructuredEnum):
#     EN = EnumField("en", label="English")
#     ZH_HANS = EnumField("zh-hans", label=_("简体中文"))


# class ComponentDocTypeEnum(StructuredEnum):
#     MARKDOWN = EnumField("markdown", label="Markdown")
#     HTML = EnumField("html", label="Html")
#     RST = EnumField("rst", label="RST")


# class DataTypeEnum(StructuredEnum):
#     OFFICIAL_PUBLIC = EnumField(1, label=_("官方公开"))
#     OFFICIAL_HIDDEN = EnumField(2, label=_("官方隐藏"))
#     CUSTOM = EnumField(3, label=_("用户自定义"))
