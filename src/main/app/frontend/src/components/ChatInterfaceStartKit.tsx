import {Settings, Message, ApiRequestBody, ApiResponse} from '../types/types'; // Adjust the import path as needed
import React, {useContext, useState} from 'react';
import { v4 as uuidv4 } from 'uuid';
import { AppContext } from '../App';
import {Avatar, Button, TextInput, Typography, Widget} from "@neo4j-ndl/react";
import ChatBotAvatar from './assets/chatbot-ai.png';
import ChatBotUserAvatar from './assets/chatbot-user.png';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


function ChatInterface() {


    const {settings} = useContext(AppContext) as { settings: Settings };

    const [input, setInput] = useState<string>(" ");
    const [messages, setMessages] = useState<Message[]>([]);
    const [sessionId] = useState<string>(() => `s-${uuidv4()}`);
    const [conversationId] = useState<string>(() => `conv-${uuidv4()}`);
    const [messageHistory, setMessageHistory] = useState<string[]>([]);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [isResponseOk, setIsResponseOk] = useState<boolean>(false);


    const fetchResponseFromAPI = async (inputText: string): Promise<string> => {
        setIsSubmitting(true);

        const requestBody: ApiRequestBody = {
        session_id: sessionId,
        conversation_id: conversationId,
        question: inputText,
        llm_type: settings.selectedLLM,
        temperature: settings.temperature,
        number_of_documents: settings.useGrounding ? settings.contextDocuments : 0,
        message_history: messageHistory,
    };

    try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_ADDRESS}/llm`, {
          method: 'POST',
          headers: {
              'accept': 'application/json',
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
      });
      const responseData: ApiResponse = await response.json();
      if (!response.ok) {
          throw new Error( "HTTP error: ${response.status}");
      }
      setMessageHistory(responseData.message_history || []);
      setIsResponseOk(true);
      return responseData.content;
    } catch (error) {
        console.error("API call failed:", error);
        setIsResponseOk(false);
        return "Sorry, something went wrong.";
    } finally {
        setIsSubmitting(false);
    }
};



    const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

    const simulateTypingEffect = async (responseText: string, setMessages: React.Dispatch<React.SetStateAction<Message[]>>) => {
        let typedText = " ";

        const typingMessageId = Date.now();
        setMessages(msgs => [...msgs, {id: typingMessageId, text: ' ', sender: 'bot', isTyping: true}]);

        for (let j = 0; j < responseText.length; j++) {
            await delay(15);

            typedText += responseText.charAt(j);

            setMessages(msgs => msgs.map(msg =>
                msg.id === typingMessageId ? {...msg, text: typedText} : msg));
        }

        setMessages(msgs => msgs.map(msg =>
            msg.id === typingMessageId ? {...msg, isTyping: false} : msg));

    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!input.trim()) return;

        const userMessage: Message = { id: Date.now(), text: input, sender: 'user' };
        setMessages((messages: Message[]) => [...messages, userMessage]);
        setInput(''); // Clear the input field

         const apiResponse: string = await fetchResponseFromAPI(input);
          simulateTypingEffect(apiResponse, setMessages);
};


    const handleReset = () => {
            setMessages([]); // Clear all messages
            setMessageHistory([]); // Clear message history
            setIsSubmitting(false); // Ensure submit button is enabled
    };

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
                  <Markdown remarkPlugins={[remarkGfm]}>{chat.text}</Markdown>
                  </div>
                  <div style={{ textAlign: 'right', verticalAlign: 'bottom', paddingTop: '12px' }}>
                    <Typography variant='body-small'>{Date.now()}</Typography>
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
          size="medium"
      >Reset Chat
      </Button>
      </form>
    </div>
  );
}

export default ChatInterface;










