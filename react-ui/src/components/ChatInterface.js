import React, { useContext, useState } from 'react';
import { AppContext } from '../App';
import { v4 as uuidv4 } from 'uuid';

function ChatInterface() {
  
  const { settings } = useContext(AppContext);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [sessionId] = useState(() => `s-${uuidv4()}`);
  const [conversationId] = useState(() => `conv-${uuidv4()}`);

  // Asynchronous function to call our API
  const fetchResponseFromAPI = async (inputText) => {
    const requestBody = {
      session_id: sessionId,
      conversation_id: conversationId,
      question: inputText,
      llm_type: settings.selectedLLM,
      temperature: settings.temperature,
      number_of_documents: settings.useGrounding ? settings.contextDocuments : 0,
    };

    try {
      const response = await fetch('https://agent-neo-backend-qaiojvs3da-uc.a.run.app/llm', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }
      const data = await response.json();
      return data.content; // Adjust this based on how our API formats the response
    } catch (error) {
      console.error("API call failed:", error);
      return "Sorry, something went wrong."; // Providing a user-friendly error message
    }
  };

  const simulateTypingEffect = (responseText) => {
    let typedText = '';
    for (let i = 0; i < responseText.length; i++) {
      setTimeout(() => {
        typedText += responseText.charAt(i);
        // Update messages with partially typed text
        if (i === 0) {
          setMessages(msgs => [...msgs, { id: Date.now(), text: typedText, sender: 'bot', isTyping: true }]);
        } else {
          setMessages(msgs => msgs.map(msg => 
            msg.isTyping ? { ...msg, text: typedText } : msg
          ));
        }
        // Once the entire message is typed out, update to remove the typing indicator
        if (i === responseText.length - 1) {
          setMessages(msgs => msgs.map(msg => 
            msg.isTyping ? { ...msg, isTyping: false } : msg
          ));
        }
      }, i * 20); // Speed of typing effect
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages(messages => [...messages, userMessage]);
    setInput('');

    // Fetch the response from the API
    const apiResponse = await fetchResponseFromAPI(input);
    simulateTypingEffect(apiResponse);
  };

  const handleReset = () => {
    setMessages([]); // Clears the chat history
  };

  return (
    <div className="chat-interface">
      <div className="chat-output">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message here..."
        />
        <button type="submit">Send</button>
        <button type="button" onClick={handleReset}>Reset Chat</button>
      </form>
    </div>
  );
}

export default ChatInterface;
