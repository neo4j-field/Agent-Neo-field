import React from "react";
import {Route, Navigate, RouteProps} from "react-router-dom";
import auth from "./auth";

interface PrivateRouteProps {
  path: string;
  exact?: boolean;
  element: React.ReactElement;
  appIsInitialized: boolean;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({
  path,
  element: Element,
  appIsInitialized,
  exact = true,
}) => (
  <Route
    path={path}
    exact = {exact}
    render={(props:any) =>
      !appIsInitialized || !auth.isAuthenticated() ? (
        <Navigate to="/login" replace />
      ) : (
        <Element {...props} />
      )
    }
  />
);

export default PrivateRoute;
