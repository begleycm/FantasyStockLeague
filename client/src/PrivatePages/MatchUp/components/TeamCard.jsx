import styles from './TeamCard.module.css'

function TeamCard({ team, isPlayer1 }) {
  return (
    <div className={styles.teamCard}>
      <div className={styles.teamInfo}>
        <div className={styles.teamHeader}>
          <h2 className={styles.teamName}>{team.name}</h2>
          <div className={styles.teamRecord}>{team.record}</div>
        </div>
        
        <div className={styles.statRow}>
          <span className={styles.statValue}>${team.value.toLocaleString()}</span>
          <span className={`${styles.statValue} ${team.profit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
            {team.profit >= 0 ? '+' : ''}${team.profit.toLocaleString()}
          </span>
        </div>
      </div>

      <div className={styles.stocksSection}>
        <h3 className={styles.stocksTitle}>{team.name} Portfolio</h3>
        <div className={styles.stocksTable}>
          <div className={styles.stocksHeader}>
            <div>Stock Ticker</div>
            <div>Profit</div>
          </div>
          <div className={styles.stocksBody}>
            {team.stocks.map((stock, index) => (
              <div key={index} className={styles.stockRow}>
                <div className={styles.ticker}>{stock.ticker}</div>
                <div className={`${styles.stockProfit} ${stock.profit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
                  {stock.profit >= 0 ? '+' : ''}${stock.profit.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TeamCard
