
import { useRef, useState } from "react";
import "./App.css";

const initialMessages = [
  {
    role: "assistant",
    text: "Hi! I'm your DocuMind AI assistant. Upload your documents and ask me questions about them.",
  },
];

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState(initialMessages);
  const [search, setSearch] = useState("");
  const [documents, setDocuments] = useState([]);
  const [notice, setNotice] = useState("");
  const fileInputRef = useRef(null);

  const filteredDocuments = documents.filter((doc) =>
    doc.name.toLowerCase().includes(search.toLowerCase())
  );

  function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const validType = /\.(pdf|txt)$/i.test(file.name);
    if (!validType) {
      setNotice("Please choose a PDF or TXT file.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setNotice("The file must be smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
    setNotice("");
  }

  function handleUpload() {
    if (!selectedFile) {
      fileInputRef.current?.click();
      return;
    }

    // Demo only: connect this action to the FastAPI upload endpoint.
    const exists = documents.some(
      (doc) => doc.name === selectedFile.name
    );

    if (exists) {
      setNotice("This filename is already in the demo document list.");
      return;
    }

    setDocuments((current) => [
      ...current,
      {
        id: `${Date.now()}-${selectedFile.name}`,
        name: selectedFile.name,
        size: selectedFile.size,
        status: "Demo upload",
      },
    ]);

    setNotice(
      `${selectedFile.name} was added to the demo list. Backend upload is not connected yet.`
    );
    setSelectedFile(null);

    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleAsk(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text) return;

    setMessages((current) => [
      ...current,
      { role: "user", text },
      {
        role: "assistant",
        text: "Your question is ready, but the AI backend is not connected yet. Once the FastAPI chat endpoint is available, answers can be generated from your uploaded documents.",
      },
    ]);
    setQuestion("");
  }

  const totalDocuments = documents.length;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#dashboard">
          <span className="brand-mark">◆</span>
          <span>
            <strong>DocuMind <em>AI</em></strong>
            <small>YOUR KNOWLEDGE WORKSPACE</small>
          </span>
        </a>

        <nav className="side-nav" aria-label="Main navigation">
          <a className="nav-link active" href="#dashboard">
            <span className="nav-icon">⌂</span> Dashboard
          </a>
          <a className="nav-link" href="#documents">
            <span className="nav-icon">▤</span> Documents
          </a>
          <a className="nav-link" href="#assistant">
            <span className="nav-icon">▢</span> AI Assistant
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="avatar">D</div>
          <div>
            <strong>Team Workspace</strong>
            <small>TRICITY AI-Thon</small>
          </div>
          <span className="sidebar-chevron">›</span>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <label className="global-search">
            <span>⌕</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search documents, ask questions..."
              aria-label="Search documents"
            />
            <kbd>Ctrl + K</kbd>
          </label>

          <div className="topbar-profile">
            <span className="notification" aria-label="Notifications">♧</span>
            <div className="avatar small-avatar">D</div>
            <strong>Team Workspace</strong>
            <span>⌄</span>
          </div>
        </header>

        {notice && (
          <div className="notice" role="status">
            <span>{notice}</span>
            <button onClick={() => setNotice("")} aria-label="Dismiss message">
              ×
            </button>
          </div>
        )}

        <div className="dashboard-grid">
          <div className="dashboard-main">
            <section className="hero">
              <div className="hero-copy">
                <span className="tag">✦ AI-POWERED KNOWLEDGE</span>
                <h1>
                  Your knowledge,
                  <br />
                  <span>one conversation away.</span>
                </h1>
                <p>
                  Upload documents, ask questions, and get instant
                  insights from your files with DocuMind AI.
                </p>
                <button
                  className="primary-button hero-button"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <span>⇧</span> Upload Document <span>→</span>
                </button>
              </div>

              <div className="hero-illustration" aria-hidden="true">
                <div className="floating-label">Find answers<br />from your files</div>
                <div className="document-sheet pdf-sheet">
                  <b>PDF</b>
                  <i />
                  <i />
                  <i />
                </div>
                <div className="document-sheet text-sheet">
                  <i />
                  <i />
                  <i />
                  <i />
                </div>
                <div className="ai-sheet">
                  <span>✦</span>
                  <strong>AI</strong>
                  <small>Knowledge engine</small>
                </div>
              </div>
            </section>

            <section className="stats-grid" aria-label="Document statistics">
              <article className="stat-card">
                <div className="stat-icon purple-icon">▤</div>
                <div>
                  <p>Total Documents</p>
                  <strong>{totalDocuments}</strong>
                  <small>PDFs &amp; TXT files</small>
                </div>
              </article>
              <article className="stat-card">
                <div className="stat-icon green-icon">✓</div>
                <div>
                  <p>Processed</p>
                  <strong>0</strong>
                  <small>Ready for queries</small>
                </div>
              </article>
              <article className="stat-card">
                <div className="stat-icon orange-icon">◷</div>
                <div>
                  <p>Processing</p>
                  <strong>0</strong>
                  <small>Being analyzed</small>
                </div>
              </article>
              <article className="stat-card">
                <div className="stat-icon blue-icon">☁</div>
                <div>
                  <p>Storage Used</p>
                  <strong>
                    {(
                      documents.reduce((sum, doc) => sum + doc.size, 0) /
                      (1024 * 1024)
                    ).toFixed(2)}{" "}
                    MB
                  </strong>
                  <small>Demo browser session</small>
                </div>
              </article>
            </section>

            <section className="lower-grid">
              <article className="panel recent-documents" id="documents">
                <div className="panel-heading">
                  <div className="heading-icon">▤</div>
                  <div>
                    <h2>Recent Documents</h2>
                    <p>Your latest uploaded files</p>
                  </div>
                  <a href="#documents">View all <span>→</span></a>
                </div>

                {filteredDocuments.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-folder">▱</div>
                    <strong>
                      {search ? "No matching documents" : "No documents yet"}
                    </strong>
                    <p>
                      {search
                        ? "Try a different search term."
                        : "Upload your first document to get started with DocuMind AI."}
                    </p>
                    {!search && (
                      <button
                        className="primary-button"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        ⇧ &nbsp; Upload Document
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="document-list">
                    {filteredDocuments.map((doc) => (
                      <div className="document-row" key={doc.id}>
                        <div className="document-file-icon">▤</div>
                        <div className="document-info">
                          <strong>{doc.name}</strong>
                          <small>
                            {(doc.size / 1024).toFixed(1)} KB · {doc.status}
                          </small>
                        </div>
                        <span className="demo-badge">Demo</span>
                      </div>
                    ))}
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  className="hidden-file-input"
                  type="file"
                  accept=".pdf,.txt,application/pdf,text/plain"
                  onChange={handleFileChange}
                />

                {selectedFile && (
                  <div className="selected-file">
                    <span>Selected: {selectedFile.name}</span>
                    <button
                      className="primary-button"
                      onClick={handleUpload}
                    >
                      Add to demo list
                    </button>
                  </div>
                )}
              </article>

              <article className="panel assistant-panel" id="assistant">
                <div className="panel-heading">
                  <div className="heading-icon chat-heading-icon">▢</div>
                  <div>
                    <h2>AI Assistant</h2>
                    <p>Ask questions and get instant answers</p>
                  </div>
                </div>

                <div className="chat-messages" aria-live="polite">
                  {messages.map((message, index) => (
                    <div
                      className={`message-row ${message.role}`}
                      key={`${message.role}-${index}`}
                    >
                      {message.role === "assistant" && (
                        <div className="bot-avatar">✳</div>
                      )}
                      <div className="message-bubble">{message.text}</div>
                    </div>
                  ))}
                </div>

                <div className="suggestion-list">
                  <button onClick={() => setQuestion("Summarize my document")}>
                    Summarize this document
                  </button>
                  <button onClick={() => setQuestion("Find the key points")}>
                    Find key points
                  </button>
                  <button onClick={() => setQuestion("What are the main topics?")}>
                    What are the main topics?
                  </button>
                </div>

                <form className="chat-form" onSubmit={handleAsk}>
                  <input
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="Ask a question..."
                    aria-label="Ask the AI assistant"
                  />
                  <button type="submit" aria-label="Send question">➤</button>
                </form>
                <p className="demo-disclaimer">
                  Demo chat · Connect the backend for AI answers
                </p>
              </article>
            </section>
          </div>

          <aside className="right-column">
            <section className="workspace-status">
              <div className="status-check">✓</div>
              <div>
                <strong>Workspace Ready</strong>
                <p>Everything is running smoothly!</p>
              </div>
            </section>

            <section className="panel quick-actions">
              <h2>Quick Actions</h2>
              <button onClick={() => fileInputRef.current?.click()}>
                <span className="quick-icon">⇧</span>
                <strong>Upload Document</strong>
                <span className="action-arrow">›</span>
              </button>
              <a href="#assistant">
                <span className="quick-icon">▢</span>
                <strong>Ask AI Assistant</strong>
                <span className="action-arrow">›</span>
              </a>
              <a href="#documents">
                <span className="quick-icon">▱</span>
                <strong>View Documents</strong>
                <span className="action-arrow">›</span>
              </a>
            </section>

            <section className="panel activity-panel">
              <h2><span>◷</span> Recent Activity</h2>
              {documents.length === 0 ? (
                <div className="activity-empty">
                  <span className="activity-icon">✧</span>
                  <div>
                    <strong>No recent activity</strong>
                    <p>Your document activity will appear here.</p>
                  </div>
                </div>
              ) : (
                documents.slice().reverse().map((doc) => (
                  <div className="activity-item" key={doc.id}>
                    <span className="activity-icon">⇧</span>
                    <div>
                      <strong>Document selected</strong>
                      <p>{doc.name}</p>
                    </div>
                    <small>Now</small>
                  </div>
                ))
              )}
              <div className="activity-item">
                <span className="activity-icon blue-activity">▢</span>
                <div>
                  <strong>Assistant ready</strong>
                  <p>Chat interface available</p>
                </div>
              </div>
            </section>

            <section className="insights-card">
              <div className="insight-bulb">☼</div>
              <div>
                <strong>Better insights. Faster.</strong>
                <p>
                  Turn your documents into knowledge with the power of AI.
                </p>
              </div>
              <div className="insight-wave" />
            </section>
          </aside>
        </div>

        <footer className="page-footer">
          <strong>DocuMind AI</strong>
          <span>Built for TRICITY AI-Thon</span>
        </footer>
      </main>
    </div>
  );
}
