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
  const panelClassName = ["board-panel", disabled ? "board-panel--disabled" : ""].join(" ").trim()

  return (
    <section
      className={panelClassName}
      aria-label="Tic tac toe board"
      aria-disabled={disabled}
    >
      {heading && <h2>{heading}</h2>}
      {description && <p className="board-description">{description}</p>}
      <div className="board-grid" role="grid">
        {cells.map((value, index) => {
          const isWinningCell = winningIndexSet.has(index)
          const cellClassNames = ["board-cell"]
          if (value === "X") cellClassNames.push("board-cell--x")
          if (value === "O") cellClassNames.push("board-cell--o")
          if (isWinningCell) cellClassNames.push("board-cell--winning")

          const symbolClassNames = ["board-symbol"]
          if (value === "X") symbolClassNames.push("board-symbol--x")
          if (value === "O") symbolClassNames.push("board-symbol--o")

          return (
            <button
              key={index}
              type="button"
              className={cellClassNames.join(" ")}
              data-value={value}
              onClick={() => onCellClick?.(index)}
              disabled={disabled || !isInteractive || Boolean(value)}
              aria-label={`Cell ${index + 1} ${value ? `holds ${value}` : "is empty"}`}
            >
              <span className={symbolClassNames.join(" ")}>{value}</span>
            </button>
          )
        })}
      </div>
    </section>
  )
}
