import { createContext, useState } from 'react';
import HomePage from "./HomePage"; // Make sure this path is correct
import { NeedleThemeProvider } from '@neo4j-ndl/react';
import './tailwind.css';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';
import { Settings, AppContextType } from './types/types'; // Ensure these are correct


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

    return (
        <NeedleThemeProvider theme={theme} wrapperProps={{ isWrappingChildren: false }}>
        <AppContext.Provider value={{ settings, setSettings, toggleTheme, theme }}>
            <HomePage />
        </AppContext.Provider>
    </NeedleThemeProvider>
    );
}

export default App;
