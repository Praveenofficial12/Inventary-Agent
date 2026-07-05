import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User } from 'lucide-react';
import apiClient from '../api/apiClient';

const SUGGESTIONS = [
  'What products are running low on stock?',
  'Analyze current inventory health',
  'Which supplier has the fastest lead time?',
  'Generate a stock shortage alert',
];

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(2, 10));
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    try {
      const res = await apiClient.post('/chat/message', {
        session_id: sessionId,
        message: text,
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.content }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'System error encountered. Please verify the backend connection and retry.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)' }}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <h1 className="page-title">Nexus AI Chat</h1>
        <p className="page-subtitle">Conversational inventory intelligence powered by Gemini AI</p>
      </div>

      {/* Messages Area */}
      <div className="chat-messages" style={{ flex: 1 }}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <Bot size={32} />
            </div>
            <h2>How can Nexus AI assist you?</h2>
            <p>Ask about stock levels, supplier lead times, policy documents, or get a quick analysis of your inventory status.</p>
            <div className="chat-suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="suggestion-chip" onClick={() => sendMessage(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg ${msg.role === 'user' ? 'user' : ''}`}>
            <div className={`msg-avatar ${msg.role === 'assistant' ? 'ai' : 'user'}`}>
              {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className={`msg-bubble ${msg.role === 'assistant' ? 'ai' : 'user'}`}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="typing-indicator">
            <div className="msg-avatar ai">
              <Bot size={18} />
            </div>
            <div className="typing-bubble">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask the Nexus AI about your inventory..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
