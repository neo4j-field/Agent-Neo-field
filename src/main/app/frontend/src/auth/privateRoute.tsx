import React from 'react';
import { Navigate } from 'react-router-dom';
import auth from "./auth";

interface PrivateRouteProps {
    element: React.ReactElement;
    appIsInitialized: boolean;
}

const PrivateRoute = ({ element, appIsInitialized }: PrivateRouteProps): React.ReactElement => {
    if (!appIsInitialized || !auth.isAuthenticated()) {
        return <Navigate to="/" replace />;
    }
    return element;
};

export default PrivateRoute;
