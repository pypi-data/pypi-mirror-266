// This file is part of InvenioRDM
// Copyright (C) 2020-2022 CERN.
// Copyright (C) 2020-2021 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2021 New York University.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import {
  SearchAppResultsPane,
  SearchConfigurationContext,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/oarepo_dashboard";
import React, { useContext } from "react";
import { SearchBar, ActiveFilters } from "react-searchkit";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { Grid, Button, Container } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  SearchAppFacets,
  ClearFiltersButton,
  ShouldActiveFiltersRender,
} from "@js/oarepo_ui";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Overridable from "react-overridable";

const queryClient = new QueryClient();

export const UserDashboardSearchAppLayoutHOC = ({
  placeholder,
  extraContent,
  mobileOnlyExtraRow,
  appName,
}) => {
  const DashboardUploadsSearchLayout = (props) => {
    const [sidebarVisible, setSidebarVisible] = React.useState(false);
    const { config } = props;
    const searchAppContext = useContext(SearchConfigurationContext);
    const { buildUID } = searchAppContext;
    return (
      <QueryClientProvider client={queryClient}>
        <Container className="rel-mt-4 rel-mb-4">
          <Grid>
            <GridResponsiveSidebarColumn
              width={3}
              open={sidebarVisible}
              onHideClick={() => setSidebarVisible(false)}
            >
              <SearchAppFacets aggs={config.aggs} appName={appName} />
            </GridResponsiveSidebarColumn>
            <Grid.Column computer={13} mobile={16} tablet={16}>
              <Grid columns="equal">
                <ShouldActiveFiltersRender>
                  <Grid.Row only="computer" verticalAlign="middle">
                    <Grid.Column>
                      <ActiveFilters />
                      <Overridable
                        id={buildUID("ClearFiltersButton.container")}
                      >
                        <ClearFiltersButton />
                      </Overridable>
                    </Grid.Column>
                  </Grid.Row>
                </ShouldActiveFiltersRender>
                <Grid.Row only="computer" verticalAlign="middle">
                  <Grid.Column>
                    <SearchBar placeholder={placeholder} className="rel-pl-1" />
                  </Grid.Column>
                  {extraContent && extraContent()}
                </Grid.Row>
                <Grid.Column only="mobile tablet" mobile={2} tablet={2}>
                  <Button
                    basic
                    icon="sliders"
                    onClick={() => setSidebarVisible(true)}
                    aria-label={i18next.t("Filter results")}
                  />
                </Grid.Column>
                <Grid.Column
                  only="mobile tablet"
                  mobile={14}
                  tablet={14}
                  floated="right"
                >
                  <SearchBar placeholder={placeholder} />
                </Grid.Column>
                {extraContent && (
                  <Grid.Row only="tablet mobile" verticalAlign="middle">
                    {extraContent()}
                  </Grid.Row>
                )}
                {mobileOnlyExtraRow && (
                  <Grid.Row verticalAlign="middle" only="mobile">
                    {mobileOnlyExtraRow()}
                  </Grid.Row>
                )}
                <ShouldActiveFiltersRender>
                  <Grid.Row only="mobile tablet">
                    <Grid.Column>
                      <Overridable
                        id={buildUID("ClearFiltersButton.container")}
                      >
                        <ClearFiltersButton />
                      </Overridable>
                    </Grid.Column>
                  </Grid.Row>
                </ShouldActiveFiltersRender>
                <Grid.Row>
                  <Grid.Column mobile={16} tablet={16} computer={16}>
                    <SearchAppResultsPane
                      layoutOptions={config.layoutOptions}
                      appName={appName}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Grid.Column>
          </Grid>
        </Container>
      </QueryClientProvider>
    );
  };

  DashboardUploadsSearchLayout.propTypes = {
    config: PropTypes.object.isRequired,
  };

  return DashboardUploadsSearchLayout;
};

UserDashboardSearchAppLayoutHOC.propTypes = {
  placeholder: PropTypes.string,
  extraContent: PropTypes.oneOfType([PropTypes.func, PropTypes.oneOf([null])]),
  mobileOnlyExtraRow: PropTypes.oneOfType([
    PropTypes.func,
    PropTypes.oneOf([null]),
  ]),
  appName: PropTypes.string,
};

UserDashboardSearchAppLayoutHOC.defaultProps = {
  extraContent: null,
  mobileOnlyExtraRow: null,
  appName: undefined,
  placeholder: "",
};
