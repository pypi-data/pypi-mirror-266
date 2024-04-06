import React from "react";
import { Grid } from "semantic-ui-react";
import { parametrize } from "react-overridable";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  ActiveFiltersElement,
  ClearFiltersButton,
} from "@js/oarepo_ui";
import { withState } from "react-searchkit";
import {
  RequestsEmptyResultsWithState,
  RequestStatusFilter,
} from "@js/invenio_requests/search";
import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { PropTypes } from "prop-types";
import {
  UserDashboardSearchAppLayoutHOC,
  UserDashboardSearchAppResultView,
  FacetsButtonGroupNameToggler,
} from "@js/dashboard_components";
import { i18next } from "@translations/oarepo_dashboard";
import { ComputerTabletRequestsListItem } from "./ComputerTabletRequestsListItem";
import { MobileRequestsListItem } from "./MobileRequestsListItem";
import { requestTypeSpecificComponents } from "./RequestTypeSpecificComponents";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export function RequestsResultsItemTemplateDashboard({ result }) {
  const ComputerTabletRequestsItemWithState = withState(
    ComputerTabletRequestsListItem
  );
  const MobileRequestsItemWithState = withState(MobileRequestsListItem);
  const detailPageUrl = `/docs/${result?.topic?.reference?.documents}`;
  return (
    <>
      <ComputerTabletRequestsItemWithState
        result={result}
        detailsURL={detailPageUrl}
      />
      <MobileRequestsItemWithState result={result} detailsURL={detailPageUrl} />
    </>
  );
}

RequestsResultsItemTemplateDashboard.propTypes = {
  result: PropTypes.object.isRequired,
};
export const FacetButtons = () => (
  <React.Fragment>
    <Grid.Column only="computer" textAlign="right">
      <RequestStatusFilter keepFiltersOnUpdate />
      <span className="rel-ml-2"></span>
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("My"), filterName: "mine" },
          { text: i18next.t("Others"), filterName: "assigned" },
        ]}
      />
    </Grid.Column>
    <Grid.Column only="mobile tablet" textAlign="left">
      <RequestStatusFilter keepFiltersOnUpdate />
    </Grid.Column>
    <Grid.Column only="mobile tablet" textAlign="right">
      <FacetsButtonGroupNameToggler
        basic
        toggledFilters={[
          { text: i18next.t("My"), filterName: "mine" },
          { text: i18next.t("Others"), filterName: "assigned" },
        ]}
      />
    </Grid.Column>
  </React.Fragment>
);

const UserDashboardSearchAppResultViewWAppName = parametrize(
  UserDashboardSearchAppResultView,
  {
    appName: overridableIdPrefix,
  }
);

const ActiveFiltersElementWIgnoredFilters = parametrize(ActiveFiltersElement, {
  ignoredFilters: ["mine", "assigned"],
});
const ClearFiltersButtonWIgnoredFilters = parametrize(ClearFiltersButton, {
  ignoredFilters: ["mine", "assigned"],
});
export const DashboardUploadsSearchLayout = UserDashboardSearchAppLayoutHOC({
  placeholder: i18next.t("Search in my requests..."),
  extraContent: FacetButtons,
  appName: overridableIdPrefix,
});
export const componentOverrides = {
  [`${overridableIdPrefix}.EmptyResults.element`]:
    RequestsEmptyResultsWithState,
  [`${overridableIdPrefix}.ResultsList.item`]:
    RequestsResultsItemTemplateDashboard,
  [`${overridableIdPrefix}.ActiveFilters.element`]:
    ActiveFiltersElementWIgnoredFilters,
  [`${overridableIdPrefix}.ClearFiltersButton.container`]:
    ClearFiltersButtonWIgnoredFilters,
  [`${overridableIdPrefix}.SearchApp.results`]:
    UserDashboardSearchAppResultViewWAppName,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,
  // from invenio requests in case we have some overlapping request types
  ...defaultContribComponents,
  // our request type specific components (icons, labels, etc.)
  ...requestTypeSpecificComponents,
};

createSearchAppsInit({ componentOverrides });
