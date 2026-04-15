"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Plus, Send, FileText, Database, MessageSquare, Loader2, Search, ArrowRight } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const INGESTION_URL = process.env.NEXT_PUBLIC_INGESTION_SERVICE_URL || 'http://localhost:8001';
const QUERY_URL = process.env.NEXT_PUBLIC_QUERY_SERVICE_URL || 'http://localhost:8002';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

type DocumentRecord = {
  id: number;
  filename: string;
  upload_time: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchDocuments = async () => {
    try {
      const resp = await axios.get(`${INGESTION_URL}/documents`);
      setDocuments(resp.data.data);
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${INGESTION_URL}/upload`, formData);
      if (fileInputRef.current) fileInputRef.current.value = '';
      fetchDocuments();
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isQuerying) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsQuerying(true);

    try {
      const resp = await axios.post(`${QUERY_URL}/query`, { question: input });
      setMessages(prev => [...prev, { role: 'assistant', content: resp.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Connection lost. Ensure services are running." }]);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="main-container">
      {/* MINIMAL SIDEBAR */}
      <motion.aside 
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="sidebar"
      >
        <div className="sidebar-header">
          <div className="logo-circle" />
          <h3 style={{ fontSize: '15px', fontWeight: 600 }}>AI Brain</h3>
        </div>

        <div className="upload-section">
          <button 
            className="minimal-btn" 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? <Loader2 className="animate-spin" size={14} /> : <Plus size={14} />}
            <span>{isUploading ? 'INDEXING' : 'NEW DOCUMENT'}</span>
          </button>
          <input type="file" ref={fileInputRef} onChange={handleUpload} hidden />
        </div>

        <div className="brains-section">
          <span className="label">KNOWLEDGE</span>
          <div className="doc-list">
            <AnimatePresence>
              {documents.map((doc, idx) => (
                <motion.div 
                  key={doc.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05, duration: 0.5 }}
                  className="doc-item"
                >
                  <FileText size={12} />
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{doc.filename}</span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </motion.aside>

      {/* MINIMAL CHAT Area */}
      <main className="chat-area">
        <div className="chat-header">
          <div className="status-label">
            <div className="dot" />
            <span>AI Assistant</span>
          </div>
          <Search size={16} style={{ opacity: 0.3 }} />
        </div>

        <div className="messages-container" ref={scrollRef}>
          <AnimatePresence initial={false}>
            {messages.length === 0 && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="empty-state"
                style={{ height: '400px' }}
              >
                <h1 style={{ fontSize: '32px', marginBottom: '10px' }}>What’s on your mind?</h1>
                <p style={{ opacity: 0.4 }}>Upload a document to expand the knowledge base.</p>
              </motion.div>
            )}

            {messages.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, scale: 0.98, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                className={`message-bubble ${msg.role === 'assistant' ? 'msg-ai' : 'msg-user'}`}
              >
                {msg.content}
              </motion.div>
            ))}

            {isQuerying && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="msg-ai"
                style={{ width: '100px', padding: '12px 24px' }}
              >
                <Loader2 className="animate-spin" size={16} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="input-container">
          <form className="fluid-input" onSubmit={handleSendMessage}>
            <input 
              type="text" 
              placeholder="Type your question..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isQuerying}
            />
            <button type="submit" disabled={!input.trim() || isQuerying} style={{ background: 'none', border: 'none' }}>
              <ArrowRight className="send-icon" size={20} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
