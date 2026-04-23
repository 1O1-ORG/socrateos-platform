import Link from 'next/link';

const STEPS = [
  {
    num: '01',
    title: 'Clarify the Claim',
    desc: 'Narrow ambiguity. Surface what feels unresolved.',
  },
  {
    num: '02',
    title: 'Surface Assumptions',
    desc: 'Identify hidden beliefs taken for granted without examination.',
  },
  {
    num: '03',
    title: 'Introduce Tension',
    desc: 'Present a genuine counterpoint that creates cognitive dissonance.',
  },
  {
    num: '04',
    title: 'Force a Tradeoff',
    desc: 'Choose between competing values. Make the stakes personal.',
  },
  {
    num: '05',
    title: 'Synthesize a Position',
    desc: 'Show how thinking evolved. End with a concrete next step.',
  },
];

export default function HomePage() {
  return (
    <main className="landing">
      <section className="hero">
        <div className="hero-badge">Open-Core Dialectic Engine</div>
        <h1 className="hero-title">
          Think Harder.<br />
          <span className="hero-accent">Not Faster.</span>
        </h1>
        <p className="hero-subtitle">
          SocrateOS doesn&apos;t answer your questions. It makes you confront
          what you&apos;re actually asking. Five steps from raw thought to
          actionable clarity.
        </p>
        <div className="hero-actions">
          <Link href="/chat" className="btn btn-primary" id="hero-start-session">
            Start a Session
          </Link>
          <a
            href="https://github.com/1O1-ORG/socrateos-platform"
            className="btn btn-ghost"
            target="_blank"
            rel="noopener noreferrer"
            id="hero-view-source"
          >
            View Source
          </a>
        </div>
      </section>

      <section className="protocol">
        <h2 className="section-title">The Dialectic Protocol</h2>
        <p className="section-subtitle">
          Every session follows the same five-step structure. No shortcuts.
        </p>
        <div className="steps-grid">
          {STEPS.map((s) => (
            <div key={s.num} className="step-card">
              <div className="step-num">{s.num}</div>
              <h3 className="step-title">{s.title}</h3>
              <p className="step-desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-section">
        <h2 className="cta-title">Ready to think differently?</h2>
        <p className="cta-subtitle">
          Clone the repo or start a session right now. No account needed.
        </p>
        <div className="cta-actions">
          <Link href="/chat" className="btn btn-primary" id="cta-start-session">
            Start a Session
          </Link>
        </div>
        <div className="cta-code">
          <code>git clone https://github.com/1O1-ORG/socrateos-platform.git</code>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-inner">
          <span className="footer-brand">SocrateOS</span>
          <span className="footer-sep">·</span>
          <span>Apache 2.0</span>
          <span className="footer-sep">·</span>
          <a
            href="https://github.com/1O1-ORG/socrateos-platform"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </div>
      </footer>
    </main>
  );
}
