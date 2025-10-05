import React, { useState, useRef, useEffect } from 'react';
import { askChatbot } from '../services/api';
import './Chatbot.css';

const Chatbot = ({ isVisible, onClose }) => {
  const [messages, setMessages] = useState([
    { text: "Hello! Ask me a question about the projects, like 'How many projects are in Toronto?' or 'What is the average budget for completed projects?'", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesAreaRef = useRef(null);

  // Scroll to the bottom of the messages area when new messages are added
  useEffect(() => {
    if (messagesAreaRef.current) {
      messagesAreaRef.current.scrollTop = messagesAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const botResponse = await askChatbot(input);
    const botMessage = { text: botResponse, sender: 'bot' };
    
    setMessages(prev => [...prev, botMessage]);
    setIsLoading(false);
  };

  if (!isVisible) return null;

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Lighthouse Assistant</h5>
        <button type="button" className="btn-close" onClick={onClose}></button>
      </div>
      <div className="card-body chat-window">
        <div className="messages-area" ref={messagesAreaRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && <div className="message bot">...</div>}
        </div>
        <div className="chat-input input-group mt-3">
          <input 
            type="text" 
            className="form-control" 
            placeholder="Ask a question..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
            disabled={isLoading}
          />
          <button className="btn btn-primary" onClick={handleSend} disabled={isLoading}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
