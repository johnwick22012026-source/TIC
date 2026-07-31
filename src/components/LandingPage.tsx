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

const findWinningCells = (cells: string[]): number[] | null => {
  for (const line of WIN_LINES) {
    const [a, b, c] = line
    const value = cells[a]
    if (value && value === cells[b] && value === cells[c]) {
      return [a, b, c]
    }
  }
  return null
}

type ResetPayload = {
  board: string[]
  status: GameStatus
  winning_cells?: number[]
}

export default function LandingPage() {
  const [board, setBoard] = useState<string[]>(initialBoard)
  const [busy, setBusy] = useState(false)
  const [gameStatus, setGameStatus] = useState<GameStatus>("in_progress")
  const [winningCells, setWinningCells] = useState<number[] | null>(null)

  const applyResetState = ({ board, status, winning_cells }: ResetPayload) => {
    setBoard(board)
    setGameStatus(status)
    setWinningCells(winning_cells && winning_cells.length > 0 ? winning_cells : null)
  }

  const handleCellClick = (index: number) => {
    if (busy || board[index] || gameStatus !== "in_progress") return

    const boardAfterX = [...board]
    boardAfterX[index] = "X"
    setBoard(boardAfterX)

    const statusAfterX = evaluateBoard(boardAfterX)
    const winningAfterX =
      statusAfterX === "x_win" || statusAfterX === "o_win"
        ? findWinningCells(boardAfterX)
        : null

    setGameStatus(statusAfterX)
    setWinningCells(winningAfterX)

    if (statusAfterX !== "in_progress") {
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
        const winningAfterO =
          statusAfterO === "x_win" || statusAfterO === "o_win"
            ? findWinningCells(boardAfterO)
            : null

        setGameStatus(statusAfterO)
        setWinningCells(winningAfterO)
      } else {
        setGameStatus("draw")
        setWinningCells(null)
      }

      setBusy(false)
    }, 500)
  }

  const handleNewGame = async () => {
    if (busy) return
    setBusy(true)

    try {
      const response = await fetch("/api/play/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })

      if (!response.ok) {
        throw new Error("Unable to reset game via backend")
      }

      const data = (await response.json()) as {
        board: string[]
        status: GameStatus
        winning_cells?: number[]
      }

      applyResetState({
        board: data.board,
        status: data.status,
        winning_cells: data.winning_cells,
      })
    } catch (error) {
      console.error("Reset request failed:", error)
      applyResetState({
        board: Array.from({ length: 9 }, () => ""),
        status: "in_progress",
        winning_cells: null,
      })
    } finally {
      setBusy(false)
    }
  }

  const isTerminalGame = gameStatus !== "in_progress"

  const statusText = (() => {
    if (gameStatus === "x_win") return "X won the round! Eyes on the highlighted line."
    if (gameStatus === "o_win") return "O won this heat! Check the glowing cells."
    if (gameStatus === "draw") return "Draw! The board filled without a winning line."
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
          winningCells={winningCells ?? undefined}
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
