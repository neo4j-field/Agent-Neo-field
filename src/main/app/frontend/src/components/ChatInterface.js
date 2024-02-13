// Import necessary hooks and utilities from React and other libraries
import React, { useContext, useState } from 'react';
import { AppContext } from '../App'; // Import the context to use shared state
import { v4 as uuidv4 } from 'uuid'; // Import uuid to generate unique ids

// Define the ChatInterface component
function ChatInterface() {
  // Use the useContext hook to access global settings from AppContext
  const { settings } = useContext(AppContext);

  // State hooks for managing component state
  const [input, setInput] = useState(''); // Tracks user input
  const [messages, setMessages] = useState([]); // Stores all chat messages
  const [sessionId] = useState(() => `s-${uuidv4()}`); // Generates a unique session id
  const [conversationId] = useState(() => `conv-${uuidv4()}`); // Generates a unique conversation id
  const [messageHistory, setMessageHistory] = useState([]); // Stores message history for API requests
  const [isSubmitting, setIsSubmitting] = useState(false); // Tracks if a submission is in progress

  // Function to call the API asynchronously
  const fetchResponseFromAPI = async (inputText) => {
    setIsSubmitting(true); // Indicate that an API call is in progress
    // Prepare the request body with necessary information
    const requestBody = {
      session_id: sessionId,
      conversation_id: conversationId,
      question: inputText,
      llm_type: settings.selectedLLM,
      temperature: settings.temperature,
      number_of_documents: settings.useGrounding ? settings.contextDocuments : 0,
      message_history: messageHistory,
    };

    try {
      // Execute the API call with fetch
      console.log("address: ", process.env.REACT_APP_BACKEND_ADDRESS)
      console.log("address: ", `${process.env.REACT_APP_BACKEND_ADDRESS}/llm`)
      console.log("body: ", requestBody)
      const response = await fetch(`${process.env.REACT_APP_BACKEND_ADDRESS}/llm`, {
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
      const data = await response.json(); // Parse the JSON response
      setMessageHistory(data.message_history); // Update the message history with the new history from response
      return data.content; // Return the response content to be displayed
    } catch (error) {
      console.error("API call failed:", error);
      return "Sorry, something went wrong."; // Handle errors gracefully
    } finally {
      setIsSubmitting(false); // Re-enable the submit button after the API call
    }
  };

  // Function to simulate typing effect for bot responses
  const simulateTypingEffect = (responseText) => {
    let typedText = '';
    for (let i = 0; i < responseText.length; i++) {
      setTimeout(() => {
        typedText += responseText.charAt(i); // Append characters one by one
        // Update the messages state with the new partial message
        if (i === 0) {
          setMessages(msgs => [...msgs, { id: Date.now(), text: typedText, sender: 'bot', isTyping: true }]);
        } else {
          // Update the last message with the new text
          setMessages(msgs => msgs.map(msg => 
            msg.isTyping ? { ...msg, text: typedText } : msg
          ));
        }
        // Remove the typing indicator once the full message is displayed
        if (i === responseText.length - 1) {
          setMessages(msgs => msgs.map(msg => 
            msg.isTyping ? { ...msg, isTyping: false } : msg
          ));
        }
      }, i * 20); // Delay between each character to simulate typing
    }
  };

  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission behavior
    if (!input.trim()) return; // Ignore empty submissions

    // Create a new message object and add it to the messages array
    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages(messages => [...messages, userMessage]);
    setInput(''); // Clear the input field

    // Fetch the response from the API and simulate typing effect
    const apiResponse = await fetchResponseFromAPI(input);
    simulateTypingEffect(apiResponse);
  };

  // Function to reset the chat interface
  const handleReset = () => {
    setMessages([]); // Clear all messages
    setMessageHistory([]); // Clear message history
    setIsSubmitting(false); // Ensure submit button is enabled
  };

  // Inline styles for the submit button
  const buttonStyles = {
    enabled: {
      backgroundColor: '#007bff', // Color for the enabled state
      color: 'white',
      cursor: 'pointer',
    },
    disabled: {
      backgroundColor: '#cccccc', // Color for the disabled state
      color: '#666666',
      cursor: 'not-allowed',
    }
  };

  // Component JSX to render the chat interface
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
        <button
          type="submit"
          disabled={isSubmitting}
          style={isSubmitting ? buttonStyles.disabled : buttonStyles.enabled}
        >
          Send
        </button>
        <button type="button" onClick={handleReset}>Reset Chat</button>
      </form>
    </div>
  );
}

export default ChatInterface; // Export the component for use in other parts of the application
