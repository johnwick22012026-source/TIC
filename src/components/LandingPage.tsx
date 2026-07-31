import React, { useState } from "react"
import "../styles/global.css"
import Board from "./Board"
import Scoreboard from "./Scoreboard"

const initialBoard = Array.from({ length: 9 }, () => "")
const scoreData = [
  { label: "X Wins", value: 7 },
  { label: "O Wins", value: 5 },
  { label: "Draws", value: 3 },
]

export default function LandingPage() {
  const [board, setBoard] = useState<string[]>(initialBoard)
  const [busy, setBusy] = useState(false)

  const handleCellClick = (index: number) => {
    if (busy || board[index]) return
    // Place X immediately
    const boardAfterX = [...board]
    boardAfterX[index] = "X"
    setBoard(boardAfterX)
    setBusy(true)
    // Simulate computer thinking and place O
    setTimeout(() => {
      const available = boardAfterX.reduce<number[]>((acc, val, idx) => (!val ? [...acc, idx] : acc), [])
      if (available.length > 0) {
        const oIndex = available[Math.floor(Math.random() * available.length)]
        const boardAfterO = [...boardAfterX]
        boardAfterO[oIndex] = "O"
        setBoard(boardAfterO)
      }
      setBusy(false)
    }, 500)
  }

  const handleNewGame = () => {
    if (busy) return
    setBoard(initialBoard)
    setBusy(false)
  }

  const statusText = busy
    ? "Computer is thinking..."
    : "Player X's turn · Computer ready"

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
          cells={board}
          heading="3 × 3 Battle Grid"
          description="Place your move and await the computer response."
          onCellClick={handleCellClick}
        />

        <div className="status-area">
          <p className="status-text">{statusText}</p>
          <button className="new-game" onClick={handleNewGame} disabled={busy}>
            New Game
          </button>
        </div>

        <Scoreboard
          stats={scoreData}
          description="Persistent win/draw totals keep your progress visible."
        />
      </div>
    </div>
  )
}
