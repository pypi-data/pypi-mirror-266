import React from "react";
import { parametrize } from "react-overridable";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
} from "@js/oarepo_ui";
// TODO: if we wish to import some things from invenio we need to resolve translations
// in their system
import { CommunitiesEmptySearchResults } from "@js/invenio_communities/community";
import PropTypes from "prop-types";
import { ComputerTabledCommunitiesListItem } from "./ComputerTabletCommunitiesListItem";
import { MobileCommunitiesListItem } from "./MobileCommunitiesListItem";
import {
  UserDashboardSearchAppLayoutHOC,
  UserDashboardSearchAppResultView,
} from "@js/dashboard_components";
import { i18next } from "@translations/oarepo_dashboard";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

export const UserDashboardCommunitiesListItem = ({
  result,
  communityTypeLabelTransparent,
}) => {
  const isRestricted = result?.access?.visibility === "restricted";
  return (
    <React.Fragment>
      <ComputerTabledCommunitiesListItem
        result={result}
        communityTypeLabelTransparent={communityTypeLabelTransparent}
        isRestricted={isRestricted}
      />
      <MobileCommunitiesListItem
        result={result}
        communityTypeLabelTransparent={communityTypeLabelTransparent}
        isRestricted={isRestricted}
      />
    </React.Fragment>
  );
};

UserDashboardCommunitiesListItem.propTypes = {
  result: PropTypes.object.isRequired,
  communityTypeLabelTransparent: PropTypes.bool,
};

UserDashboardCommunitiesListItem.defaultProps = {
  communityTypeLabelTransparent: false,
};

const UserDashboardSearchAppResultViewWAppName = parametrize(
  UserDashboardSearchAppResultView,
  {
    appName: overridableIdPrefix,
  }
);
export const DashboardUploadsSearchLayout = UserDashboardSearchAppLayoutHOC({
  placeholder: i18next.t("Search in my communities..."),
  appName: overridableIdPrefix,
});
export const componentOverrides = {
  [`${overridableIdPrefix}.EmptyResults.element`]:
    CommunitiesEmptySearchResults,
  [`${overridableIdPrefix}.ResultsList.item`]: UserDashboardCommunitiesListItem,
  // [`${overridableIdPrefix}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${overridableIdPrefix}.SearchApp.results`]:
    UserDashboardSearchAppResultViewWAppName,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,
};

createSearchAppsInit({ componentOverrides });
