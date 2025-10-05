import React, { useState, useRef, useEffect } from 'react';
import { askChatbot } from '../services/api';
import './Chatbot.css';

const Chatbot = ({ isVisible, onClose }) => {
  const [messages, setMessages] = useState([
    { 
      text: "Hello! I'm your enhanced Lighthouse Assistant. I can help you with:\n\n• Dashboard questions: 'What's our portfolio overview?' or 'Show me the KPIs'\n• Data analysis: 'How many high-risk projects do we have?'\n• Chart generation: 'Create a chart of projects by city' or 'Show me budget distribution'\n• SQL queries: 'What's the average budget in Toronto?'\n\nWhat would you like to know?", 
      sender: 'bot' 
    }
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

    try {
      const response = await askChatbot(input);
      
      // Handle different response types from enhanced chatbot
      let botMessage;
      if (response.type === 'chart') {
        botMessage = {
          text: response.answer,
          sender: 'bot',
          chart: response.chart,
          chartSpec: response.chart_spec
        };
      } else if (response.type === 'analytics') {
        botMessage = {
          text: response.answer,
          sender: 'bot',
          data: response.data
        };
      } else if (response.type === 'sql_result') {
        botMessage = {
          text: response.answer,
          sender: 'bot',
          sqlQuery: response.sql_query,
          results: response.results
        };
      } else {
        // Fallback for simple string responses or errors
        botMessage = {
          text: response.answer || response,
          sender: 'bot'
        };
      }
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        text: "Sorry, I encountered an error processing your request. Please try again.",
        sender: 'bot'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
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
              <div className="message-text">
                {msg.text.split('\n').map((line, i) => (
                  <div key={i}>{line}</div>
                ))}
              </div>
              
              {/* Display chart if present */}
              {msg.chart && (
                <div className="chart-container mt-2">
                  <img 
                    src={`data:image/png;base64,${msg.chart}`} 
                    alt="Generated Chart" 
                    className="img-fluid rounded"
                    style={{ maxWidth: '100%', height: 'auto' }}
                  />
                </div>
              )}
              
              {/* Display SQL query if present */}
              {msg.sqlQuery && (
                <div className="sql-query mt-2">
                  <small className="text-muted">
                    <strong>Query:</strong> <code>{msg.sqlQuery}</code>
                  </small>
                </div>
              )}
              
              {/* Display structured data if present */}
              {msg.results && msg.results.length > 0 && (
                <div className="results-table mt-2">
                  <div className="table-responsive">
                    <table className="table table-sm table-striped">
                      <thead>
                        <tr>
                          {Object.keys(msg.results[0]).map(key => (
                            <th key={key} className="small">{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {msg.results.slice(0, 5).map((row, i) => (
                          <tr key={i}>
                            {Object.values(row).map((value, j) => (
                              <td key={j} className="small">
                                {typeof value === 'number' ? value.toLocaleString() : value}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {msg.results.length > 5 && (
                      <small className="text-muted">... and {msg.results.length - 5} more rows</small>
                    )}
                  </div>
                </div>
              )}
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
