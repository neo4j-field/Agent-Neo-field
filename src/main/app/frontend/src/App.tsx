import React, { createContext, useState } from 'react';
import Sidebar from './components/SideBar';
import ChatInterfaceStarterKit from './components/ChatInterfaceStartKit';
import { NeedleThemeProvider, Logo, Typography, useMediaQuery } from '@neo4j-ndl/react';
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import { Settings, AppContextType, GraphData } from './types/types';




export const AppContext = createContext<AppContextType | null>(null);



function App() {

    const [settings, setSettings] = useState<Settings>({
        selectedLLM: 'GPT-4 8k',
        temperature: 0.7,
        useGrounding: true,
        contextDocuments: 10,
    });

    const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
    const [theme, setTheme] = useState<'light' | 'dark'>(prefersDarkMode ? 'dark' : 'light');
    const [graphData, setGraphData] = useState<GraphData | null>(null);


    const toggleTheme = () => setTheme((prevTheme) => (prevTheme === 'dark' ? 'light' : 'dark'));



    return (
        <NeedleThemeProvider theme={theme} wrapperProps={{ isWrappingChildren: false }}>
            <AppContext.Provider value={{ settings, setSettings, toggleTheme, theme, graphData, setGraphData }}>
                <div className={`flex ${theme === 'dark' ? 'ndl-theme-dark' : 'ndl-theme-light'} n-bg-palette-neutral-bg-weak`}>
                    <Sidebar />
                    <div className="flex w-full flex-col justify-center items-center">
                        <section className="flex justify-center items-center p-4">
                            <Logo color="white" type="full" className="h-8 min-h-12 min-w-32" />
                            <Typography variant="h2" className="ml-4">Agent-Neo</Typography>
                        </section>
                        <ChatInterfaceStarterKit />
                    </div>
                </div>
            </AppContext.Provider>
        </NeedleThemeProvider>
    );
}
