import React from 'react';
import { Navigate } from 'react-router-dom';
import auth from "./auth";

interface PrivateRouteProps {
    element: React.ReactElement;
    appIsInitialized: boolean;
}

const PrivateRoute = ({ element, appIsInitialized }: PrivateRouteProps): React.ReactElement => {
    if (!appIsInitialized || !auth.isAuthenticated()) {
        // Correctly using Navigate to handle unauthenticated or uninitialized app state
        console.log('starting private route redirect')
        return <Navigate to="/" replace />;
    }
    console.log("private route called")
    return element;
};

export default PrivateRoute;
