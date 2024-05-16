import React, { createContext, useEffect, useState } from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'; // Use BrowserRouter and import Switch
import Callback from "./auth/callback";
import HomePage from "./HomePage"; // Make sure this path is correct
import PrivateRoute from "./auth/privateRoute"; // Make sure this path is correct
import { NeedleThemeProvider, Logo, Typography } from '@neo4j-ndl/react';
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import { Settings, AppContextType } from './types/types'; // Ensure these are correct
import { getDynamicConfigValue } from './auth/dynamicConfig';
import auth from './auth/auth';

//A default App context.
const defaultAppContextValue: AppContextType = {
  settings: {
    selectedLLM: 'GPT-4 8k',
    temperature: 0.7,
    useGrounding: true,
    contextDocuments: 10,
  },
  setSettings: () => {},
  toggleTheme: () => {},
  theme: 'dark',
};


export const AppContext = createContext<AppContextType>(defaultAppContextValue);


function App() {
    const [settings, setSettings] = useState<Settings>({
        selectedLLM: 'GPT-4 8k',
        temperature: 0.7,
        useGrounding: true,
        contextDocuments: 10,
    });

    const [theme, setTheme] = useState<'light' | 'dark'>('dark');
    const toggleTheme = () => setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');

    const [appIsInitialized, setAppIsInitialized] = useState<boolean>(false);

    useEffect(() => {
        const initializeApp = async () => {
            if(getDynamicConfigValue("REACT_APP_AUTH_METHOD") === "auth0") {
                const pathname = window.location.pathname;
                if(pathname === "/callback"){
                    return;
                }

                try {
                    localStorage.setItem("path", pathname);
                    await auth.silentAuth();
                    setAppIsInitialized(true);
                } catch(err: unknown) {
                    const error = err as { message?: string, error?: string }; // Type assertion
                    if(error.error === "login_required" || error.message === "login_required") {
                        auth.login();
                    }
                    else {
                        console.error('Authentication error: ', error);
                        alert('An unknown error occurred. Please check the console for details.');
                    }
                }
            }
        };

        initializeApp().catch(error => {
            console.error("Failed to initialize app:", error);
        });

    }, []);

    //console.log(`window.location.pathname: ${window.location.pathname}`);
    return (
        <NeedleThemeProvider theme={theme} wrapperProps={{ isWrappingChildren: false }}>
            <AppContext.Provider value={{ settings, setSettings, toggleTheme, theme }}>
                <Router>
                    <Routes>
                        <Route path="/callback" element={<Callback />} />
                        <Route path="/" element={
                            <PrivateRoute
                                appIsInitialized={appIsInitialized}
                                element={<HomePage />}
                            />
                        } />
                    </Routes>
                </Router>
            </AppContext.Provider>
        </NeedleThemeProvider>
    );
}

export default App;
