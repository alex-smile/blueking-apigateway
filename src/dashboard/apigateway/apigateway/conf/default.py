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
"""
Django settings for apigateway project.

Generated by 'django-admin startproject' using Django 2.0.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from typing import Any, Dict, List
from urllib.parse import quote

from celery.schedules import crontab
from tencent_apigateway_common.env import Env

from apigateway.conf.celery_conf import *  # noqa
from apigateway.conf.celery_conf import CELERY_BEAT_SCHEDULE
from apigateway.conf.log_utils import get_logging_config, makedirs_when_not_exists
from apigateway.conf.utils import get_default_keepalive_options

env = Env()

ENCRYPT_KEY = env.str("ENCRYPT_KEY")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
BK_APP_CODE = env.str("BK_APP_CODE", "bk_apigateway")
BK_APP_SECRET = env.str("BK_APP_SECRET")
SECRET_KEY = env.str("SECRET_KEY", BK_APP_SECRET)

DEFAULT_TEST_APP = {
    "bk_app_code": env.str("DEFAULT_TEST_APP_CODE", BK_APP_CODE),
    "bk_app_secret": env.str("DEFAULT_TEST_APP_SECRET", BK_APP_SECRET),
}

JWT_CRYPTO_KEY = ENCRYPT_KEY
LOG_LINK_SECRET = ENCRYPT_KEY

# use the same nonce, should not be changed at all!!!!!!
CRYPTO_NONCE = env.str("BK_APIGW_CRYPTO_NONCE", "q76rE8srRuYM")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "raven.contrib.django.raven_compat",
    "django_celery_beat",
    "rest_framework",
    "drf_yasg",
    "corsheaders",
    "apigateway.apigateway",
    "apigateway.apps.monitor",
    "apigateway.schema",
    "apigateway.core",
    "apigateway.apps.access_strategy",
    "apigateway.apps.plugin",
    "apigateway.apps.label",
    "apigateway.apps.permission",
    "apigateway.apps.audit",
    "apigateway.apps.metrics",
    "apigateway.apps.support",
    "django_prometheus",
    "bkpaas_auth",
    "apigateway.account",
    "apigateway.apps.feature",
    "apigateway.apps.esb",
    "apigateway.apps.esb.bkcore",
    "apigateway.apps.docs.feedback",
    "apigw_manager.apigw",
    "apigateway.controller",
    "apigateway.healthz",
    "apigateway.iam",
    # TODO: 待启用 IAM 鉴权后，需启用以下两个 django app
    # "apigateway.iam.apigw_iam_migration",
    # "iam.contrib.iam_migration",
    # 开源版旧版 ESB 数据
    "apigateway.legacy_esb",
    "apigateway.legacy_esb.paas2",
]

MIDDLEWARE = [
    # 这个必须在最前
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "apigateway.common.middlewares.request_id.RequestIDMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 蓝鲸静态资源服务
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "bkpaas_auth.middlewares.CookieLoginMiddleware",
    "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",
    "apigateway.account.middlewares.ApiGatewayJWTAppMiddleware",
    "apigateway.account.middlewares.ApiGatewayJWTUserMiddleware",
    "apigateway.account.middlewares.SelfAppCodeAppSecretLoginMiddleware",
    # 这个必须在最后
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "apigateway.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


DATABASE_ROUTERS = [
    "apigateway.utils.db_router.DBRouter",
]

# django 3.2 add
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# CSRF Config
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_COOKIE_DOMAIN = env.str("DASHBOARD_CSRF_COOKIE_DOMAIN")
CSRF_COOKIE_NAME = env.str("DASHBOARD_CSRF_COOKIE_NAME", f"{BK_APP_CODE}_csrftoken")

# Session Config
SESSION_COOKIE_AGE = 60 * 60 * 24
SESSION_COOKIE_NAME = env.str("DASHBOARD_SESSION_COOKIE_NAME", f"{BK_APP_CODE}_sessionid")
SESSION_COOKIE_DOMAIN = CSRF_COOKIE_DOMAIN or env.str("DASHBOARD_SESSION_COOKIE_DOMAIN")

# CORS Config
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST: List[str] = env.list("CORS_ORIGIN_REGEX_WHITELIST", default=[])

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "zh-hans"
USE_I18N = True
USE_L10N = True

# timezone
TIME_ZONE = "Asia/Shanghai"
USE_TZ = True

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

LANGUAGES = (
    ("en", "English"),
    ("zh-cn", "简体中文"),
    ("zh-hans", "简体中文"),
)

LANGUAGE_COOKIE_PATH = "/"

# 国际化 cookie 信息必须跟整个蓝鲸体系保存一致
LANGUAGE_COOKIE_NAME = "blueking_language"

# 国际化 cookie 默认写在整个蓝鲸的根域下
LANGUAGE_COOKIE_DOMAIN = env.str("DASHBOARD_LANGUAGE_COOKIE_DOMAIN", None) or CSRF_COOKIE_DOMAIN

# django translation, 避免循环引用
gettext = lambda s: s  # noqa

# 站点 URL
SITE_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# 是否为本地开发环境
IS_LOCAL = env.bool("DASHBOARD_IS_LOCAL", default=False)

# static root and dirs to find static
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/backend/static/"

# About whitenoise
WHITENOISE_STATIC_PREFIX = "/backend/static/"

AUTHENTICATION_BACKENDS = [
    "bkpaas_auth.backends.DjangoAuthUserCompatibleBackend",
]

AUTH_USER_MODEL = "account.AuthUser"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apigateway.common.exception_handler.custom_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "apigateway.common.permissions.GatewayPermission",
    ),
    "DEFAULT_PAGINATION_CLASS": "apigateway.utils.paginator.StandardLimitOffsetPagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S %z",
}

SWAGGER_SETTINGS = {
    "DEFAULT_AUTO_SCHEMA_CLASS": "apigateway.utils.swagger.ResponseSwaggerAutoSchema",
}

# https://docs.djangoproject.com/en/3.2/ref/checks/
# disable warnings: db_table '<table_name>' is used by multiple models
SILENCED_SYSTEM_CHECKS = ["models.W035"]

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env.str("BK_APIGW_DATABASE_ENGINE", "django.db.backends.mysql"),
        "NAME": env.str("BK_APIGW_DATABASE_NAME", BK_APP_CODE),
        "USER": env.str("BK_APIGW_DATABASE_USER", BK_APP_CODE),
        "PASSWORD": env.str("BK_APIGW_DATABASE_PASSWORD", ""),
        "HOST": env.str("BK_APIGW_DATABASE_HOST", "localhost"),
        "PORT": env.int("BK_APIGW_DATABASE_PORT", 3306),
        "OPTIONS": {
            "isolation_level": env.str("BK_APIGW_DATABASE_ISOLATION_LEVEL", "READ COMMITTED"),
        },
    },
    "bkcore": {
        "ENGINE": env.str("BK_ESB_DATABASE_ENGINE", "django.db.backends.mysql"),
        "NAME": env.str("BK_ESB_DATABASE_NAME", "bk_esb"),
        "USER": env.str("BK_ESB_DATABASE_USER", BK_APP_CODE),
        "PASSWORD": env.str("BK_ESB_DATABASE_PASSWORD", ""),
        "HOST": env.str("BK_ESB_DATABASE_HOST", "localhost"),
        "PORT": env.int("BK_ESB_DATABASE_PORT", 3306),
        "OPTIONS": {
            "isolation_level": env.str("BK_ESB_DATABASE_ISOLATION_LEVEL", "READ COMMITTED"),
        },
    },
    "paas2": {
        "ENGINE": env.str("BK_PAAS2_DATABASE_ENGINE", "django.db.backends.mysql"),
        "NAME": env.str("BK_PAAS2_DATABASE_NAME", ""),
        "USER": env.str("BK_PAAS2_DATABASE_USER", ""),
        "PASSWORD": env.str("BK_PAAS2_DATABASE_PASSWORD", ""),
        "HOST": env.str("BK_PAAS2_DATABASE_HOST", ""),
        "PORT": env.int("BK_PAAS2_DATABASE_PORT", 3306),
        "OPTIONS": {
            "isolation_level": env.str("BK_PAAS2_DATABASE_ISOLATION_LEVEL", "READ COMMITTED"),
        },
    },
}

# 如果 paas2 database 未配置，则去除
BK_PAAS2_ENABLED = all([DATABASES["paas2"]["NAME"], DATABASES["paas2"]["USER"], DATABASES["paas2"]["HOST"]])
if not BK_PAAS2_ENABLED:
    DATABASES.pop("paas2", None)

# redis 配置
REDIS_HOST = env.str("BK_APIGW_REDIS_HOST", "localhost")
REDIS_PORT = env.int("BK_APIGW_REDIS_PORT", 6379)
REDIS_PASSWORD = env.str("BK_APIGW_REDIS_PASSWORD", "")
REDIS_PREFIX = env.str("BK_APIGW_REDIS_PREFIX", "apigw::")
REDIS_MAX_CONNECTIONS = env.int("BK_APIGW_REDIS_MAX_CONNECTIONS", 100)
REDIS_DB = env.int("BK_APIGW_REDIS_DB", 0)
# sentinel check
REDIS_USE_SENTINEL = env.bool("BK_APIGW_REDIS_USE_SENTINEL", False)
REDIS_SENTINEL_MASTER_NAME = env.str("BK_APIGW_REDIS_SENTINEL_MASTER_NAME", "mymaster")
# sentinel password is not the same as redis password, so you should both set the passwords
REDIS_SENTINEL_PASSWORD = env.str("BK_APIGW_REDIS_SENTINEL_PASSWORD", "")
REDIS_SENTINEL_ADDR_STR = env.str("BK_APIGW_REDIS_SENTINEL_ADDR", "")
# parse sentinel address from "host1:port1,host2:port2" to [("host1", port1), ("host2", port2)]
REDIS_SENTINEL_ADDR_LIST = [tuple(addr.split(":")) for addr in REDIS_SENTINEL_ADDR_STR.split(",") if addr]

DEFAULT_REDIS_CONFIG = CHANNEL_REDIS_CONFIG = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "password": REDIS_PASSWORD,
    "max_connections": REDIS_MAX_CONNECTIONS,
    "db": REDIS_DB,
    # sentinel
    "use_sentinel": REDIS_USE_SENTINEL,
    "master_name": REDIS_SENTINEL_MASTER_NAME,
    "sentinel_password": REDIS_SENTINEL_PASSWORD,
    "sentinels": REDIS_SENTINEL_ADDR_LIST,
}

# etcd 配置
ETCD_CONFIG = {
    "host": env.str("BK_ETCD_HOST", default="localhost"),
    "port": env.int("BK_ETCD_PORT", default=2379),
    "user": env.str("BK_ETCD_USER", default=None),
    "password": env.str("BK_ETCD_PASSWORD", default=None),
    "ca_cert": env.str("BK_ETCD_CA_PATH", default=None),
    "cert_cert": env.str("BK_ETCD_CERT_PATH", default=None),
    "cert_key": env.str("BK_ETCD_KEY_PATH", default=None),
}

# celery 配置
# 修改 Redis 连接时的 keepalive 配置，让连接更健壮
REDIS_CONNECTION_OPTIONS = {
    "socket_timeout": 3,
    "socket_connect_timeout": 3,
    "socket_keepalive": True,
    "socket_keepalive_options": get_default_keepalive_options(),
}
RABBITMQ_VHOST = env.str("BK_APIGW_RABBITMQ_VHOST", "")
RABBITMQ_PORT = env.str("BK_APIGW_RABBITMQ_PORT", "")
RABBITMQ_HOST = env.str("BK_APIGW_RABBITMQ_HOST", "")
RABBITMQ_USER = env.str("BK_APIGW_RABBITMQ_USER", "")
RABBITMQ_PASSWORD = env.str("BK_APIGW_RABBITMQ_PASSWORD", "")
if all([RABBITMQ_VHOST, RABBITMQ_PORT, RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD]):
    CELERY_BROKER_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
elif not REDIS_USE_SENTINEL:
    # 如果没有使用 Redis 作为 Broker，请不要启用该配置，详见：
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#broker-transport-options
    CELERY_BROKER_TRANSPORT_OPTIONS = REDIS_CONNECTION_OPTIONS
    CELERY_BROKER_URL = f"redis://:{quote(REDIS_PASSWORD)}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND = f"redis://:{quote(REDIS_PASSWORD)}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_TASK_DEFAULT_QUEUE = env.str(
        "BK_APIGW_CELERY_TASK_DEFAULT_QUEUE", f"{REDIS_PREFIX}bk_apigateway_dashboard_celery"
    )
else:
    # https://docs.celeryq.dev/en/v4.3.0/history/whatsnew-4.0.html?highlight=sentinel#redis-support-for-sentinel
    # sentinel://0.0.0.0:26379;sentinel://0.0.0.0:26380/...
    # REDIS_SENTINEL_ADDR_LIST = [(host1, port1), (host2, port2)]
    CELERY_SENTINEL_URL = ";".join(
        [f"sentinel://:{REDIS_PASSWORD}@" + ":".join(addr) + f"/{REDIS_DB}" for addr in REDIS_SENTINEL_ADDR_LIST]
    )
    CELERY_SENTINEL_TRANSPORT_OPTIONS = {
        "master_name": REDIS_SENTINEL_MASTER_NAME,
        "sentinel_kwargs": {"password": REDIS_SENTINEL_PASSWORD},
        **REDIS_CONNECTION_OPTIONS,
    }

    CELERY_BROKER_URL = CELERY_SENTINEL_URL
    CELERY_BROKER_TRANSPORT_OPTIONS = CELERY_SENTINEL_TRANSPORT_OPTIONS
    CELERY_RESULT_BACKEND = CELERY_SENTINEL_URL
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = CELERY_SENTINEL_TRANSPORT_OPTIONS
    CELERY_TASK_DEFAULT_QUEUE = env.str(
        "BK_APIGW_CELERY_TASK_DEFAULT_QUEUE", f"{REDIS_PREFIX}bk_apigateway_dashboard_celery"
    )

CELERY_BEAT_SCHEDULE.update(
    {
        "apigateway.legacy_esb.tasks.sync_legacy_esb_reusable_data": {
            "task": "apigateway.legacy_esb.tasks.sync_legacy_esb_reusable_data",
            "schedule": crontab(minute="*/5"),
        },
    }
)

if env.bool("FEATURE_FLAG_ENABLE_RUN_DATA_METRICS", True):
    CELERY_BEAT_SCHEDULE.update(
        {
            "apigateway.apps.metrics.tasks.statistics_request_by_day": {
                "task": "apigateway.apps.metrics.tasks.statistics_request_by_day",
                "schedule": crontab(minute=30, hour=0),
            },
            "apigateway.apps.permission.tasks.renew_app_resource_permission": {
                "task": "apigateway.apps.permission.tasks.renew_app_resource_permission",
                "schedule": crontab(minute=50, hour=0),
            },
        }
    )


# log 配置
LOG_LEVEL = env.str("LOG_LEVEL", "WARNING")
LOG_DIR = env.str("BK_APIGW_LOG_PATH", "")
LOGGING = get_logging_config(LOG_LEVEL, IS_LOCAL, LOG_DIR, bool(LOG_DIR))
makedirs_when_not_exists(LOG_DIR)

# sentry 配置
RAVEN_CONFIG = {
    "dsn": env.str("BK_APIGW_SENTRY_DSN", ""),
}

# Elasticsearch 配置
BK_APIGW_ES_USER = env.str("BK_APIGW_ES_USER", BK_APP_CODE)
# 密码中可能包含特殊字符
BK_APIGW_ES_PASSWORD = quote(env.str("BK_APIGW_ES_PASSWORD", ""))
BK_APIGW_ES_HOST = env.list("BK_APIGW_ES_HOST", default=[])
BK_APIGW_ES_PORT = env.str("BK_APIGW_ES_PORT", "9200")
ELASTICSEARCH_HOSTS = []
if BK_APIGW_ES_HOST and BK_APIGW_ES_PORT:
    ELASTICSEARCH_HOSTS = [f"{host}:{BK_APIGW_ES_PORT}" for host in BK_APIGW_ES_HOST]
    ELASTICSEARCH_HOSTS_WITHOUT_AUTH = ELASTICSEARCH_HOSTS.copy()
    if BK_APIGW_ES_USER and BK_APIGW_ES_PASSWORD:
        ELASTICSEARCH_HOSTS = [
            f"{BK_APIGW_ES_USER}:{BK_APIGW_ES_PASSWORD}@{host}:{BK_APIGW_ES_PORT}" for host in BK_APIGW_ES_HOST
        ]

DEFAULT_ES_SEARCH_TIMEOUT = env.int("DEFAULT_ES_SEARCH_TIMEOUT", 30)
DEFAULT_ES_HTTP_TIMEOUT = env.int("DEFAULT_ES_HTTP_TIMEOUT", 30)
DEFAULT_ES_AGGS_TERM_SIZE = env.int("DEFAULT_ES_AGGS_TERM_SIZE", 1000)

# bkrepo 配置
BKREPO_ENDPOINT_URL = env.str("BKREPO_ENDPOINT_URL", "")
BKREPO_USERNAME = env.str("BKREPO_USERNAME", "bk_apigateway")
BKREPO_PASSWORD = env.str("BKREPO_PASSWORD", "")
BKREPO_PROJECT = env.str("BKREPO_PROJECT", "bk_apigateway")
BKREPO_GENERIC_BUCKET = env.str("BKREPO_GENERIC_BUCKET", "generic")

# pypi 镜像源配置
PYPI_MIRRORS_CONFIG = {
    "default": {
        "repository_url": env.str("DEFAULT_PYPI_REPOSITORY_URL", ""),
        "index_url": env.str("DEFAULT_PYPI_INDEX_URL", ""),
        "username": env.str("DEFAULT_PYPI_USERNAME", ""),
        "password": env.str("DEFAULT_PYPI_PASSWORD", ""),
    }
}

PYPI_MIRRORS_REPOSITORY = env.str("PYPI_INDEX_URL", "https://pypi.org/simple/")

# 模板变量
BK_API_URL_TMPL = env.str("BK_API_URL_TMPL", "").rstrip("/")
BK_COMPONENT_API_URL = env.str("BK_COMPONENT_API_URL", "")
API_RESOURCE_URL_TMPL = env.str("API_RESOURCE_URL_TMPL", "")
API_DOCS_URL_TMPL = env.str("API_DOCS_URL_TMPL", "")
RESOURCE_DOC_URL_TMPL = env.str("RESOURCE_DOC_URL_TMPL", "")
COMPONENT_DOC_URL_TMPL = env.str("COMPONENT_DOC_URL_TMPL", "")
BK_API_INNER_URL_TMPL = env.str("BK_API_INNER_URL_TMPL", "") or BK_API_URL_TMPL
BK_COMPONENT_API_INNER_URL = env.str("BK_COMPONENT_API_INNER_URL", "") or BK_COMPONENT_API_URL
BK_PAAS3_API_URL = BK_API_INNER_URL_TMPL.format(api_name="bkpaas3")
BK_APIGATEWAY_API_URL = env.str("BK_APIGATEWAY_API_URL", "")

DASHBOARD_URL = env.str("DASHBOARD_URL", "").rstrip("/")

DASHBOARD_FE_URL = env.str("DASHBOARD_FE_URL", "").rstrip("/")
# 将前端 URL 默认添加到 CORS 白名单，可不配置环境变量 CORS_ORIGIN_REGEX_WHITELIST
if DASHBOARD_FE_URL and DASHBOARD_FE_URL not in CORS_ORIGIN_REGEX_WHITELIST:
    CORS_ORIGIN_REGEX_WHITELIST.append(DASHBOARD_FE_URL)

GATEWAY_DEFAULT_CREATOR = env.str("GATEWAY_DEFAULT_CREATOR", "admin")
DEFAULT_USER_AUTH_TYPE = "default"

APIGW_MANAGERS = env.list("APIGW_MANAGERS", default=["admin"])

# 网关 jwt 签发者，必须与 apigateway 后端服务保持一致，
# apigw-manager sdk 利用 issuer 支持获取不同网关实例同名网关的公钥，以支持同一后端服务接入不同网关实例
JWT_ISSUER = env.str("BK_APIGW_JWT_ISSUER", "")

# 检查保留的官方网关名
CHECK_RESERVED_GATEWAY_NAME = True
# 保留的网关名前缀，检查保留网关名时，不允许在管理端创建此前缀的网关
RESERVED_GATEWAY_NAME_PREFIXES = ["bk-"]
# 官方网关命名前缀，仅做标记
OFFICIAL_GATEWAY_NAME_PREFIXES = ["bk-"]
# 允许管理端更新网关认证信息
DEFAULT_ALLOW_UPDATE_API_AUTH = True

# 网关用户认证配置
API_USER_AUTH_CONFIGS = {
    "default": {
        "user_type": "default",
        "from_bk_token": True,
        "from_username": True,
    }
}

# 特殊的网关认证配置，在网关同步时，会更新网关的这些配置
SPECIAL_API_AUTH_CONFIGS = {
    "bk-auth": {
        "unfiltered_sensitive_keys": ["bk_token", "access_token"],
    },
}

# 默认环境的默认后端
DEFAULT_STAGE_UPSTREAMS = {
    "loadbalance": "roundrobin",
    "hosts": [
        {
            "host": "",
            "weight": 100,
        }
    ],
}

DEFAULT_STAGE_RATE_LIMIT_CONFIG = {
    "enabled": False,
    "rate": {
        "tokens": 5000,
        "period": 60,
    },
}

# 微网关 chart 信息
BCS_MICRO_GATEWAY_CHART_NAME = "bk-micro-gateway"
BCS_MICRO_GATEWAY_CHART_VERSION = "v1.0.0-alpha.2"
BCS_MICRO_GATEWAY_IMAGE_REGISTRY = ""
BCS_MICRO_GATEWAY_SENTRY_DSN = env.str("BCS_MICRO_GATEWAY_SENTRY_DSN", "")

# 公共 chart 仓库
BCS_PUBLIC_CHART_PROJECT = "bcs-public-project"
BCS_PUBLIC_CHART_REPOSITORY = "public-repo"

# BCS 为网关分配的认证 Token
BCS_API_GATEWAY_TOKEN = env.str("BCS_API_GATEWAY_TOKEN", "")

# 网关部署集群所属业务ID，影响从蓝鲸监控拉取 Prometheus 数据等功能；开源环境默认部署在蓝鲸业务(业务 ID=2)
BCS_CLUSTER_BK_BIZ_ID = env.str("BCS_CLUSTER_BK_BIZ_ID", "2")

# edge controller 配置
EDGE_CONTROLLER_API_NAME = "bk-apigateway"
# 托管的微网关实例，实例部署所用 chart 由网关生成，此 chart 中，endpoints + base_path 应为微网关实例访问网关数据的网关接口地址前缀
EDGE_CONTROLLER_API_BASE_PATH = env.str("EDGE_CONTROLLER_API_BASE_PATH", "/")

# plugin metadata config
PLUGIN_METADATA_CONFIG = {
    "file-logger": {
        "log_format": {
            # 请求信息
            "proto": "$server_protocol",
            "method": "$request_method",
            "http_host": "$host",
            "http_path": "$uri",
            "headers": "-",
            "params": "$args",
            "body": "$bk_log_request_body",
            "app_code": "$bk_app_code",
            "client_ip": "$remote_addr",
            "request_id": "$bk_request_id",
            "x_request_id": "$x_request_id",
            "request_duration": "$bk_log_request_duration",
            # 网关信息
            "api_id": "$bk_gateway_id",
            "api_name": "$bk_gateway_name",
            "resource_id": "$bk_resource_id",
            "resource_name": "$bk_resource_name",
            "stage": "$bk_stage_name",
            # 后端服务
            "backend_scheme": "$upstream_scheme",
            "backend_method": "$method",
            # 后端服务 Host，即后端服务配置中的域名或 IP+Port
            "backend_host": "$bk_backend_host",
            # 后端服务地址，请求后端时，实际请求的 IP+Port，若后端服务配置中为域名，则为域名解析后的地址
            "backend_addr": "$upstream_addr",
            "backend_path": "$bk_log_backend_path",
            "backend_duration": "$bk_log_upstream_duration",
            # 响应
            "response_body": "$bk_log_response_body",
            "response_size": "$body_bytes_sent",
            "status": "$status",
            # 其它
            "msg": "-",
            "level": "info",
            "code_name": "$bk_apigw_error_code_name",
            "error": "$bk_apigw_error_message",
            "proxy_error": "$proxy_error",
            "instance": "$instance_id",
            "timestamp": "$bk_log_request_timestamp",
        }
    },
    "bk-concurrency-limit": {
        "conn": env.int("GATEWAY_CONCURRENCY_LIMIT_CONN", 2000),
        "burst": env.int("GATEWAY_CONCURRENCY_LIMIT_BURST", 1000),
        "default_conn_delay": env.int("GATEWAY_CONCURRENCY_LIMIT_DEFAULT_CONN_DELAY", 1),  # second
        "key_type": "var",
        "key": "bk_concurrency_limit_key",
    },
    "bk-real-ip": {
        "recursive": env.bool("GATEWAY_REAL_IP_RECURSIVE", False),
        "source": env.str("GATEWAY_REAL_IP_SOURCE", "http_x_forwarded_for"),
        "trusted_addresses": env.list("GATEWAY_REAL_IP_TRUSTED_ADDRESSES", default=["127.0.0.1", "::1"]),
    },
    "bk-opentelemetry": {
        "sampler": {
            # change to always_off/always_on/parent_base if needed!
            "name": env.str("GATEWAY_OTEL_SAMPLER_NAME", "always_off"),
            "options": {
                "root": {
                    "name": "trace_id_ratio",
                    "options": {"fraction": env.float("GATEWAY_OTEL_ROOT_SAMPLER_RATIO", default=0.01)},
                }
            },
        },
        "additional_attributes": [],
    },
}

APISIX_CONFIG = {
    "pluginAttrs": {
        "log-rotate": {
            # 每间隔多长时间切分一次日志，秒为单位
            "interval": 60 * 60,
            # 最多保留多少份历史日志，超过指定数量后，自动删除老文件
            "max_kept": 24 * 7,
        },
        "prometheus": {
            "export_addr": {
                "ip": "0.0.0.0",
            },
        },
    },
}

# 内置的后端服务健康检查，按网关配置
MICRO_GATEWAY_STAGE_UPSTREAM_CHECKS: Dict[str, Any] = {}

BK_GATEWAY_RESOURCE_LABEL_PREFIX = "gateway.bk.tencent.com/"
BK_GATEWAY_ETCD_NAMESPACE_PREFIX = env.str("BK_GATEWAY_ETCD_NAMESPACE_PREFIX", default="/bk-gateway-apigw")

# 默认微网关共享实例
DEFAULT_MICRO_GATEWAY_ID = env.str("DEFAULT_MICRO_GATEWAY_ID", default="faf44a48-59e9-f790-2412-e56c90551fb3")
DEFAULT_GATEWAY_HOSTING_TYPE = env.int("DEFAULT_GATEWAY_HOSTING_TYPE", 1)

# prometheus 配置
PROMETHEUS_METRIC_NAME_PREFIX = env.str("PROMETHEUS_METRIC_NAME_PREFIX", "bk_apigateway_")
PROMETHEUS_DEFAULT_LABELS = [
    # example: foo=bar => [("foo", "=", "bar")]
    (key, "=", value)
    for key, value in env.dict("PROMETHEUS_DEFAULT_LABELS", default={}).items()
]

# DB 操作大小配置
RELEASED_RESOURCE_CREATE_BATCH_SIZE = env.int("RELEASED_RESOURCE_CREATE_BATCH_SIZE", 50)
RELEASED_RESOURCE_DOC_CREATE_BATCH_SIZE = env.int("RELEASED_RESOURCE_DOC_CREATE_BATCH_SIZE", 50)

# 网关资源数量限制
MAX_STAGE_COUNT_PER_GATEWAY = env.int("MAX_STAGE_COUNT_PER_GATEWAY", 20)
API_GATEWAY_RESOURCE_LIMITS = {
    "max_gateway_count_per_app": env.int("MAX_GATEWAY_COUNT_PER_APP", 10),  # 每个 app 最多创建的网关数量
    "max_resource_count_per_gateway": env.int("MAX_RESOURCE_COUNT_PER_GATEWAY", 1000),  # 每个网关最多创建的 api 数量
    # 配置 app 的特殊规则
    "max_gateway_count_per_app_whitelist": {
        "bk_sops": 1000000,  # 标准运维网关数量无限制
    },
    # 配置网关的特殊规则
    "max_resource_count_per_gateway_whitelist": {
        "bk-esb": 5000,
        "bk-base": 2000,
    },
}
for k, v in env.dict("MAX_GATEWAY_COUNT_PER_APP_WHITELIST", default={}).items():
    API_GATEWAY_RESOURCE_LIMITS["max_gateway_count_per_app_whitelist"][k] = int(v)
for k, v in env.dict("MAX_RESOURCE_COUNT_PER_GATEWAY_WHITELIST", default={}).items():
    API_GATEWAY_RESOURCE_LIMITS["max_resource_count_per_gateway_whitelist"][k] = int(v)

# 网关下对象的最大数量
MAX_API_LABEL_COUNT_PER_GATEWAY = env.int("MAX_API_LABEL_COUNT_PER_GATEWAY", 100)

MAX_PYTHON_SDK_COUNT_PER_RESOURCE_VERSION = env.int("MAX_PYTHON_SDK_COUNT_PER_RESOURCE_VERSION", 99)

CACHE_KEY_PREFIX = "apigw:dp:"
CACHE_VERSION = "v1"

APIGW_REVERSION_UPDATE_CHANNEL_KEY = "apigateway:reversion:update"
APIGW_REVERSION_UPDATE_SET_KEY = "apigateway:reversion:update:set"

BK_LOGIN_TICKET_KEY_TO_COOKIE_NAME = {
    "bk_token": "bk_token",
}

BK_API_DEFAULT_STAGE_MAPPINGS = env.dict("BK_API_DEFAULT_STAGE_MAPPINGS", default={})

PYTHON_SDK_MANAGER_CLASS = "apigateway.apps.docs.esb.sdk.manager.SimplePythonSDKManager"

FAKE_SEND_NOTICE = env.bool("FAKE_SEND_NOTICE", default=False)

# ==============================================================================
# OTEL
# ==============================================================================
# tracing: otel 相关配置
ENABLE_OTEL_TRACE = env.bool("BK_APIGW_ENABLE_OTEL_TRACE", default=False)
OTEL_TYPE = env.str("BK_APIGW_OTEL_TYPE", default="grpc")
OTEL_GRPC_HOST = env.str("BK_APIGW_OTEL_GRPC_HOST", default="")
OTEL_HTTP_URL = env.str("BK_APIGW_OTEL_HTTP_URL", default="")
OTEL_HTTP_TIMEOUT = env.str("BK_APIGW_OTEL_HTTP_TIMEOUT", default=1)
OTEL_DATA_TOKEN = env.str("BK_APIGW_OTEL_DATA_TOKEN", default="")
OTEL_SAMPLER = env.str("DASHBOARD_OTEL_SAMPLER", default="always_on")
OTEL_SERVICE_NAME = env.str("DASHBOARD_OTEL_SERVICE_NAME", default="bk-apigateway-dashboard")
# instrument
OTEL_INSTRUMENT_DB_API = env.bool("DASHBOARD_OTEL_INSTRUMENT_DB_API", default=False)
OTEL_INSTRUMENT_CELERY = env.bool("DASHBOARD_OTEL_INSTRUMENT_CELERY", default=False)
OTEL_INSTRUMENT_REDIS = env.bool("DASHBOARD_OTEL_INSTRUMENT_REDIS", default=False)

# bkpaas-auth 配置
BK_PAAS_LOGIN_URL = env.str("BK_PAAS_LOGIN_URL", "")
BKAUTH_BACKEND_TYPE = "bk_token"
BKAUTH_USER_COOKIE_VERIFY_URL = f"{BK_PAAS_LOGIN_URL}/api/v3/is_login/"

BKAUTH_TOKEN_APP_CODE = BK_APP_CODE
BKAUTH_TOKEN_SECRET_KEY = BK_APP_SECRET
BKAUTH_TOKEN_USER_INFO_ENDPOINT = f"{BK_COMPONENT_API_INNER_URL}/api/c/compapi/v2/bk_login/get_user/"

# bk-iam 配置
BK_IAM_SYSTEM_ID = "bk_apigateway"
BK_IAM_USE_APIGATEWAY = True
BK_IAM_GATEWAY_STAGE = BK_API_DEFAULT_STAGE_MAPPINGS.get("bk-iam", "prod")
BK_IAM_APIGATEWAY_URL = f"{BK_API_URL_TMPL.format(api_name='bk-iam')}/{BK_IAM_GATEWAY_STAGE}"
BK_IAM_MIGRATION_JSON_PATH = "data/iam"
BK_IAM_MIGRATION_APP_NAME = "apigateway.iam.apigw_iam_migration"
BK_IAM_RESOURCE_API_HOST = env.str("BK_IAM_RESOURCE_API_HOST", DASHBOARD_URL)
# 跳过注册权限模型到权限中心（注意：仅跳过注册权限模型，不关注权限校验是否依赖权限中心）
BK_IAM_SKIP = env.bool("BK_IAM_SKIP", False)
# 使用权限中心数据进行鉴权（创建网关时，会创建分级管理员、用户组，校验权限时依赖权限中心）
# TODO: 待启用 IAM 鉴权时，将默认值改为 True
USE_BK_IAM_PERMISSION = env.bool("USE_BK_IAM_PERMISSION", False)

# 使用 bkmonitorv3 网关 API，还是 monitor_v3 组件 API
USE_BKAPI_BKMONITORV3 = env.bool("USE_BKAPI_BKMONITORV3", False)
# 是否使用 bklog 网关 API
USE_BKAPI_BK_LOG = env.bool("USE_BKAPI_BK_LOG", False)


# ==============================================================================
# Feature Flag
# ==============================================================================
# 全局功能开关，用于控制站点全局性的一些功能，将与 DEFAULT_USER_FEATURE_FLAG、Model UserFeatureFlag 中数据合并
# 优先级：Model UserFeatureFlag > DEFAULT_USER_FEATURE_FLAG > DEFAULT_FEATURE_FLAG
DEFAULT_FEATURE_FLAG = {
    "ENABLE_MONITOR": env.bool("FEATURE_FLAG_ENABLE_MONITOR", False),
    "ENABLE_RUN_DATA": env.bool("FEATURE_FLAG_ENABLE_RUN_DATA", True),
    "ENABLE_RUN_DATA_METRICS": env.bool("FEATURE_FLAG_ENABLE_RUN_DATA_METRICS", True),
    "ALLOW_UPLOAD_SDK_TO_REPOSITORY": env.bool("FEATURE_FLAG_ALLOW_UPLOAD_SDK_TO_REPOSITORY", False),
    "MENU_ITEM_HELP": env.bool("FEATURE_FLAG_MENU_ITEM_HELP", False),
    "MENU_ITEM_ESB_API": env.bool("FEATURE_FLAG_MENU_ITEM_ESB_API", True),
    "MENU_ITEM_ESB_API_DOC": env.bool("FEATURE_FLAG_MENU_ITEM_ESB_API_DOC", True),
    "SYNC_ESB_TO_APIGW_ENABLED": env.bool("FEATURE_FLAG_SYNC_ESB_TO_APIGW_ENABLED", True),
    # api-support
    "ENABLE_SDK": env.bool("FEATURE_FLAG_ENABLE_SDK", False),
    "ALLOW_CREATE_APPCHAT": env.bool("FEATURE_FLAG_ALLOW_CREATE_APPCHAT", False),
    "MENU_ITEM_TOOLS": env.bool("FEATURE_FLAG_MENU_ITEM_TOOLS", False),
    "ENABLE_FEEDBACK": env.bool("FEATURE_FLAG_ENABLE_FEEDBACK", False),
}

# 用户功能开关，将与 DEFAULT_FEATURE_FLAG 合并
DEFAULT_USER_FEATURE_FLAG = {
    "MICRO_GATEWAY_ENABLED": env.bool("FEATURE_FLAG_MICRO_GATEWAY_ENABLED", False),
}

# 具体网关默认功能开关，将与 core.constants 中共享网关、专享网关等功能开关配置合并，
# 支持不同类型的网关，有不同的功能特性集
GLOBAL_GATEWAY_FEATURE_FLAG = {
    "OFFICIAL_API_TIPS_ENABLED": env.bool("OFFICIAL_API_TIPS_ENABLED", True),
    "MICRO_GATEWAY_ENABLED": env.bool("FEATURE_FLAG_MICRO_GATEWAY_ENABLED", False),
    "ACCESS_STRATEGY_ENABLED": env.bool("FEATURE_FLAG_ACCESS_STRATEGY_ENABLED", False),
    "PLUGIN_ENABLED": env.bool("FEATURE_FLAG_PLUGIN_ENABLED", True),
    "STAGE_RATE_LIMIT_ENABLED": env.bool("FEATURE_FLAG_STAGE_RATE_LIMIT_ENABLED", False),
    "RESOURCE_WITH_MOCK_ENABLED": env.bool("FEATURE_FLAG_RESOURCE_WITH_MOCK_ENABLED", False),
    "RESOURCE_DISABLE_STAGE_ENABLED": env.bool("FEATURE_FLAG_RESOURCE_DISABLE_STAGE_ENABLED", False),
    "BACKEND_SERVICE_ENABLED": env.bool("FEATURE_FLAG_BACKEND_SERVICE_ENABLED", False),
}

# ==============================================================================
# 访问日志
# ==============================================================================
ACCESS_LOG_CONFIG = {
    "es_client_type": env.str("BK_APIGW_ES_CLIENT_TYPE", "bk_log"),
    "es_time_field_name": env.str("BK_APIGW_ES_TIME_FIELD_NAME", "dtEventTimeStamp"),
    "es_index": env.str("BK_APIGW_API_LOG_ES_INDEX", "2_bklog_bkapigateway_apigateway_container*"),
}

BK_ESB_ACCESS_LOG_CONFIG = {
    "es_client_type": env.str("BK_ESB_ES_CLIENT_TYPE", "bk_log"),
    "es_time_field_name": env.str("BK_ESB_ES_TIME_FIELD_NAME", "dtEventTimeStamp"),
    "es_index": env.str("BK_ESB_API_LOG_ES_INDEX", "2_bklog_bkapigateway_esb_container*"),
}

# ==============================================================================
# ESB 配置
# ==============================================================================
ESB_DEFAULT_BOARD = "default"

ESB_MANAGERS = env.list("ESB_MANAGERS", default=APIGW_MANAGERS)

# ESB 组件对应网关的名称
BK_ESB_GATEWAY_NAME = "bk-esb"

# 用户类型配置
USER_AUTH_TYPE_CONFIGS = {
    "default": {
        "boards": [
            "default",
        ],
    },
}

# 将 esb 的 jwt 密钥同步到指定名称的网关
SYNC_ESB_JWT_KEY_GATEWAY_NAMES = {
    BK_ESB_GATEWAY_NAME: {
        "description": "蓝鲸 ESB 编码组件",
        "description_en": "ESB Coding Component",
        "is_public": False,
    },
    "apigw": {
        "description": "蓝鲸 ESB 占位网关",
        "description_en": "ESB placeholder gateway",
        "is_public": False,
    },
}

ESB_BOARD_CONFIGS = {
    "default": {
        "name": "default",
        "label": gettext("蓝鲸智云"),
        # envs
        "api_envs": [
            {
                "name": "prod",
                "label": gettext("正式环境"),
                "host": env.str("ESB_DEFAULT_BOARD_PROD_URL", "") or BK_COMPONENT_API_URL,
                "description": gettext("访问后端正式环境"),
            },
            {
                "name": "test",
                "label": gettext("测试环境"),
                "host": env.str("ESB_DEFAULT_BOARD_TEST_URL", ""),
                "description": gettext("访问后端测试环境"),
            },
        ],
        # sdk
        "has_sdk": env.bool("ESB_DEFAULT_BOARD_HAS_SDK", True),
        "sdk_name": "bkapi-component-open",
        "sdk_package_prefix": "bkapi_component.open",
        "sdk_doc_templates": {
            "python_sdk_usage_example": "python_sdk_usage_example_v2.md",
        },
        "sdk_description": gettext("访问蓝鲸智云组件 API"),
    },
}
