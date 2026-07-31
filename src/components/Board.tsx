export interface BoardProps {
  cells?: string[]
  heading?: string
  description?: string
  onCellClick?: (index: number) => void
  disabled?: boolean
}

const defaultCells = Array.from({ length: 9 }, () => "")

export default function Board({
  cells = defaultCells,
  heading,
  description,
  onCellClick,
  disabled = false,
}: BoardProps) {
  const isInteractive = typeof onCellClick === "function" && !disabled

  return (
    <section className="board-panel" aria-label="Tic tac toe board">
      {heading && <h2>{heading}</h2>}
      {description && <p className="board-description">{description}</p>}
      <div className="board-grid" role="grid">
        {cells.map((value, index) => (
          <button
            key={index}
            type="button"
            className="board-cell"
            onClick={() => onCellClick?.(index)}
            disabled={disabled || !isInteractive || Boolean(value)}
            aria-label={`Cell ${index + 1} ${value ? `holds ${value}` : "is empty"}`}
          >
            <span className="board-symbol">{value}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
