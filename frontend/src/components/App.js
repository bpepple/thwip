import React from "react";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import SeriesListCard from "./SeriesListCard";

const App = () => (
  <DataProvider endpoint="api/series/"
                render={data => <SeriesListCard data={data} />} />
);

const wrapper = document.getElementById("app");

wrapper ? ReactDOM.render(<App />, wrapper) : null;
