import React, { createContext, useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterfaceStarterKit from './components/ChatInterfaceStarterKit';
import ChatInterface from './components/ChatInterface';
import { NeedleThemeProvider, Logo, Typography } from '@neo4j-ndl/react';
//import './App.css';  not needed anymore
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';

export const AppContext = createContext();
const theme = 'dark'; //Ideally you would have a toggle on screen to let the user update the theme mode

function App() {
    const [settings, setSettings] = useState({
        selectedLLM: 'GPT-4 8k',
        temperature: 0.7,
        useGrounding: true,
        contextDocuments: 10,
    });

    return (
        <NeedleThemeProvider theme={theme} wrapperProps={{ isWrappingChildren: false }}>
            <AppContext.Provider value={{ settings, setSettings }}>
                <div className={`flex ${theme === 'dark' ? 'ndl-theme-dark' : 'ndl-theme-light'} n-bg-palette-neutral-bg-weak`}>
                    <Sidebar />
                    <div className="flex w-full flex-col justify-center items-center">
                        <section className="flex justify-center items-center p-4">
                            <Logo color="white" type="full" className="h-8 min-h-12 min-w-32" />
                            <Typography variant="h2" className="ml-4">Agent-Neo</Typography>
                        </section>
                        {/* Uncomment for the same chat visual you had */}
                        {/* <ChatInterface />  */}
                        
                        {/* Uncomment for the chatbot from Needle starter kit */}
                        <ChatInterfaceStarterKit />
                    </div>
                </div>
            </AppContext.Provider>
        </NeedleThemeProvider>
    );
}

export default App;
