from django.contrib import admin

from data_browser.common import global_state
from data_browser.orm_admin import get_models
from tests.core.admin import AddressAdmin
from tests.core.admin import ProductAdmin
from tests.core.models import Address
from tests.core.models import Producer
from tests.core.models import Product


class TestAdminMixin:
    def test_annotation_loaded_on_detail(self, admin_client, mocker):
        get_queryset = mocker.patch(
            "tests.core.admin.AddressAdmin.andrew.get_queryset",
            wraps=AddressAdmin.andrew.get_queryset,
        )
        a = Address.objects.create()
        assert (
            admin_client.get(f"/admin/core/address/{a.pk}/change/").status_code == 200
        )
        get_queryset.assert_called_once()

    def test_annotation_loaded_unnecessarily_on_detail(self, admin_client, mocker):
        get_queryset = mocker.patch(
            "tests.core.admin.ProductAdmin.annotated.get_queryset",
            wraps=ProductAdmin.annotated.get_queryset,
        )
        p = Product.objects.create(producer=Producer.objects.create())
        assert (
            admin_client.get(f"/admin/core/product/{p.pk}/change/").status_code == 200
        )
        get_queryset.assert_called_once()

    def test_annotation_loaded_on_list(self, admin_client, mocker):
        get_queryset = mocker.patch(
            "tests.core.admin.ProductAdmin.annotated.get_queryset",
            wraps=ProductAdmin.annotated.get_queryset,
        )
        assert admin_client.get("/admin/core/product/").status_code == 200
        get_queryset.assert_called_once()

    def test_annotation_not_loaded_on_list(self, admin_client, mocker):
        get_queryset = mocker.patch(
            "tests.core.admin.AddressAdmin.andrew.get_queryset",
            wraps=AddressAdmin.andrew.get_queryset,
        )
        assert admin_client.get("/admin/core/address/").status_code == 200
        get_queryset.assert_not_called()

    def test_request_factory_compability_list(self, rf, admin_user, mocker):
        request = rf.get("/")
        request.user = admin_user
        get_queryset = mocker.patch(
            "tests.core.admin.AddressAdmin.andrew.get_queryset",
            wraps=AddressAdmin.andrew.get_queryset,
        )
        resp = AddressAdmin(Address, admin.site).changelist_view(request)
        assert resp.status_code == 200
        get_queryset.assert_called_once()

    def test_request_factory_compability_detail(self, rf, admin_user, mocker):
        address = Address.objects.create()
        request = rf.get("/")
        request.user = admin_user
        get_queryset = mocker.patch(
            "tests.core.admin.AddressAdmin.andrew.get_queryset",
            wraps=AddressAdmin.andrew.get_queryset,
        )
        resp = AddressAdmin(Address, admin.site).changeform_view(
            request, str(address.pk)
        )
        assert resp.status_code == 200
        get_queryset.assert_called_once()

    def test_ddb_url(self, admin_client):
        resp = admin_client.get("/admin/core/product/")
        assert resp.status_code == 200
        expected = (
            "/data_browser/query/core.Product/.html"
            "?a_field__a_lookup=a_value"
            "&name__not_equals=not+a+thing"
            "&a_field__a_lookup=true"
        )
        assert resp.context["ddb_url"] == expected

    def test_ddb_url_ignored(self, admin_client):
        resp = admin_client.get("/admin/core/ignored/")
        assert resp.status_code == 200
        assert "ddb_url" not in resp.context


def test_admin_options_setting(admin_ddb_request, settings):
    assert "core.InAdmin" in get_models(global_state.request)
    settings.DATA_BROWSER_ADMIN_OPTIONS = {"tests.core.admin.InAdmin": {"ignore": True}}
    assert "core.InAdmin" not in get_models(global_state.request)
