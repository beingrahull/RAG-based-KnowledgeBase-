import React, { useState } from 'react';
import { Send, Bot, User, ChevronDown, ChevronUp, BookOpen, Sparkles, Loader2, AlertCircle } from 'lucide-react';

export default function ChatQuery() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedSource, setExpandedSource] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userMsg = { id: Date.now(), role: 'user', content: question };
    setMessages((prev) => [...prev, userMsg]);
    const currentQ = question;
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: currentQ }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Query request failed');
      }

      const botMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${err.message}`,
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSource = (key) => {
    setExpandedSource(expandedSource === key ? null : key);
  };

  return (
    <div className="flex flex-col h-[650px] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white">RAG Assistant</h2>
            <p className="text-xs text-slate-400">Ask questions grounded in your uploaded documents</p>
          </div>
        </div>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mb-3">
              <Bot className="w-6 h-6" />
            </div>
            <h3 className="text-base font-medium text-slate-200">Start asking questions</h3>
            <p className="text-xs text-slate-400 mt-1">
              Upload PDF documents first, then ask specific questions. Answers will include source context citations.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-sm shadow-md shadow-indigo-600/10'
                    : msg.isError
                    ? 'bg-red-500/10 border border-red-500/20 text-red-300 rounded-tl-sm'
                    : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-sm shadow-md'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Sources Section */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                      Sources ({msg.sources.length})
                    </div>
                    <div className="space-y-2">
                      {msg.sources.map((src, idx) => {
                        const key = `${msg.id}-src-${idx}`;
                        const isOpen = expandedSource === key;
                        return (
                          <div
                            key={key}
                            className="bg-slate-900/80 border border-slate-800 rounded-lg overflow-hidden text-xs"
                          >
                            <button
                              onClick={() => toggleSource(key)}
                              className="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-slate-800/50 transition text-slate-300"
                            >
                              <span className="font-medium truncate">
                                Source Chunk #{src.chunk_number || idx + 1}
                              </span>
                              {isOpen ? (
                                <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                              ) : (
                                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                              )}
                            </button>
                            {isOpen && (
                              <div className="px-3 py-2.5 border-t border-slate-800/80 bg-slate-950/60 text-slate-400 font-mono text-[11px] leading-normal whitespace-pre-wrap">
                                {src.text}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}

        {loading && (
          <div className="flex gap-3.5 justify-start">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-950 border border-slate-800 text-slate-400 rounded-2xl rounded-tl-sm p-4 text-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Searching vector store & synthesizing answer...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 bg-slate-950/60">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your uploaded documents..."
            disabled={loading}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="p-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded-xl transition shrink-0 shadow-lg shadow-indigo-600/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
