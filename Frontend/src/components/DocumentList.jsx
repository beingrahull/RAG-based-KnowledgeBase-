import React, { useEffect, useState, useCallback } from 'react';
import { FileText, RefreshCw, CheckCircle, Clock, AlertTriangle, Loader2 } from 'lucide-react';

export default function DocumentList({ refreshTrigger, onSelectDocument }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch('/api/documents');
      if (!res.ok) {
        throw new Error('Failed to fetch documents');
      }
      const data = await res.json();
      setDocuments(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments, refreshTrigger]);

  // Auto-poll if any document is in 'pending' or 'processing' status
  useEffect(() => {
    const hasInFlight = documents.some(
      (doc) => doc.status === 'pending' || doc.status === 'processing'
    );
    if (!hasInFlight) return;

    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000);

    return () => clearInterval(interval);
  }, [documents, fetchDocuments]);

  const formatSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
  };

  const renderStatusBadge = (status) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3.5 h-3.5" /> Ready
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3.5 h-3.5" /> Pending
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertTriangle className="w-3.5 h-3.5" /> Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Your Documents</h2>
          <p className="text-slate-400 text-sm">
            {documents.length} document{documents.length === 1 ? '' : 's'} in library
          </p>
        </div>
        <button
          onClick={fetchDocuments}
          className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition"
          title="Refresh document list"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin mb-2 text-indigo-500" />
          <p className="text-sm">Loading documents...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      ) : documents.length === 0 ? (
        <div className="py-12 text-center border border-dashed border-slate-800 rounded-xl">
          <FileText className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-slate-400 text-sm font-medium">No documents uploaded yet.</p>
          <p className="text-slate-500 text-xs mt-1">Upload a PDF to start asking questions.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onClick={() => onSelectDocument && onSelectDocument(doc)}
              className="p-4 bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 rounded-xl flex items-center justify-between gap-4 transition"
            >
              <div className="flex items-center gap-3.5 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <h3 className="text-sm font-medium text-slate-200 truncate">{doc.filename}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                    <span>{formatSize(doc.size)}</span>
                    <span>•</span>
                    <span>{formatDate(doc.uploaded_at)}</span>
                  </div>
                </div>
              </div>
              <div className="shrink-0">{renderStatusBadge(doc.status)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
