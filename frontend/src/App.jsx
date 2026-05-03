import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Use relative URL for production (same domain)
  const API_URL = '/generate';

  const handleGenerate = async (type) => {
    if (!input.trim()) {
      alert('Please enter some text first!');
      return;
    }

    setLoading(true);
    setResponse('');
    setError('');

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: input,
          type: type,
        }),
      });

      const data = await res.json();

      if (res.ok) {
        setResponse(data.response);
      } else {
        const errMsg = data.detail || 'Something went wrong on the server.';
        setError(errMsg);
        alert('Error: ' + errMsg);
      }
    } catch (err) {
      console.error('Fetch error:', err);
      const networkErr = 'Failed to connect to the backend server. Please ensure it is running at http://localhost:8000';
      setError(networkErr);
      alert(networkErr);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!response) return;
    navigator.clipboard.writeText(response).then(() => {
      alert('Copied to clipboard!');
    });
  };

  return (
    <div className="app-container">
      <div className="card">
        <h1>AI Study Assistant</h1>
        
        <textarea
          placeholder="Paste your notes or enter a topic here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />

        <div className="button-group">
          <button disabled={loading} onClick={() => handleGenerate('10mark')}>Generate 10-Mark Answer</button>
          <button disabled={loading} onClick={() => handleGenerate('20mark')}>Generate 20-Mark Answer</button>
          <button disabled={loading} onClick={() => handleGenerate('summarize')}>Summarize Notes</button>
          <button disabled={loading} onClick={() => handleGenerate('explain')}>Explain Simply</button>
        </div>

        {loading && <p className="loading">Generating content... please wait.</p>}
        {error && <p className="error-message">{error}</p>}

        {response && !loading && (
          <div className="output-section">
            <div className="output-header">
              <h3>Result</h3>
              <button className="copy-btn" onClick={copyToClipboard}>Copy Text</button>
            </div>
            <div className="output-content">
              <ReactMarkdown>{response}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
