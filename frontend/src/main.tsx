import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import LandingPage from "./LandingPage";
import "./index.css";

const isLandingRoute = window.location.pathname.startsWith("/landing");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {isLandingRoute ? <LandingPage /> : <App />}
  </React.StrictMode>
);
