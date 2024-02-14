import React, { useContext } from 'react';
import { AppContext } from '../App';
import { SegmentedControl, Switch, TextInput, Label} from '@neo4j-ndl/react';


function Sidebar() {
  const { settings, setSettings } = useContext(AppContext);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSettings((prevSettings) => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

   const handleLLMChange = (newValue) => {
    setSettings((prevSettings) => ({
      ...prevSettings,
      selectedLLM: newValue
    }));
  };




  return (
      <div className="w-80 flex-shrink-0 p-5 border-r overflow-y-auto">
          <div className="mb-4 p-4">
              <h3 className="text-lg font-semibold mb-2">Select LLM</h3>
              <SegmentedControl
                  selected={settings.selectedLLM}
                  onChange={handleLLMChange}
                  size="small"
                  className="w-full"
              >
                  {/* Wrapping each SegmentedControl.Item in a div with Tailwind padding for vertical spacing */}
                  {['chat-bison 2k', 'chat-bison 32k', 'GPT-4 8k', 'GPT-4 32k'].map((llm) => (
                      <div key={llm} className="my-10"> {/* Adds vertical padding to each item */}
                          <SegmentedControl.Item value={llm} className="py-2">
                              {llm}
                          </SegmentedControl.Item>
                      </div>
                  ))}
              </SegmentedControl>
          </div>
          <div className="mb-4">
              <h3 className="text-lg font-semibold mb-2">Select Temperature</h3>
              <input
                  className="w-full h-2 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 custom-slider" // Tailwind classes for initial styling + custom-slider for the thumb and track
                  type="range"
                  name="temperature"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.temperature}
                  onChange={handleChange}
              />
              <div className="text-center mt-1">{settings.temperature}</div>
          </div>
          <div className="mb-4">
              <label className="flex items-center space-x-3">
                  <h3 className="text-lg font-semibold">Use Grounding?</h3>
                  <input
                      type="checkbox"
                      name="useGrounding"
                      checked={settings.useGrounding}
                      onChange={handleChange}
                      className="form-checkbox h-5 w-5" // Tailwind classes for styling checkboxes
                  />
              </label>
          </div>
      </div>
  );
}

export default Sidebar;