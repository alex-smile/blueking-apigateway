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
# Generated by Django 3.2.18 on 2023-09-01 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_proxy_backend'),
        ('label', '0003_auto_20230227_2006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apilabel',
            old_name='api',
            new_name='gateway',
        ),
        migrations.AlterField(
            model_name='apilabel',
            name='gateway',
            field=models.ForeignKey(db_column='api_id', on_delete=django.db.models.deletion.CASCADE, to='core.gateway'),
        ),
        migrations.AlterUniqueTogether(
            name='apilabel',
            unique_together={('gateway', 'name')},
        ),
    ]
