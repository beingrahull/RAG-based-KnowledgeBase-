import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import AuthModal from './components/AuthModal';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import ChatQuery from './components/ChatQuery';
import { FileText, MessageSquare, LogOut, User, Database, Sparkles, Loader2 } from 'lucide-react';

function Dashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'documents'
  const [docRefresh, setDocRefresh] = useState(0);

  const handleUploadSuccess = () => {
    setDocRefresh((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-600/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg text-white tracking-tight">RAG KBEng</span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-md uppercase">
                Frontend
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center bg-slate-950 p-1 border border-slate-800 rounded-xl">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Q&A Chat
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'documents'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              Documents
            </button>
          </div>

          {/* User Profile / Logout */}
          <div className="flex items-center gap-3">
            <div className="hidden md:flex flex-col items-end">
              <span className="text-xs font-medium text-slate-200">{user?.name}</span>
              <span className="text-[11px] text-slate-500">{user?.email}</span>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-red-400 bg-slate-900 border border-slate-800 hover:border-red-500/30 rounded-xl transition"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'chat' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <ChatQuery />
            </div>
            <div className="space-y-6">
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
              <DocumentList refreshTrigger={docRefresh} />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            <DocumentList refreshTrigger={docRefresh} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-600">
        RAG KBEng • Production-Shaped Retrieval Augmented Generation Engine
      </footer>
    </div>
  );
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-indigo-400">
        <Loader2 className="w-8 h-8 animate-spin mb-3" />
        <p className="text-sm font-medium text-slate-400">Connecting to Knowledge Engine...</p>
      </div>
    );
  }

  return user ? <Dashboard /> : <AuthModal />;
}
