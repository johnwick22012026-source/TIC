import "../styles/global.css"

const scoreData = [
  { label: "X Wins", value: 7 },
  { label: "O Wins", value: 5 },
  { label: "Draws", value: 3 },
]

const boardCells = Array.from({ length: 9 }, () => "")

export default function LandingPage() {
  return (
    <div className="page">
      <div className="game-shell">
        <header className="title-area">
          <p className="eyebrow">Classic Strategy</p>
          <h1>Tic-Tac-Toe Arena</h1>
          <p className="subtitle">
            Fast, polished gameplay that keeps you focused on the board and the
            scoreboard in one tidy view.
          </p>
        </header>

        <section className="board-region" aria-label="Tic tac toe board placeholder">
          <div className="board-grid">
            {boardCells.map((_, index) => (
              <div key={index} className="board-cell" aria-hidden="true" />
            ))}
          </div>
        </section>

        <div className="status-area">
          <p className="status-text">Player X&apos;s turn · Computer ready</p>
          <button className="new-game">New Game</button>
        </div>

        <section className="scoreboard">
          <h2>Scoreboard</h2>
          <div className="score-grid">
            {scoreData.map((stat) => (
              <article key={stat.label} className="score-card">
                <p className="score-label">{stat.label}</p>
                <p className="score-value">{stat.value}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
