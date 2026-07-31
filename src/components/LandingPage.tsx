import React, { useState, useEffect, useCallback, useRef } from "react"
import "../styles/global.css"
import Board from "./Board"
import Scoreboard, { ScoreStat } from "./Scoreboard"

const initialBoard = Array.from({ length: 9 }, () => "")

type GameStatus = "in_progress" | "x_win" | "o_win" | "draw"
type GameMode = "single" | "versus"

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

const MODE_OPTIONS: Array<{ value: GameMode; label: string }> = [
  { value: "single", label: "1 vs Computer" },
  { value: "versus", label: "1 vs 1" },
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
  const [gameMode, setGameMode] = useState<GameMode>("single")
  const [currentPlayer, setCurrentPlayer] = useState<"X" | "O">("X")

  const [scoreStats, setScoreStats] = useState<ScoreStat[]>([])
  const [scoreLoading, setScoreLoading] = useState(true)
  const [scoreError, setScoreError] = useState<string | null>(null)

  const [resultSubmissionStatus, setResultSubmissionStatus] = useState<SubmissionStatus>("idle")
  const [resultSubmissionError, setResultSubmissionError] = useState<string | null>(null)
  const lastSubmittedKeyRef = useRef<string | null>(null)
  const computerMoveTimeoutRef = useRef<number | null>(null)

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

  // Clear any pending computer move when component unmounts
  useEffect(() => {
    return () => {
      if (computerMoveTimeoutRef.current) {
        clearTimeout(computerMoveTimeoutRef.current)
      }
    }
  }, [])

  // Clear pending computer move on mode change
  useEffect(() => {
    if (computerMoveTimeoutRef.current) {
      clearTimeout(computerMoveTimeoutRef.current)
      computerMoveTimeoutRef.current = null
    }
  }, [gameMode])

  const applyResetState = ({ board, status, winning_cells }: ResetPayload) => {
    setBoard(board)
    setGameStatus(status)
    setWinningCells(winning_cells && winning_cells.length > 0 ? winning_cells : null)
    setResultSubmissionStatus("idle")
    setResultSubmissionError(null)
    lastSubmittedKeyRef.current = null
    setBusy(false)
    setCurrentPlayer("X")
  }

  const submitGameResult = useCallback(() => {
    if (gameStatus === "in_progress") {
      return
    }

    const winner =
      gameStatus === "x_win" ? "X" : gameStatus === "o_win" ? "O" : "draw"
    const key = `${winner}-${board.join("")}`

    if (lastSubmittedKeyRef.current === key) {
      return
    }

    lastSubmittedKeyRef.current = key
    setResultSubmissionStatus("pending")
    setResultSubmissionError(null)

    const payload = {
      winner,
      board_snapshot: JSON.stringify(board),
      completed_at: new Date().toISOString(),
      mode: gameMode,
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
  }, [board, fetchScores, gameMode, gameStatus])

  useEffect(() => {
    submitGameResult()
  }, [submitGameResult])

  const handleCellClick = (index: number) => {
    if (busy || board[index] || gameStatus !== "in_progress") return

    const isSinglePlayer = gameMode === "single"
    const symbolToPlace = isSinglePlayer ? "X" : currentPlayer
    const boardAfterMove = [...board]
    boardAfterMove[index] = symbolToPlace
    setBoard(boardAfterMove)

    const statusAfterMove = evaluateBoard(boardAfterMove)
    const winningAfterMove =
      statusAfterMove === "x_win" || statusAfterMove === "o_win"
        ? findWinningCells(boardAfterMove)
        : null

    setGameStatus(statusAfterMove)
    setWinningCells(winningAfterMove)

    if (statusAfterMove !== "in_progress") {
      if (!isSinglePlayer) {
        setCurrentPlayer("X")
      }
      setBusy(false)
      return
    }

    if (isSinglePlayer) {
      setBusy(true)
      // Schedule computer move and store timeout ID
      computerMoveTimeoutRef.current = window.setTimeout(() => {
        const available = boardAfterMove.reduce<number[]>((acc, val, idx) => (
          !val ? [...acc, idx] : acc
        ), [])

        if (available.length > 0) {
          const oIndex = available[Math.floor(Math.random() * available.length)]
          const boardAfterO = [...boardAfterMove]
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
        computerMoveTimeoutRef.current = null
      }, 500)
      return
    }

    setCurrentPlayer((prev) => (prev === "X" ? "O" : "X"))
  }

  const handleNewGame = async () => {
    if (busy) return
    setBusy(true)

    const params = new URLSearchParams({ mode: gameMode })

    try {
      const response = await fetch(`/api/play/reset?${params.toString()}`, {
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
    if (gameMode === "single") {
      if (busy) return "Computer is thinking..."
      return "Player X's turn · Computer ready"
    }
    return `Player ${currentPlayer}'s turn · Alternate corners to win.`
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

  const boardDescription =
    gameMode === "single"
      ? "Place your move and await the computer response."
      : "Players trade turns placing X and O on the 3 × 3 grid."

  const handleModeChange = (mode: GameMode) => {
    if (mode === gameMode) return
    setGameMode(mode)
    setCurrentPlayer("X")
    setBusy(false)
  }

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

        <div className="game-content">
          <div className="match-mode-group">
            <p className="match-mode-label">Match Mode</p>
            <div className="mode-options" role="radiogroup" aria-label="Select match mode">
              {MODE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  role="radio"
                  aria-checked={gameMode === option.value}
                  className={`mode-option${
                    gameMode === option.value ? " mode-option--active" : ""
                  }`}
                  onClick={() => handleModeChange(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <div className="board-status-wrapper">
            <Board
              cells={board}
              heading="3 × 3 Battle Grid"
              description={boardDescription}
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
                    className={`submission-text${
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
          </div>

          <Scoreboard stats={displayStats} description={scoreboardDescription} />
        </div>
      </div>
    </div>
  )
}
