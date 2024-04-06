import React from "react";
import { Grid, Button } from "semantic-ui-react";
import { parametrize } from "react-overridable";
import { i18next } from "@translations/oarepo_dashboard";
import {
  UserDashboardSearchAppLayoutHOC,
  UserDashboardSearchAppResultView,
} from "@js/dashboard_components";
import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchappSearchbarElement,
  DynamicResultsListItem,
} from "@js/oarepo_ui";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

// TODO: currently, we don't support multiple models, so create new
// can be just a regular button, not a dropdown with options
// to be revisited
// const schemesList = [
//   {
//     key: "docs",
//     text: <a href="/docs/_new">New doc</a>,
//     value: "docs",
//     // major hack for first item in dropdown being automatically highlighted :0
//     selected: false,
//     active: false,
//   },
//   {
//     key: "communities",
//     text: <a href="/communities/new">New comm</a>,
//     value: "communities",
//   },
// ];

const UserDashboardSearchAppResultViewWAppName = parametrize(
  UserDashboardSearchAppResultView,
  {
    appName: overridableIdPrefix,
  }
);

const ExtraContent = () => (
  <Grid.Column textAlign="right">
    <Button
      as="a"
      href="/docs/_new"
      type="button"
      labelPosition="left"
      icon="plus"
      content={i18next.t("Create new draft")}
      primary
    />
    {/* <Dropdown
      button
      className="icon primary tiny"
      placeholder="Choose an option"
      labeled
      icon="plus"
      options={[]}
      text={i18next.t("Create new...")}
    /> */}
  </Grid.Column>
);
export const DashboardUploadsSearchLayout = UserDashboardSearchAppLayoutHOC({
  placeholder: i18next.t("Search in my uploads..."),
  extraContent: ExtraContent,
  appName: overridableIdPrefix,
});
export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: DynamicResultsListItem,
  [`${overridableIdPrefix}.SearchBar.element`]: SearchappSearchbarElement,
  // [`${overridableIdPrefix}.SearchApp.facets`]: ContribSearchAppFacetsWithConfig,
  [`${overridableIdPrefix}.SearchApp.results`]:
    UserDashboardSearchAppResultViewWAppName,
  [`${overridableIdPrefix}.SearchApp.layout`]: DashboardUploadsSearchLayout,
};

createSearchAppsInit({ componentOverrides });
