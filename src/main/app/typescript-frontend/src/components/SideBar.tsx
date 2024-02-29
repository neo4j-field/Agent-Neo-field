import React, { useContext } from 'react';
import { SegmentedControl, Switch, Typography } from '@neo4j-ndl/react';
import { AppContextType } from '../types/types'; // Adjust the import path as needed
import { AppContext } from '../App';

function Sidebar() {
  const { settings, setSettings, toggleTheme, theme } = useContext(AppContext) as AppContextType;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked, type } = e.target;
    setSettings((prevSettings) => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };


  const handleLLMChange = (newValue: string) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      selectedLLM: newValue,
    }));
  };

    return (
        <div className="w-80 flex flex-col gap-y-12 flex-shrink-0 p-5 border-r overflow-y-auto">
          <section className="flex flex-col gap-y-4">
            <Typography variant="h3">LLM</Typography>
            <SegmentedControl
                selected={settings.selectedLLM}
                onChange={handleLLMChange}
                size="small"
                className="w-full"
            >
              {['chat-bison 2k', 'chat-bison 32k', 'GPT-4 8k', 'GPT-4 32k'].map((llm) => (
                  <SegmentedControl.Item key={llm} value={llm}>
                    <Typography variant="body-small">{llm}</Typography>
                  </SegmentedControl.Item>
              ))}
            </SegmentedControl>
          </section>
          <section className="flex flex-col gap-y-4">
            <Typography variant="h3">Temperature</Typography>
            <input
                className="w-full h-2 rounded-lg appearance-none cursor-pointer range-lg"
                type="range"
                name="temperature"
                min="0"
                max="1"
                step="0.05"
                value={settings.temperature.toString()}
                onChange={handleChange}
            />
            <Typography variant="body-large" className="text-center">{settings.temperature}</Typography>
          </section>
          <section className="flex flex-col gap-y-4">
            <Switch
                checked={settings.useGrounding}
                name="useGrounding"
                label={<Typography variant="subheading-small">Grounding</Typography>}
                labelBefore
                onChange={handleChange}
            />
          </section>
          <section className="flex flex-col gap-y-4">
            <Switch
                checked={theme === 'dark'}
                name="themeToggle"
                label={<Typography variant="subheading-small">Dark Mode</Typography>}
                labelBefore
                onChange={toggleTheme} // Use the toggleTheme method here
            />
          </section>
        </div>
    );
}

export default Sidebar;
