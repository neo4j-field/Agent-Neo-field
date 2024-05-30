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
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  graphData: GraphData | null;
  setGraphData: React.Dispatch<React.SetStateAction<GraphData | null>>;
}

export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  isTyping?: boolean;
  message_history?: any[];
}


export interface FetchOptions {
  endpoint: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: { [key: string]: string };
  body?: string;
}

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



export interface DocumentNode {
  url: string;
  text: string;
  index: number;
}


export interface GraphData {
  nodes: DocumentNode[];
}

