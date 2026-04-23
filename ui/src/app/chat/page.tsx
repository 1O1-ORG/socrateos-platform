'use client';

import { useRef, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Message = {
  role: 'user' | 'system';
  content: string;
  stepNum?: number;
};

const STEP_LABELS = [
  'Clarifying the Claim',
  'Surfacing Assumptions',
  'Introducing Tension',
  'Forcing a Tradeoff',
  'Synthesizing a Position',
];

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [originalInput, setOriginalInput] = useState('');
  const [synthesis, setSynthesis] = useState('');

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }, 60);
  };

  const startSession = async (text: string) => {
    setMessages([{ role: 'user', content: text }]);
    setOriginalInput(text);
    setIsLoading(true);
    setInput('');
    scrollToBottom();

    try {
      const res = await fetch(`${API_URL}/api/dialectic/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: text }),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Session start failed');

      setSessionId(data.session_id);
      setCurrentStep(data.state?.loop_step ?? 1);
      setIsComplete(Boolean(data.state?.is_complete));
      setMessages([
        { role: 'user', content: text },
        { role: 'system', content: data.response, stepNum: 1 },
      ]);
      if (data.state?.is_complete) {
        setSynthesis(data.response || '');
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: 'An error occurred starting the session. Check console for details.' },
      ]);
    } finally {
      setIsLoading(false);
      scrollToBottom();
      inputRef.current?.focus();
    }
  };

  const continueSession = async (text: string) => {
    if (!sessionId) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setIsLoading(true);
    setInput('');
    scrollToBottom();

    try {
      const res = await fetch(`${API_URL}/api/dialectic/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, user_response: text }),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Session step failed');

      const step = data.state?.loop_step ?? currentStep;
      const complete = Boolean(data.state?.is_complete);
      setCurrentStep(step);
      setIsComplete(complete);
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: data.response, stepNum: step },
      ]);
      if (complete) {
        setSynthesis(data.response || '');
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: 'An error occurred. Check console for details.' },
      ]);
    } finally {
      setIsLoading(false);
      scrollToBottom();
      inputRef.current?.focus();
    }
  };

  const handleSubmit = () => {
    const text = input.trim();
    if (!text || isLoading || isComplete) return;
    if (!sessionId) {
      void startSession(text);
    } else {
      void continueSession(text);
    }
  };

  const reset = () => {
    setMessages([]);
    setSessionId(null);
    setIsLoading(false);
    setIsComplete(false);
    setCurrentStep(0);
    setOriginalInput('');
    setSynthesis('');
    setInput('');
    inputRef.current?.focus();
  };

  return (
    <main className="chat-page">
      <header className="chat-header">
        <a href="/" className="chat-logo">SocrateOS</a>
        <div className="chat-step-indicator">
          {currentStep > 0 && !isComplete && (
            <span>Step {currentStep} of 5 — {STEP_LABELS[currentStep - 1]}</span>
          )}
          {isComplete && <span>Session Complete</span>}
        </div>
      </header>

      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <svg viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <h2>What&apos;s on your mind?</h2>
            <p>
              Share a thought, question, or dilemma. Socrates will guide you through
              a structured five-step dialectic from raw idea to refined clarity.
            </p>
          </div>
        )}

        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`chat-msg ${m.role === 'user' ? 'chat-msg-user' : 'chat-msg-system'}`}
          >
            {m.role === 'system' && m.stepNum && (
              <div className="chat-step-label">
                <span className="chat-step-dot" />
                Step {m.stepNum}: {STEP_LABELS[(m.stepNum - 1) % 5]}
              </div>
            )}
            <div className="chat-bubble">{m.content}</div>
          </div>
        ))}

        {isComplete && (
          <div className="chat-completion">
            <div className="chat-completion-bar" />
            <h3>Session Complete</h3>
            <div className="chat-completion-grid">
              <div>
                <div className="chat-completion-label">You started with</div>
                <div className="chat-completion-text chat-original">{originalInput}</div>
              </div>
              <div>
                <div className="chat-completion-label">You arrived at</div>
                <div className="chat-completion-text chat-synthesis">{synthesis}</div>
              </div>
            </div>
            <button className="btn btn-primary" onClick={reset} id="chat-new-session">
              Start a New Session
            </button>
          </div>
        )}
      </div>

      {isLoading && (
        <div className="chat-thinking">
          <span className="thinking-dot" />
          <span className="thinking-dot" />
          <span className="thinking-dot" />
          <span>Socrates is thinking...</span>
        </div>
      )}

      <div className="chat-input-area">
        <div className="chat-input-wrap">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Type your thought here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            disabled={isLoading || isComplete}
          />
          <button
            className="chat-send"
            onClick={handleSubmit}
            disabled={isLoading || isComplete || !input.trim()}
            id="chat-send-btn"
          >
            Continue
            <svg viewBox="0 0 24 24">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
}
