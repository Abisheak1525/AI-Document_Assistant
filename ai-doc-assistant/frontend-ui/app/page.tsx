"use client";
import { useState, Component, ReactNode } from "react";
import { chatWithAI } from "../lib/api";

interface ChatResponse {
  answer: string;
  sources: string[];
}

interface Message {
  query: string;
  response: ChatResponse;
}

// Simple Error Boundary component
class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: string }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: "" };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <h2>Something went wrong.</h2>
          <p>{this.state.error}</p>
          <button onClick={() => this.setState({ hasError: false, error: "" })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await chatWithAI(query);
      
      // Handle response as before
      let data: ChatResponse;
      if (response.answer && typeof response.answer === 'object') {
        data = response.answer;
      } else {
        data = response;
      }
      
      // Add to chat history
      setMessages(prev => [...prev, { query, response: data }]);
      setQuery(""); // Clear input
    } catch (err) {
      console.error(err);
      // Error is handled by boundary if it propagates
    }
    setLoading(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://localhost:8080/api/upload", { // Adjust URL if needed
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        setMessages([]); // Clear history for new chat
        setFile(null);
        alert("PDF uploaded successfully. Start chatting!");
      } else {
        alert("Upload failed.");
      }
    } catch (err) {
      console.error(err);
      alert("Upload error.");
    }
  };

  return (
    <ErrorBoundary>
      <main className="p-10 max-w-2xl mx-auto min-h-screen bg-white text-black">
        <h1 className="text-2xl font-bold mb-5">AI Document Assistant</h1>
        
        {/* PDF Upload */}
        <div className="mb-4">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange} 
            className="mb-2"
          />
          <button 
            onClick={handleUpload} 
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
            disabled={!file}
          >
            Upload PDF & Start New Chat
          </button>
        </div>
        
        {/* Form */}
        <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
          <input 
            className="border p-2 flex-grow rounded"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask something about your document..."
          />
          <button 
            type="submit"
            className={`px-4 py-2 rounded transition ${loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white relative`}
            disabled={loading}
          >
            {loading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
            <span className={loading ? 'invisible' : ''}>Ask</span>
          </button>
        </form>
        
        {/* Chat History */}
        <div className="max-h-96 overflow-y-auto border rounded p-4 bg-gray-50">
          {messages.length === 0 ? (
            <p className="text-gray-500">No messages yet. Ask a question!</p>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="mb-4 p-3 border-b bg-white rounded shadow-sm">
                <p className="font-semibold text-blue-600">You: {msg.query}</p>
                <p className="whitespace-pre-line text-gray-800 mt-2">{msg.response.answer}</p>
                <div className="mt-2 pt-2 border-t text-sm text-gray-500 italic">
                  <strong>Source:</strong> {msg.response.sources?.length > 0 ? msg.response.sources.join(", ") : "No sources found"}
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </ErrorBoundary>
  );
}