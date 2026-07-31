import "../styles/global.css"

const sampleBoard = [
  "X",
  "O",
  "",
  "",
  "X",
  "",
  "O",
  "",
  "X",
]

const mockStats = [
  { label: "X Wins", value: 7 },
  { label: "O Wins", value: 5 },
  { label: "Draws", value: 3 },
]

export default function LandingPage() {
  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Tic-Tac-Toe Arena</p>
        <h1>Fast-paced React gameplay, no backend delays.</h1>
        <p>
          Challenge the computer and track wins with a lightweight Vite + React
          scaffold that’s ready to scale into the full scoreboard experience.
        </p>
        <div className="hero-actions">
          <button className="primary">Start New Game</button>
          <button className="ghost">View Scoreboard</button>
        </div>
      </header>

      <section className="board-section">
        <h2>Active Board</h2>
        <div className="board-grid" aria-label="Sample tic tac toe board">
          {sampleBoard.map((cell, index) => (
            <div key={index} className={`board-cell ${cell ? "occupied" : ""}`}>
              {cell || ""}
            </div>
          ))}
        </div>
        <p className="board-status">
          Player X&apos;s turn · Computer thinking...
        </p>
      </section>

      <section className="stats-section">
        <h2>Scoreboard Snapshot</h2>
        <div className="stats-grid">
          {mockStats.map((stat) => (
            <article key={stat.label} className="stat-card">
              <p className="stat-label">{stat.label}</p>
              <p className="stat-value">{stat.value}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
