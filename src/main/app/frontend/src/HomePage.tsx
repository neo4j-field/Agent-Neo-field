import React, {useCallback, useContext,useState} from 'react';
import { AppContext } from './App'; // Import AppContext to use global state if needed
import Sidebar from './components/SideBar';
import ChatInterfaceStarterKit from './components/ChatInterfaceStartKit';
import { Logo, Typography } from '@neo4j-ndl/react';
import {GraphResponse} from "./types/graphtypes";



const HomePage: React.FC<{ conversationId: string }> = ({ conversationId }) => {

    const { theme, settings } = useContext(AppContext);
    const [conversationData, setConversationData] = useState<GraphResponse | null>(null);


    const fetchConversationData = useCallback(async () => {
    try {
        const response = await fetch(`${import.meta.env.VITE_BACKEND_DEV_ADDRESS}/graph-llm/${conversationId}`);
        console.log('response:', response);

        if (!response.ok) {
            throw new Error(`Error fetching data: ${response.statusText}`);
        }

        const text = await response.text();
        console.log('raw response', text);

        const data: GraphResponse = JSON.parse(text);
        setConversationData(data);
    } catch (error) {
        console.error('Failed to fetch conversation data:', error);
    }
}, [conversationId]);


    return (
        <div className={`flex ${theme === 'dark' ? 'ndl-theme-dark' : 'ndl-theme-light'} n-bg-palette-neutral-bg-weak`}>
            <Sidebar
                conversationId={conversationId}
                onFetchConversationData={fetchConversationData}
            />
            <div className="flex w-full flex-col justify-center items-center">
                <section className="flex justify-center items-center p-4">
                    <Logo color="white" type="full" className="h-8 min-h-12 min-w-32" />
                    <Typography variant="h2" className="ml-4">Agent-Neo</Typography>
                </section>
                <ChatInterfaceStarterKit
                    conversationId={conversationId}
                    onFetchConversationData={fetchConversationData}
                />
            </div>
        </div>
    );
};

export default HomePage;
