// Import necessary hooks and utilities from React and other libraries
import React, { useContext, useState } from 'react';
import { AppContext } from '../App'; // Import the context to use shared state
import { v4 as uuidv4 } from 'uuid'; // Import uuid to generate unique ids
import { Button, TextInput, Typography, Widget, Avatar } from '@neo4j-ndl/react';
import ChatBotUserAvatar from './assets/chatbot-user.png';
import ChatBotAvatar from './assets/chatbot-ai.png';

// Define the ChatInterface component
function ChatInterface() {
  // Use the useContext hook to access global settings from AppContext
  const { settings } = useContext(AppContext);

  // State hooks for managing component state
  const [input, setInput] = useState(''); // Tracks user input
  const [messages, setMessages] = useState([]); // Stores all chat messages
  const [sessionId] = useState(() => `s-${uuidv4()}`); // Generates a unique session id
  const [conversationId] = useState(() => `conv-${uuidv4()}`); // Generates a unique conversation id
  const [messageHistory, setMessageHistory] = useState(); // Stores message history for API requests
  const [isSubmitting, setIsSubmitting] = useState(false); // Tracks if a submission is in progress

  const [isResponseOk, setIsResponseOk] = useState(false); // Tracks if response from API is ok

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
        setIsResponseOk(false);
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }
      const data = await response.json(); // Parse the JSON response
      setMessageHistory(data.message_history); // Update the message history with the new history from response
      setIsResponseOk(true);
      return data.content; // Return the response content to be displayed
    } catch (error) {
      setIsResponseOk(false);
      console.error("API call failed:", error);
      return "Sorry, something went wrong."; // Handle errors gracefully
    } finally {
      setIsSubmitting(false); // Re-enable the submit button after the API call
    }
  };

  // Function to simulate typing effect for bot responses
const simulateTypingEffect = async (responseText) => {
  let typedText = '';
  // Add initial message indicating typing is in progress
  const typingMessageId = Date.now();
  setMessages(msgs => [...msgs, { id: typingMessageId, text: '', sender: 'bot', isTyping: true }]);

  for (let i = 0; i < responseText.length; i++) {
    await delay(20); // Delay to simulate typing
    typedText += responseText.charAt(i);
    // Update the message to show the new character
    setMessages(msgs => msgs.map(msg =>
      msg.id === typingMessageId ? { ...msg, text: typedText } : msg
    ));
  }

  // Once the message is fully "typed out", remove the typing indicator
  setMessages(msgs => msgs.map(msg =>
    msg.id === typingMessageId ? { ...msg, isTyping: false } : msg
  ));
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

  // Component JSX to render the chat interface
  return (
    <div className="flex flex-col grow pt-12 pb-10 pr-5 pl-2.5 w-9/12">
      <div className="flex flex-col overflow-y-auto p-2.5 mb-5 h-[calc(100dvh-220px)] border border-[#ccc]">
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: '3rem' }}>
        <Widget className='n-bg-palette-neutral-bg-weak' header='' isElevated={false} style={{ height: '100%' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '12px' }}>
            {messages.map((chat) => (
              <div
                key={chat.id}
                style={{
                  display: 'flex',
                  flexDirection: chat.sender === 'bot' ? 'row' : 'row-reverse',
                  alignItems: 'flex-end',
                  gap: '10px',
                }}
              >
                <div style={{ width: '30px', height: '30px' }}>
                  {chat.sender === 'bot' ? (
                    <Avatar
                      className=''
                      hasStatus
                      name='KM'
                      shape='square'
                      size='x-large'
                      source={ChatBotAvatar}
                      status={isResponseOk? 'online' : 'offline'}
                      type='image'
                      style={{ marginLeft: '-15px' }}
                    />
                  ) : (
                    <Avatar
                      className=''
                      hasStatus
                      name='KM'
                      shape='square'
                      size='x-large'
                      source={ChatBotUserAvatar}
                      status='online'
                      type='image'
                    />
                  )}
                </div>
                <Widget
                  header=''
                  isElevated={true}
                  className={chat.sender === 'bot' ? 'n-bg-palette-neutral-bg-strong' : 'n-bg-palette-primary-bg-weak'}
                  style={{
                    padding: '4',
                    alignSelf: 'flex-start',
                    maxWidth: '55%',
                  }}
                >
                  <div style={{ flexGrow: 1 }}>
                  <Typography variant='body-medium'>{chat.text}</Typography>
                  </div>
                  <div style={{ textAlign: 'right', verticalAlign: 'bottom', paddingTop: '12px' }}>
                    <Typography variant='body-small'>2024-01-01 09:00:00</Typography>
                  </div>
                </Widget>
              </div>
            ))}
          </div>
        </Widget>
      </div>
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2.5">
        <TextInput
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message here..."
          fluid={true}
          className='grow'
        />
      <Button
        color="primary"
        fill="filled"
        size="medium"
        disabled={isSubmitting}
        loading={isSubmitting}
        type="submit"
        >Send
      </Button>
      <Button
          onClick={handleReset}
          type="button"
          color="neutral"
          fill="outlined"
          size="medium" // Added for size consistency
      >Reset Chat
      </Button>
      </form>
    </div>
  );
}

export default ChatInterface; // Export the component for use in other parts of the application
