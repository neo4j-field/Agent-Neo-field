import React from "react";

export interface Settings {
  selectedLLM: string;
  temperature: number;
  useGrounding: boolean;
  contextDocuments: number;
}

export interface AppContextType {
  settings: Settings;
  setSettings: React.Dispatch<React.SetStateAction<Settings>>;
  toggleTheme: () => void;
  theme: 'light' | 'dark';
}


//todo: might need to refactor
export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  isTyping?: boolean;
  message_history?: any[];
}


//todo: might need to refactor
export interface ApiRequestBody {
  session_id: string;
  conversation_id: string;
  question: string;
  llm_type: string;
  temperature: number;
  number_of_documents: number;
  message_history?: any[]; // Adjust the type according to your actual message history structure
}

export interface ApiResponse {
  session_id: string;
  conversation_id: string;
  content: string; // Ensure this property is included
  message_history?: string[]; // This is correctly optional
}

