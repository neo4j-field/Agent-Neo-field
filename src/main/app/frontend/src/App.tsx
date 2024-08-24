import React, { createContext, useEffect, useState } from 'react';
import { useMediaQuery } from 'react-responsive'
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'; // Use BrowserRouter and import Switch
import Callback from "./auth/callback";
import HomePage from "./HomePage"; // Make sure this path is correct
import PrivateRoute from "./auth/privateRoute"; // Make sure this path is correct
import { NeedleThemeProvider } from '@neo4j-ndl/react';
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import { Settings, AppContextType, GraphData } from './types/types';
import { getDynamicConfigValue } from './auth/dynamicConfig';
import auth from './auth/auth';
import { v4 as uuidv4 } from 'uuid';



const defaultGraphData: GraphData = {
  nodes: []
};


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
  graphData: defaultGraphData,
  setGraphData: () => {},
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
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const toggleTheme = () => setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));
    const [appIsInitialized, setAppIsInitialized] = useState<boolean>(false);
    const [conversationId] = useState<string>(() => `conv-${uuidv4()}`);

    useEffect(() => {
        const initializeApp = async() => {
            const authMethod = getDynamicConfigValue("AUTH_METHOD");

            if(authMethod === "auth0"){
                const pathname = window.location.pathname;

                //skip initialization if we are on callback
                if(pathname === "/callback"){
                    return;
                }

                try {
                    localStorage.setItem("path", pathname);

                    await auth.silentAuth();
                } catch (err:unknown){
                    const error = err as { message?: string; error?: string }; // Type assertion

                    if(error.error === "login_required" || error.message === "login_required") {
                        auth.login();
                        return;
                    }
                    else {
                        console.error(' Authentication error:', error );
                        alert('An unknown error occured. Please check the console for details');
                    }
                }
                finally {
                    setAppIsInitialized(true)
                }

            }
            else {
                setAppIsInitialized(true);
            }
        };

        initializeApp().catch(error => {
        console.error("Failed to initialize app:", error);
        });
    }, []);

    //console.log(`window.location.pathname: ${window.location.pathname}`);
    return (
        <NeedleThemeProvider theme={theme} wrapperProps={{ isWrappingChildren: false }}>
            <AppContext.Provider value={{ settings, setSettings, toggleTheme, theme, graphData, setGraphData }}>
                <Router>
                    <Routes>
                        <Route path="/callback" element={<Callback />} />
                        <Route path="/" element={
                            <PrivateRoute
                                appIsInitialized={appIsInitialized}
                                element={<HomePage conversationId={conversationId} />}
                            />
                        } />
                    </Routes>
                </Router>
            </AppContext.Provider>
        </NeedleThemeProvider>
    );
}


export default App