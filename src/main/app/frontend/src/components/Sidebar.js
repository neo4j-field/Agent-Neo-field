import React, { useContext } from 'react';
import { AppContext } from '../App';

function Sidebar() {
  const { settings, setSettings } = useContext(AppContext);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSettings((prevSettings) => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  return (
    <div className="sidebar">
      {/* LLM Selection */}
      <div>
        <h3>Select LLM</h3>
        {['chat-bison 2k', 'chat-bison 32k', 'GPT-4 8k', 'GPT-4 32k'].map((llm) => (
          <label key={llm}>
            <input
              type="radio"
              name="selectedLLM"
              value={llm}
              checked={settings.selectedLLM === llm}
              onChange={handleChange}
            />
            {llm}
          </label>
        ))}
      </div>

      {/* Temperature Adjustment */}
      <div>
        <h3>Select Temperature</h3>
        <input
          type="range"
          name="temperature"
          min="0"
          max="1"
          step="0.05"
          value={settings.temperature}
          onChange={handleChange}
        />
        <span>{settings.temperature}</span>
      </div>

      {/* Grounding Toggle */}
      <div>
        <label>
          <h3>Use Grounding?</h3>
          <input
            type="checkbox"
            name="useGrounding"
            checked={settings.useGrounding}
            onChange={handleChange}
          />
        </label>
      </div>

      {/* Context Documents Selection */}
      {settings.useGrounding && (
        <div>
          <h3>Select Number of Context Documents</h3>
          <input
            type="range"
            name="contextDocuments"
            min="1"
            max="10"
            value={settings.contextDocuments}
            onChange={handleChange}
          />
          <span>{settings.contextDocuments}</span>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
