import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export default function DocumentUpload({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files[0]);
    }
  };

  const handleFiles = async (file) => {
    setError(null);
    setSuccessMsg(null);

    // Basic extension check
    const allowed = ['pdf', 'docx', 'txt'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      setError(`Unsupported file type: .${ext}. Please upload PDF, DOCX, or TXT.`);
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to upload document');
      }

      setSuccessMsg(`"${file.name}" uploaded successfully. Ingestion in background.`);
      if (onUploadSuccess) {
        onUploadSuccess(data.document);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <h2 className="text-lg font-semibold text-white mb-1">Upload Document</h2>
      <p className="text-slate-400 text-sm mb-4">
        Upload PDF, DOCX, or TXT files to ingest into the vector knowledgebase.
      </p>

      {error && (
        <div className="mb-4 p-3.5 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="mb-4 p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-3 text-emerald-400 text-sm">
          <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{successMsg}</span>
        </div>
      )}

      <form
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition ${
          dragActive
            ? 'border-indigo-500 bg-indigo-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-950/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleChange}
          className="hidden"
        />

        <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-indigo-400 mb-3 border border-slate-700">
          {uploading ? (
            <Loader2 className="w-6 h-6 animate-spin" />
          ) : (
            <UploadCloud className="w-7 h-7" />
          )}
        </div>

        <p className="text-sm font-medium text-slate-200">
          {uploading ? 'Uploading and processing...' : 'Click to upload or drag & drop'}
        </p>
        <p className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT (Max size 10MB)</p>
      </form>
    </div>
  );
}
