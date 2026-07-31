export interface BoardProps {
  cells?: string[]
  heading?: string
  description?: string
  onCellClick?: (index: number) => void
  disabled?: boolean
  winningCells?: number[]
}

const defaultCells = Array.from({ length: 9 }, () => "")

export default function Board({
  cells = defaultCells,
  heading,
  description,
  onCellClick,
  disabled = false,
  winningCells,
}: BoardProps) {
  const isInteractive = typeof onCellClick === "function" && !disabled
  const winningIndexSet = new Set(winningCells ?? [])
  const panelClassName = `board-panel${disabled ? " board-panel--disabled" : ""}`
  const gridClassName = `board-grid${disabled ? " board-grid--disabled" : ""}`

  return (
    <section className={panelClassName} aria-label="Tic tac toe board">
      {heading && <h2>{heading}</h2>}
      {description && <p className="board-description">{description}</p>}
      <div className={gridClassName} role="grid">
        {cells.map((value, index) => {
          const isWinningCell = winningIndexSet.has(index)
          return (
            <button
              key={index}
              type="button"
              className={`board-cell${isWinningCell ? " board-cell--winning" : ""}`}
              onClick={() => onCellClick?.(index)}
              disabled={disabled || !isInteractive || Boolean(value)}
              aria-label={`Cell ${index + 1} ${value ? `holds ${value}` : "is empty"}`}
            >
              <span className="board-symbol">{value}</span>
            </button>
          )
        })}
      </div>
    </section>
  )
}
