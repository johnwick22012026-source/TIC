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

type GameStatus = "in_progress" | "x_win" | "o_win" | "draw"

const WIN_LINES: Array<[number, number, number]> = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
]

const evaluateBoard = (cells: string[]): GameStatus => {
  for (const [a, b, c] of WIN_LINES) {
    const value = cells[a]
    if (value && value === cells[b] && value === cells[c]) {
      return value === "X" ? "x_win" : "o_win"
    }
  }

  if (cells.every((cell) => Boolean(cell))) {
    return "draw"
  }

  return "in_progress"
}

export default function LandingPage() {
  const [board, setBoard] = useState<string[]>(initialBoard)
  const [busy, setBusy] = useState(false)
  const [gameStatus, setGameStatus] = useState<GameStatus>("in_progress")

  const handleCellClick = (index: number) => {
    if (busy || board[index] || gameStatus !== "in_progress") return

    const boardAfterX = [...board]
    boardAfterX[index] = "X"
    setBoard(boardAfterX)

    const statusAfterX = evaluateBoard(boardAfterX)
    if (statusAfterX !== "in_progress") {
      setGameStatus(statusAfterX)
      setBusy(false)
      return
    }

    setBusy(true)
    setTimeout(() => {
      const available = boardAfterX.reduce<number[]>((acc, val, idx) => (
        !val ? [...acc, idx] : acc
      ), [])

      if (available.length > 0) {
        const oIndex = available[Math.floor(Math.random() * available.length)]
        const boardAfterO = [...boardAfterX]
        boardAfterO[oIndex] = "O"
        setBoard(boardAfterO)
        const statusAfterO = evaluateBoard(boardAfterO)
        setGameStatus(statusAfterO)
      } else {
        setGameStatus("draw")
      }

      setBusy(false)
    }, 500)
  }

  const handleNewGame = () => {
    if (busy) return
    setBoard(initialBoard)
    setGameStatus("in_progress")
    setBusy(false)
  }

  const isTerminalGame = gameStatus !== "in_progress"

  const statusText = (() => {
    if (gameStatus === "x_win") return "Victory! Player X has won the round."
    if (gameStatus === "o_win") return "Player O wins this heat. Ready to try again?"
    if (gameStatus === "draw") return "It's a draw—no winning line was formed."
    if (busy) return "Computer is thinking..."
    return "Player X's turn · Computer ready"
  })()

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
          disabled={busy || isTerminalGame}
        />

        <div className="status-area">
          <p className="status-text" aria-live="polite">
            {statusText}
          </p>
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
