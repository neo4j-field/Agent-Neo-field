import React from "react";
import { Navigate } from "react-router-dom";
import auth from "./auth"; // Adjust this import to your actual path

interface PrivateRouteProps {
  element: React.ReactElement;
  appIsInitialized: boolean;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({
  element,
  appIsInitialized,
}) => {
  if (!appIsInitialized || !auth.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return element;
};

export default PrivateRoute;
