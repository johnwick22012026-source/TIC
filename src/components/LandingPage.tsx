import "../styles/global.css"
import Board from "./Board"
import Scoreboard from "./Scoreboard"

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

        <Board
          cells={boardCells}
          heading="3 × 3 Battle Grid"
          description="Place your move and await the computer response."
        />

        <div className="status-area">
          <p className="status-text">Player X&apos;s turn · Computer ready</p>
          <button className="new-game">New Game</button>
        </div>

        <Scoreboard
          stats={scoreData}
          description="Persistent win/draw totals keep your progress visible."
        />
      </div>
    </div>
  )
}
