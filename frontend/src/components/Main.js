import React from 'react';
import { Switch, Route } from 'react-router-dom';
import IssueList from "./IssueList";
import SeriesList from "./SeriesList";

const Main = () => (
  <main>
    <Switch>
      <Route exact path="/series" component={SeriesList}/>
      <Route path="/issue" component={IssueList}/>
    </Switch>
  </main>
)

export default Main
