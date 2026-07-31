export interface ScoreStat {
  label: string
  value: number | string
}

export interface ScoreboardProps {
  stats: ScoreStat[]
  heading?: string
  description?: string
}

export default function Scoreboard({
  stats,
  heading = "Scoreboard",
  description,
}: ScoreboardProps) {
  return (
    <section className="scoreboard-panel" aria-label="Scoreboard summary">
      <div className="scoreboard-heading">
        <p className="eyebrow">Results</p>
        <h2>{heading}</h2>
        {description && <p className="subtitle">{description}</p>}
      </div>
      <div className="score-grid">
        {stats.map((stat) => (
          <article key={stat.label} className="score-card">
            <p className="score-label">{stat.label}</p>
            <p className="score-value">{stat.value}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
