import React, { useState, useEffect, useCallback } from "react"
import "../styles/global.css"
import Board from "./Board"
import Scoreboard, { ScoreStat } from "./Scoreboard"

const initialBoard = Array.from({ length: 9 }, () => "")

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

type SubmissionStatus = "idle" | "pending" | "success" | "error"

export default function LandingPage() {
  const [board, setBoard] = useState<string[]>(initialBoard)
  const [busy, setBusy] = useState(false)
  const [gameStatus, setGameStatus] = useState<GameStatus>("in_progress")
  const [winningCells, setWinningCells] = useState<number[] | null>(null)

  const [scoreStats, setScoreStats] = useState<ScoreStat[]>([])
  const [scoreLoading, setScoreLoading] = useState(true)
  const [scoreError, setScoreError] = useState<string | null>(null)

  const [resultSubmissionStatus, setResultSubmissionStatus] = useState<SubmissionStatus>("idle")
  const [resultSubmissionError, setResultSubmissionError] = useState<string | null>(null)
  const [lastSubmittedKey, setLastSubmittedKey] = useState<string | null>(null)

  const placeholderStats: ScoreStat[] = [
    { label: "X Wins", value: "—" },
    { label: "O Wins", value: "—" },
    { label: "Draws", value: "—" },
  ]

  const fetchScores = useCallback(async () => {
    setScoreLoading(true)
    setScoreError(null)
    try {
      const res = await fetch("/api/games/scoreboard")
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const stats: ScoreStat[] = [
        { label: "X Wins", value: data.x_wins },
        { label: "O Wins", value: data.o_wins },
        { label: "Draws", value: data.draws },
      ]
      setScoreStats(stats)
    } catch (err) {
      console.error("Failed to load scoreboard totals:", err)
      setScoreError("Unable to load scoreboard")
    } finally {
      setScoreLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchScores()
  }, [fetchScores])

  const applyResetState = ({ board, status, winning_cells }: ResetPayload) => {
    setBoard(board)
    setGameStatus(status)
    setWinningCells(winning_cells && winning_cells.length > 0 ? winning_cells : null)
    setResultSubmissionStatus("idle")
    setResultSubmissionError(null)
    setLastSubmittedKey(null)
  }

  const submitGameResult = useCallback(() => {
    if (gameStatus === "in_progress") {
      return
    }

    const winner =
      gameStatus === "x_win" ? "X" : gameStatus === "o_win" ? "O" : "draw"
    const key = `${winner}-${board.join("")}`

    if (lastSubmittedKey === key) {
      return
    }

    setLastSubmittedKey(key)
    setResultSubmissionStatus("pending")
    setResultSubmissionError(null)

    const payload = {
      winner,
      board_snapshot: JSON.stringify(board),
      completed_at: new Date().toISOString(),
    }

    fetch("/api/games", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }
        return res.json()
      })
      .then(() => {
        setResultSubmissionStatus("success")
        fetchScores()
      })
      .catch((err) => {
        console.error("Failed to submit game result:", err)
        setResultSubmissionError("Unable to persist this round. Try again shortly.")
        setResultSubmissionStatus("error")
      })
  }, [board, fetchScores, gameStatus, lastSubmittedKey])

  useEffect(() => {
    submitGameResult()
  }, [submitGameResult])

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

  const submissionText = (() => {
    if (!isTerminalGame) return null
    if (resultSubmissionStatus === "pending") return "Submitting result to the scoreboard..."
    if (resultSubmissionStatus === "error") return resultSubmissionError
    if (resultSubmissionStatus === "success") return "Result saved to persistent scoreboard."
    return null
  })()

  const displayStats = scoreLoading || scoreError ? placeholderStats : scoreStats
  const scoreboardDescription = scoreLoading
    ? "Loading scoreboard totals..."
    : scoreError
    ? "Error loading scoreboard totals"
    : "Persistent win/draw totals keep your progress visible."

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
          <div>
            <p className="status-text" aria-live="polite">
              {statusText}
            </p>
            {submissionText && (
              <p
                className={`submission-text$ {
                  resultSubmissionStatus === "error" ? " submission-text--error" : ""
                }`}
                aria-live={resultSubmissionStatus === "error" ? "assertive" : "polite"}
              >
                {submissionText}
              </p>
            )}
          </div>
          <button className="new-game" onClick={handleNewGame} disabled={busy}>
            New Game
          </button>
        </div>

        <Scoreboard
          stats={displayStats}
          description={scoreboardDescription}
        />
      </div>
    </div>
  )
}
