import React, { createContext, useState }
 from 'react';
import Sidebar from './components/Sidebar'; // Ensure you create Sidebar.js
import ChatInterface from './components/ChatInterface'; // Ensure you create ChatInterface.js
import './App.css'; // Ensure we add styling

// Create a context for global state
export const AppContext = createContext();

function App() {
  const [settings, setSettings] = useState({
    selectedLLM: 'GPT-4 8k',
    temperature: 0.7,
    useGrounding: true,
    contextDocuments: 10,
  });

  return (
    <AppContext.Provider value={{ settings, setSettings }}>
      
      <div className="app-title">Agent-Neo</div>
      <div className="app">
        <Sidebar />
        <ChatInterface />
      </div>
    </AppContext.Provider>
  );
}

export default App;
