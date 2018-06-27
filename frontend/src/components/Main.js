import React from 'react';
import { Switch, Route } from 'react-router-dom';
import IssueList from "./IssueList";
import SeriesList from "./SeriesList";
import PublisherList from "./PublisherList";
import PublisherSeriesList from "./PublisherSeriesList";

const Main = () => (
  <main>
    <Switch>
      <Route exact path="/series" component={SeriesList} />
      <Route path="/series/:id" component={IssueList} />
      <Route exact path="/publisher" component={PublisherList} />
      <Route path="/publisher/:id" component={PublisherSeriesList} />
    </Switch>
  </main>
)

export default Main
