import { useState, useEffect } from 'react'
import styles from './StockModal.module.css'

function StockModal({ stock, isOpen, onClose }) {
  const [balance, setBalance] = useState(0)
  const [ownedShares, setOwnedShares] = useState(0)
  const [buyShares, setBuyShares] = useState('')
  const [sellShares, setSellShares] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [activeTab, setActiveTab] = useState('buy') // 'buy' or 'sell'

  const leagueId = localStorage.getItem('selected_league_id')

  useEffect(() => {
    if (isOpen && stock && leagueId) {
      fetchStockInfo()
    }
  }, [isOpen, stock, leagueId])

  const fetchStockInfo = async () => {
    if (!stock || !leagueId) return
    
    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch(`http://localhost:8000/api/stocks/info/${leagueId}/${stock.ticker}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setBalance(data.balance || 0)
        setOwnedShares(data.owned_shares || 0)
      }
    } catch (err) {
      console.error('Error fetching stock info:', err)
    }
  }

  if (!isOpen || !stock) return null

  const currentPrice = stock.current_price ?? stock.price ?? 0
  const startPrice = stock.start_price ?? 0
  const change = stock.change ?? (currentPrice - startPrice)
  const changePercent = stock.changePercent ?? (startPrice !== 0 ? (change / startPrice) * 100 : 0)

  const handleBuy = async (e) => {
    e.preventDefault()
    if (!leagueId) {
      setError('Please select a league first')
      return
    }

    const shares = parseFloat(buyShares)
    if (!shares || shares <= 0) {
      setError('Please enter a valid number of shares')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch('http://localhost:8000/api/stocks/buy/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          league_id: leagueId,
          ticker: stock.ticker,
          shares: shares,
        }),
      })

      const data = await response.json()
      if (response.ok) {
        setSuccess(data.message || 'Stock purchased successfully')
        setBuyShares('')
        await fetchStockInfo() // Refresh balance and shares
        
        // Invalidate owned stocks cache and notify MyStocks component
        if (leagueId) {
          const cacheKey = `owned_stocks_cache_${leagueId}`
          const timestampKey = `owned_stocks_cache_timestamp_${leagueId}`
          localStorage.removeItem(cacheKey)
          localStorage.removeItem(timestampKey)
          
          // Dispatch custom event to notify MyStocks component
          window.dispatchEvent(new CustomEvent('stocksUpdated', { detail: { leagueId } }))
        }
      } else {
        setError(data.error || 'Failed to buy stock')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSell = async (e) => {
    e.preventDefault()
    if (!leagueId) {
      setError('Please select a league first')
      return
    }

    const shares = parseFloat(sellShares)
    if (!shares || shares <= 0) {
      setError('Please enter a valid number of shares')
      return
    }

    if (shares > ownedShares) {
      setError(`You only own ${ownedShares} shares`)
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch('http://localhost:8000/api/stocks/sell/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          league_id: leagueId,
          ticker: stock.ticker,
          shares: shares,
        }),
      })

      const data = await response.json()
      if (response.ok) {
        setSuccess(data.message || 'Stock sold successfully')
        setSellShares('')
        await fetchStockInfo() // Refresh balance and shares
        
        // Invalidate owned stocks cache and notify MyStocks component
        if (leagueId) {
          const cacheKey = `owned_stocks_cache_${leagueId}`
          const timestampKey = `owned_stocks_cache_timestamp_${leagueId}`
          localStorage.removeItem(cacheKey)
          localStorage.removeItem(timestampKey)
          
          // Dispatch custom event to notify MyStocks component
          window.dispatchEvent(new CustomEvent('stocksUpdated', { detail: { leagueId } }))
        }
      } else {
        setError(data.error || 'Failed to sell stock')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const buyCost = buyShares ? (parseFloat(buyShares) * currentPrice).toFixed(2) : '0.00'
  const sellRevenue = sellShares ? (parseFloat(sellShares) * currentPrice).toFixed(2) : '0.00'

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>{stock.name || 'Stock Details'}</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.stockDetails}>
          <div className={styles.detailRow}>
            <span className={styles.label}>Ticker:</span>
            <span className={styles.value}>{stock.ticker || 'N/A'}</span>
          </div>
          
          <div className={styles.detailRow}>
            <span className={styles.label}>Company Name:</span>
            <span className={styles.value}>{stock.name || 'N/A'}</span>
          </div>
          
          <div className={styles.detailRow}>
            <span className={styles.label}>Current Price:</span>
            <span className={styles.value}>${currentPrice.toFixed(2)}</span>
          </div>
          
          <div className={styles.detailRow}>
            <span className={styles.label}>Start Price:</span>
            <span className={styles.value}>${startPrice.toFixed(2)}</span>
          </div>
          
          <div className={styles.detailRow}>
            <span className={styles.label}>Change:</span>
            <span className={`${styles.value} ${change >= 0 ? styles.positive : styles.negative}`}>
              {change >= 0 ? '+' : ''}${change.toFixed(2)}
            </span>
          </div>
          
          <div className={styles.detailRow}>
            <span className={styles.label}>Change %:</span>
            <span className={`${styles.value} ${changePercent >= 0 ? styles.positive : styles.negative}`}>
              {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
            </span>
          </div>
        </div>

        {leagueId ? (
          <>
            <div className={styles.tabs}>
              <button 
                className={`${styles.tab} ${activeTab === 'buy' ? styles.activeTab : ''}`}
                onClick={() => {
                  setActiveTab('buy')
                  setError('')
                  setSuccess('')
                }}
              >
                Buy
              </button>
              <button 
                className={`${styles.tab} ${activeTab === 'sell' ? styles.activeTab : ''}`}
                onClick={() => {
                  setActiveTab('sell')
                  setError('')
                  setSuccess('')
                }}
              >
                Sell
              </button>
            </div>

            <div className={styles.userInfo}>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Balance:</span>
                <span className={styles.infoValue}>${balance.toFixed(2)}</span>
              </div>
              <div className={styles.infoRow}>
                <span className={styles.infoLabel}>Owned Shares:</span>
                <span className={styles.infoValue}>{ownedShares.toFixed(2)}</span>
              </div>
            </div>

            {activeTab === 'buy' ? (
              <form onSubmit={handleBuy} className={styles.tradeForm}>
                <div className={styles.formGroup}>
                  <label htmlFor="buyShares">Shares to Buy</label>
                  <input
                    type="number"
                    id="buyShares"
                    step="0.01"
                    min="0.01"
                    value={buyShares}
                    onChange={(e) => setBuyShares(e.target.value)}
                    placeholder="Enter shares"
                    required
                  />
                  <div className={styles.costInfo}>
                    Cost: ${buyCost}
                  </div>
                </div>
                {error && <div className={styles.errorMessage}>{error}</div>}
                {success && <div className={styles.successMessage}>{success}</div>}
                <button 
                  type="submit" 
                  className={styles.buyButton}
                  disabled={loading || !buyShares || parseFloat(buyShares) <= 0}
                >
                  {loading ? 'Processing...' : 'Buy Stock'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleSell} className={styles.tradeForm}>
                <div className={styles.formGroup}>
                  <label htmlFor="sellShares">Shares to Sell</label>
                  <input
                    type="number"
                    id="sellShares"
                    step="0.01"
                    min="0.01"
                    max={ownedShares}
                    value={sellShares}
                    onChange={(e) => setSellShares(e.target.value)}
                    placeholder={`Max: ${ownedShares.toFixed(2)}`}
                    required
                  />
                  <div className={styles.costInfo}>
                    Revenue: ${sellRevenue}
                  </div>
                </div>
                {error && <div className={styles.errorMessage}>{error}</div>}
                {success && <div className={styles.successMessage}>{success}</div>}
                <button 
                  type="submit" 
                  className={styles.sellButton}
                  disabled={loading || !sellShares || parseFloat(sellShares) <= 0 || parseFloat(sellShares) > ownedShares}
                >
                  {loading ? 'Processing...' : 'Sell Stock'}
                </button>
              </form>
            )}
          </>
        ) : (
          <div className={styles.noLeagueMessage}>
            Please select a league to buy or sell stocks
          </div>
        )}

        <div className={styles.modalActions}>
          <button className={styles.closeModalButton} onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default StockModal

