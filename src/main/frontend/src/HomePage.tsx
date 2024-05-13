import React, {useContext} from 'react';
import { AppContext } from './App'; // Import AppContext to use global state if needed
import Sidebar from './components/SideBar';
import ChatInterfaceStarterKit from './components/ChatInterfaceStartKit';
import { Logo, Typography } from '@neo4j-ndl/react';



const HomePage: React.FC = () => {
    // If you need to access the global context (e.g., theme or settings), you can use useContext here
    const { theme, settings } = useContext(AppContext);


    return (
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
    );
};

export default HomePage;
