import React, { createContext, useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { NeedleThemeProvider, Logo } from '@neo4j-ndl/react';
import './App.css';
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';

export const AppContext = createContext();

function App() {
    const [settings, setSettings] = useState({
        selectedLLM: 'GPT-4 8k',
        temperature: 0.7,
        useGrounding: true,
        contextDocuments: 10,
    });

    return (
        <NeedleThemeProvider theme="dark">
            <AppContext.Provider value={{ settings, setSettings }}>
                <div className="app flex">
                    <Sidebar />
                    <div className="flex flex-col justify-center items-center">
                        {/* Example usage of Logo, assuming you want it at the top of your sidebar or app */}
                        <div className="app-title flex justify-center items-center p-4">
                            <Logo color="white" type="full" className="n-w-24" />
                            <h1 className="text-white text-2xl font-bold ml-4">Agent-Neo</h1>
                        </div>
                        <ChatInterface />
                    </div>
                </div>
            </AppContext.Provider>
        </NeedleThemeProvider>
    );
}

export default App;
