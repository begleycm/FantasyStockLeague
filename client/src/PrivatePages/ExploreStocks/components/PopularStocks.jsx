import styles from './PopularStocks.module.css'

function PopularStocks({ stocks, onStockClick }) {
  return (
    <div className={styles.popularSection}>
      <div className={styles.sectionHeader}>
        <h2>Popular Stocks</h2>
      </div>
      <div className={styles.stocksList}>
        {stocks && stocks.length > 0 ? (
          stocks.map((stock, index) => {
            const currentPrice = stock.current_price ?? stock.price ?? 0
            const change = stock.change ?? 0
            const changePercent = stock.changePercent ?? 0
            
            return (
              <div 
                key={index} 
                className={styles.stockItem}
                onClick={() => onStockClick && onStockClick(stock)}
                style={{ cursor: onStockClick ? 'pointer' : 'default' }}
              >
                <div className={styles.stockInfo}>
                  <div className={styles.ticker}>{stock.ticker || 'N/A'}</div>
                  <div className={styles.stockName}>{stock.name || 'N/A'}</div>
                </div>
                <div className={styles.stockPrice}>
                  <div className={styles.price}>${currentPrice.toFixed(2)}</div>
                  <div className={`${styles.change} ${change >= 0 ? styles.positive : styles.negative}`}>
                    {change >= 0 ? '+' : ''}${change.toFixed(2)}({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div>No stocks available</div>
        )}
      </div>
    </div>
  )
}

export default PopularStocks
