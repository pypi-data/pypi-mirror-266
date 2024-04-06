from oarepo_ui.resources.config import (
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.resource import RecordsUIResource
from flask_menu import current_menu
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_dashboard.ui.dashboard_components.search import (
    DashboardRequestsSearchComponent,
)


class DashboardRequestsUIResourceConfig(RecordsUIResourceConfig):
    url_prefix = "/me/requests/"
    blueprint_name = "requests_dashboard"
    template_folder = "templates"
    application_id = "requests_dashboard"
    templates = {
        "search": "DashboardRequestsPage",
    }

    routes = {
        "create": "/dummy-route",
        "edit": "/dummy-route",
        "search": "/",
        "detail": "/dummy-route",
        "export": "/dummy-route",
    }
    api_service = "requests"

    components = [
        DashboardRequestsSearchComponent,
    ]

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return "/api/requests/"


class DashboardRequestsUIResource(RecordsUIResource):
    pass


def create_blueprint(app):
    """Register blueprint for this resource."""
    app_blueprint = DashboardRequestsUIResource(
        DashboardRequestsUIResourceConfig()
    ).as_blueprint()

    @app_blueprint.before_app_first_request
    def init_menu():
        user_dashboard = current_menu.submenu("user_dashboard")
        user_dashboard.submenu("requests").register(
            "requests_dashboard.search",
            text=_("Requests"),
            order=3,
        )

    return app_blueprint
