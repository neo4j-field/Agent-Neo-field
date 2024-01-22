import React, { useState } from 'react';

function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  // Asynchronous function to call our API
  const fetchResponseFromAPI = async (inputText) => {
    try {
      const response = await fetch('YOUR_API_ENDPOINT', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add any additional headers our API requires
        },
        body: JSON.stringify({ message: inputText }),
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }
      const data = await response.json();
      return data.response; // Adjust this based on how our API formats the response
    } catch (error) {
      console.error("API call failed:", error);
      return "Sorry, something went wrong."; // Providing a user-friendly error message
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return; // Prevent sending empty messages

    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInput(''); // Clear input after sending

    // Invoke the API call and handle the response
    const apiResponse = await fetchResponseFromAPI(input);
    const botResponse = { id: Date.now() + 1, text: apiResponse, sender: 'bot' };
    setMessages((prevMessages) => [...prevMessages, botResponse]);
  };

  const handleReset = () => {
    setMessages([]); // Clear chat history
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
