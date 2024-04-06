from oarepo_ui.resources.components import UIResourceComponent


class DashboardRequestsSearchComponent(UIResourceComponent):
    def before_ui_search(self, *, search_options, view_args, **kwargs):
        search_options["initial_filters"] = [["is_open", "true"], ["mine", "true"]]
