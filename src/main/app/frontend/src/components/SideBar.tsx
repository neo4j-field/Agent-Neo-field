import React, { useContext, useState } from 'react';
import { Drawer, Typography, SegmentedControl, Switch, Button } from '@neo4j-ndl/react';
import { AppContextType } from '../types/types';
import { AppContext } from '../App';

function Sidebar() {
  const { settings, setSettings, toggleTheme, theme } = useContext(AppContext) as AppContextType;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value, checked, type } = target;

    setSettings((prevSettings) => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const [isDrawerExpanded, setIsDrawerExpanded] = useState(false);

  const handleDrawerChange = (expanded: boolean) => {
  setIsDrawerExpanded(expanded);
  };

  const handleLLMChange = (newValue: string) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      selectedLLM: newValue,
    }));
  };

  return (
    <>
      <Button
        onClick={() => handleDrawerChange(!isDrawerExpanded)}
        type="button"
        color="neutral"
        fill="outlined"
        size="small"
        className="absolute top-0 left-0 mt-4 ml-4"
      >
        {isDrawerExpanded ? 'Hide Options' : 'Show Options'}
      </Button>

      <Drawer
        position="left"
        type="push"
        expanded={isDrawerExpanded}
        onExpandedChange={handleDrawerChange}
        closeable
        className="flex flex-col gap-y-12 flex-shrink-0 p-5 border-r bg-white h-screen"
      >
        <div className="flex flex-col gap-y-12 flex-shrink-0 p-5 overflow-y-auto">
            <section className="flex flex-col gap-y-4">
                <Typography variant="h3">LLM</Typography>
                <SegmentedControl
                    selected={settings.selectedLLM}
                    onChange={handleLLMChange}
                    size="small"
                    className="w-full"
                >
                    {['Gemini', 'GPT-4 8k', 'GPT-4 32k'].map((llm) => (
                        <SegmentedControl.Item
                            key={llm}
                            value={llm}
                            className="min-w-0 flex-1 text-xs px-2"
                        >
                            <Typography variant="body-small" className="truncate">
                                {llm}
                            </Typography>
                        </SegmentedControl.Item>
                    ))}
                </SegmentedControl>
            </section>
            <section className="flex flex-col gap-y-4">
                <Typography variant="h3">Temperature</Typography>
                <input
                    className="w-full h-2 rounded-lg appearance-none cursor-pointer range-lg n-bg-palette-primary-bg-weak"
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
                    onChange={toggleTheme}
                />
            </section>
        </div>
      </Drawer>
    </>
  );
}

export default Sidebar;
