import { useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';

/**
 * Component: ActionButton
 * Purpose: Reusable accessible button with consistent styling.
 */
const ActionButton = ({ onClick, label, variant = 'primary', disabled }) => (
  <button 
    className={`btn btn-${variant}`} 
    onClick={onClick} 
    disabled={disabled}
    aria-label={label}
  >
    {label}
  </button>
);

/**
 * Component: OutputSection
 * Purpose: Display AI results with copy-to-clipboard functionality.
 */
const OutputSection = ({ content, onCopy }) => (
  <section className="output-section" aria-live="polite">
    <div className="output-header">
      <h2 id="output-title">Study Guide</h2>
      <button 
        className="copy-btn" 
        onClick={() => onCopy(content)}
        aria-label="Copy generated text to clipboard"
      >
        Copy Text
      </button>
    </div>
    <div className="output-content" aria-labelledby="output-title">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  </section>
);

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Use a relative URL which works with the FastAPI proxy/mount
  const API_URL = '/generate';

  const handleGenerate = async (type) => {
    if (!input.trim() || input.length < 5) {
      setError('Please enter at least 5 characters to generate a quality answer.');
      return;
    }

    setLoading(true);
    setResponse('');
    setError('');

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input, type: type }),
      });

      const data = await res.json();

      if (res.ok) {
        setResponse(data.response);
      } else {
        throw new Error(data.detail || 'The AI service is busy. Please try again.');
      }
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Content copied to clipboard!');
    });
  };

  return (
    <div className="app-container">
      <header>
        <h1>AI Study Assistant</h1>
        <p>Expertly structured study materials powered by Google Gemini</p>
      </header>

      <main className="card">
        <section className="input-section">
          <label htmlFor="study-input" className="sr-only">Enter study topic or notes</label>
          <textarea
            id="study-input"
            placeholder="Paste your notes or enter a question here (e.g., 'What is Photosynthesis?')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            aria-required="true"
          />

          <div className="button-group">
            <ActionButton 
              label="10-Mark Answer" 
              onClick={() => handleGenerate('10mark')} 
              disabled={loading}
            />
            <ActionButton 
              label="20-Mark Answer" 
              onClick={() => handleGenerate('20mark')} 
              disabled={loading}
            />
            <ActionButton 
              label="Summarize" 
              variant="secondary"
              onClick={() => handleGenerate('summarize')} 
              disabled={loading}
            />
            <ActionButton 
              label="Explain Simply" 
              variant="accent"
              onClick={() => handleGenerate('explain')} 
              disabled={loading}
            />
          </div>
        </section>

        {loading && (
          <div className="loader" aria-busy="true">
            <div className="spinner"></div>
            <p>Our AI is crafting your study guide...</p>
          </div>
        )}

        {error && (
          <div className="error-box" role="alert">
            <p>{error}</p>
          </div>
        )}

        {response && !loading && (
          <OutputSection content={response} onCopy={copyToClipboard} />
        )}
      </main>

      <footer>
        <p>&copy; {new Date().getFullYear()} AI Study Assistant | Built with Google Gemini 1.5 Flash</p>
      </footer>
    </div>
  );
}

export default App;
