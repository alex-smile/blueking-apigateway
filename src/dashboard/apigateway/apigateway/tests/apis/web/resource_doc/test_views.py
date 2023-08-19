import json

from apigateway.apps.support.constants import DocLanguageEnum
from apigateway.biz.resource_doc.import_doc.models import ArchiveDoc


class TestResourceDocListCreateApi:
    def test_list(self, request_view, fake_resource_doc):
        fake_gateway = fake_resource_doc.api

        resp = request_view(
            method="GET",
            view_name="resource_doc.list_create",
            path_params={"gateway_id": fake_gateway.id, "resource_id": fake_resource_doc.resource_id},
        )
        result = resp.json()

        assert resp.status_code == 200
        assert len(result["data"]) == 2

    def test_create(self, request_view, fake_resource, faker):
        fake_gateway = fake_resource.api

        resp = request_view(
            method="POST",
            view_name="resource_doc.list_create",
            path_params={"gateway_id": fake_gateway.id, "resource_id": fake_resource.id},
            data={
                "language": "zh",
                "content": faker.pystr(),
            },
        )
        result = resp.json()

        assert resp.status_code == 201
        assert result["data"]["id"] != 0


class TestResourceDocUpdateDestroyApi:
    def test_update(self, request_view, fake_resource_doc, faker):
        fake_gateway = fake_resource_doc.api

        resp = request_view(
            method="PUT",
            view_name="resource_doc.update_destroy",
            path_params={
                "gateway_id": fake_gateway.id,
                "resource_id": fake_resource_doc.resource_id,
                "id": fake_resource_doc.id,
            },
            data={
                "language": "zh",
                "content": faker.pystr(),
            },
        )
        assert resp.status_code == 200

    def test_destroy(self, request_view, fake_resource_doc):
        fake_gateway = fake_resource_doc.api

        resp = request_view(
            method="DELETE",
            view_name="resource_doc.update_destroy",
            path_params={
                "gateway_id": fake_gateway.id,
                "resource_id": fake_resource_doc.resource_id,
                "id": fake_resource_doc.id,
            },
        )
        assert resp.status_code == 204


class TestResourceDocArchiveParseApi:
    def test_post(self, request_view, fake_gateway, mocker, faker, fake_tgz_file):
        mocker.patch(
            "apigateway.apis.web.resource_doc.views.ArchiveParser.parse",
            return_value=[
                ArchiveDoc(
                    resource_name=faker.pystr(),
                    language=DocLanguageEnum.ZH,
                    content=faker.pystr(),
                    content_changed=True,
                    filename=faker.pystr(),
                )
            ],
        )

        resp = request_view(
            method="POST",
            view_name="resource_doc.archive.parse",
            path_params={"gateway_id": fake_gateway.id},
            data={
                "file": fake_tgz_file,
            },
            format="multipart",
        )

        assert resp.status_code == 200


class TestResourceDocImportByArchiveApi:
    def post(self, request_view, fake_gateway, mocker, faker, fake_tgz_file):
        mocker.patch("apigateway.apis.web.resource_doc.views.ArchiveParser.parse", return_value=[])
        mocker.patch("apigateway.apis.web.resource_doc.views.ResourceDocImporter.import_docs")

        resp = request_view(
            method="POST",
            view_name="resource_doc.import.by_archive",
            path_params={"gateway_id": fake_gateway.id},
            data={
                "selected_resource_docs": json.dumps(
                    [
                        {
                            "language": "zh",
                            "resource_name": faker.pystr(),
                        }
                    ]
                ),
                "file": fake_tgz_file,
            },
            format="multipart",
        )

        assert resp.status_code == 200


class TestResourceDocImportBySwaggerApi:
    def test_post(self, request_view, fake_gateway, mocker, faker):
        mocker.patch("apigateway.apis.web.resource_doc.views.SwaggerParser.parse", return_value=[])
        mocker.patch("apigateway.apis.web.resource_doc.views.ResourceDocImporter.import_docs")

        resp = request_view(
            method="POST",
            view_name="resource_doc.import.by_swagger",
            path_params={"gateway_id": fake_gateway.id},
            data={
                "selected_resource_docs": [
                    {
                        "language": "zh",
                        "resource_name": "get_user",
                    }
                ],
                "swagger": faker.pystr(),
                "language": "zh",
            },
        )

        assert resp.status_code == 200


class TestResourceDocExportApi:
    def test_post(self, request_view, fake_resource_doc):
        fake_gateway = fake_resource_doc

        resp = request_view(
            method="POST",
            view_name="resource_doc.export",
            path_params={"gateway_id": fake_gateway.id},
            data={
                "export_type": "all",
                "file_type": "tgz",
            },
        )

        assert resp.status_code == 200
