import { useState, useEffect } from 'react'
import Pagination from '../../../components/Pagination.jsx'
import styles from './MyStocks.module.css'

const OWNED_STOCKS_CACHE_KEY = 'owned_stocks_cache'
const OWNED_STOCKS_CACHE_TIMESTAMP_KEY = 'owned_stocks_cache_timestamp'
const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes in milliseconds (matches backend API cooldown)

function MyStocks() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentBalance, setCurrentBalance] = useState(0)
  const [netWorth, setNetWorth] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 9

  // Cache utility functions
  const getCachedOwnedStocks = () => {
    try {
      const leagueId = localStorage.getItem('selected_league_id')
      if (!leagueId) return null
      
      const cacheKey = `${OWNED_STOCKS_CACHE_KEY}_${leagueId}`
      const timestampKey = `${OWNED_STOCKS_CACHE_TIMESTAMP_KEY}_${leagueId}`
      
      const cachedData = localStorage.getItem(cacheKey)
      const cachedTimestamp = localStorage.getItem(timestampKey)
      
      if (cachedData && cachedTimestamp) {
        const timestamp = parseInt(cachedTimestamp, 10)
        const now = Date.now()
        const age = now - timestamp
        
        // Check if cache is still valid (less than CACHE_DURATION old)
        if (age < CACHE_DURATION) {
          console.log(`Using cached owned stocks data (${Math.round(age / 1000)}s old)`)
          return JSON.parse(cachedData)
        } else {
          console.log('Cache expired, fetching fresh data')
          // Clear expired cache
          localStorage.removeItem(cacheKey)
          localStorage.removeItem(timestampKey)
        }
      }
    } catch (error) {
      console.error('Error reading cache:', error)
    }
    return null
  }

  const setCachedOwnedStocks = (data) => {
    try {
      const leagueId = localStorage.getItem('selected_league_id')
      if (!leagueId) return
      
      const cacheKey = `${OWNED_STOCKS_CACHE_KEY}_${leagueId}`
      const timestampKey = `${OWNED_STOCKS_CACHE_TIMESTAMP_KEY}_${leagueId}`
      
      localStorage.setItem(cacheKey, JSON.stringify(data))
      localStorage.setItem(timestampKey, Date.now().toString())
      console.log('Owned stocks data cached')
    } catch (error) {
      console.error('Error caching owned stocks:', error)
    }
  }

  const fetchOwnedStocks = async () => {
    const leagueId = localStorage.getItem('selected_league_id')
    if (!leagueId) {
      setError('Please select a league first')
      setLoading(false)
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      setError('Please log in')
      setLoading(false)
      return
    }

    // Try to load from cache first for instant display
    const cachedData = getCachedOwnedStocks()
    if (cachedData) {
      const leagueId = localStorage.getItem('selected_league_id')
      const timestampKey = `${OWNED_STOCKS_CACHE_TIMESTAMP_KEY}_${leagueId}`
      const cachedTimestamp = localStorage.getItem(timestampKey)
      const age = cachedTimestamp ? Math.round((Date.now() - parseInt(cachedTimestamp, 10)) / 1000) : 0
      const remainingTime = cachedTimestamp ? Math.round((CACHE_DURATION - (Date.now() - parseInt(cachedTimestamp, 10))) / 1000) : 0
      console.log(`Using cached owned stocks (${age}s old, ${remainingTime}s remaining). Not calling API.`)
      const stocksData = cachedData.stocks || cachedData
      const transformedStocks = stocksData.map(stock => ({
        ticker: stock.ticker,
        name: stock.name,
        startPrice: parseFloat(stock.start_price) || 0,
        currentPrice: parseFloat(stock.current_price) || 0,
        avgPricePerShare: parseFloat(stock.avg_price_per_share) || 0,
        shares: parseFloat(stock.shares) || 0
      }))
      setStocks(transformedStocks)
      
      if (cachedData.current_balance !== undefined) {
        setCurrentBalance(cachedData.current_balance || 0)
      }
      if (cachedData.net_worth !== undefined) {
        setNetWorth(cachedData.net_worth || 0)
      } else if (cachedData.total_stock_value !== undefined && cachedData.current_balance !== undefined) {
        setNetWorth((cachedData.total_stock_value || 0) + (cachedData.current_balance || 0))
      }
      
      setError('')
      setLoading(false)
      // Cache is valid, don't fetch fresh data
      return
    }

    // Only fetch if cache is expired or doesn't exist
    try {
      console.log("Cache expired or missing. Fetching fresh owned stocks data from API...")
      const response = await fetch(`http://localhost:8000/api/owned-stocks/${leagueId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Handle both old format (array) and new format (object with stocks array)
        const stocksData = data.stocks || data
        const transformedStocks = stocksData.map(stock => ({
          ticker: stock.ticker,
          name: stock.name,
          startPrice: parseFloat(stock.start_price) || 0,
          currentPrice: parseFloat(stock.current_price) || 0,
          avgPricePerShare: parseFloat(stock.avg_price_per_share) || 0,
          shares: parseFloat(stock.shares) || 0
        }))
        setStocks(transformedStocks)
        
        // Set balance and net worth if available
        if (data.current_balance !== undefined) {
          setCurrentBalance(data.current_balance || 0)
        }
        if (data.net_worth !== undefined) {
          setNetWorth(data.net_worth || 0)
        } else if (data.total_stock_value !== undefined && data.current_balance !== undefined) {
          setNetWorth((data.total_stock_value || 0) + (data.current_balance || 0))
        }
        
        // Cache the fresh data
        setCachedOwnedStocks(data)
        
        setError('')
      } else if (response.status === 401) {
        // Token expired or invalid
        setError('Your session has expired. Please log in again.')
        localStorage.removeItem('access_token')
        localStorage.removeItem('selected_league_id')
        // Clear cache on logout
        const cacheKey = `${OWNED_STOCKS_CACHE_KEY}_${leagueId}`
        const timestampKey = `${OWNED_STOCKS_CACHE_TIMESTAMP_KEY}_${leagueId}`
        localStorage.removeItem(cacheKey)
        localStorage.removeItem(timestampKey)
        // Optionally redirect to login
        window.location.href = '/Login'
      } else {
        const errorData = await response.json().catch(() => ({}))
        setError(errorData.error || errorData.detail || 'Failed to load stocks')
        setStocks([])
      }
    } catch (err) {
      console.error('Error fetching owned stocks:', err)
      setError('Network error. Please try again.')
      setStocks([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOwnedStocks()
    
    // Listen for stock purchase/sale events to refresh immediately
    const handleStocksUpdated = (event) => {
      const leagueId = localStorage.getItem('selected_league_id')
      if (event.detail && event.detail.leagueId === leagueId) {
        console.log('Stocks updated event received, refreshing MyStocks...')
        fetchOwnedStocks()
      }
    }
    
    window.addEventListener('stocksUpdated', handleStocksUpdated)
    
    return () => {
      window.removeEventListener('stocksUpdated', handleStocksUpdated)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Calculate totals
  const totalStockValue = stocks.reduce((sum, stock) => sum + (stock.currentPrice * stock.shares), 0)
  
  // Net worth = stock value + current balance
  const calculatedNetWorth = netWorth > 0 ? netWorth : (totalStockValue + currentBalance)
  
  // Calculate all-time profit: net worth - starting balance (10000)
  const totalAllTimeProfit = calculatedNetWorth - 10000

  // Calculate pagination
  const totalPages = Math.ceil(stocks.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentStocks = stocks.slice(startIndex, endIndex)

  const handlePageChange = (page) => {
    setCurrentPage(page)
  }

  return (
    <div className={styles.myStocksSection}>
      <h2>My Stocks</h2>
      
      {loading ? (
        <div className={styles.loading}>Loading stocks...</div>
      ) : error ? (
        <div className={styles.errorMessage}>{error}</div>
      ) : stocks.length === 0 ? (
        <div className={styles.emptyState}>
          <p>You don't own any stocks yet.</p>
          <p>Go to Explore Stocks to start buying!</p>
        </div>
      ) : (
        <>
          <div className={styles.stockTable}>
            <div className={styles.tableHeader}>
              <div>Ticker</div>
              <div>Stock Name</div>
              <div>Avg Purchase Price</div>
              <div>Current Price</div>
              <div>All-Time Profit</div>
              <div>Shares</div>
            </div>
            <div className={styles.stockTableBody}>
              {currentStocks.map((stock, index) => {
                // Calculate all-time profit using avg_price_per_share
                const allTimeProfit = stock.avgPricePerShare > 0 
                  ? (stock.currentPrice - stock.avgPricePerShare) * stock.shares
                  : 0
                const profitPercent = stock.avgPricePerShare > 0 
                  ? ((stock.currentPrice - stock.avgPricePerShare) / stock.avgPricePerShare) * 100 
                  : 0
                
                return (
                  <div key={index} className={styles.stockRow}>
                    <div className={styles.ticker}>{stock.ticker}</div>
                    <div className={styles.stockName}>{stock.name}</div>
                    <div className={styles.startPrice}>
                      {stock.avgPricePerShare > 0 ? `$${stock.avgPricePerShare.toFixed(2)}` : 'N/A'}
                    </div>
                    <div className={styles.currentPrice}>${stock.currentPrice.toFixed(2)}</div>
                    <div className={`${styles.profit} ${allTimeProfit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
                      {stock.avgPricePerShare > 0 ? (
                        <>${allTimeProfit.toFixed(2)} ({profitPercent.toFixed(1)}%)</>
                      ) : (
                        <>N/A</>
                      )}
                    </div>
                    <div className={styles.shares}>{stock.shares.toFixed(2)}</div>
                  </div>
                )
              })}
            </div>
          </div>
          {totalPages > 1 && (
            <Pagination 
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
          <div className={styles.stockSummary}>
            <div className={styles.summaryItem}>
              <span className={styles.summaryLabel}>Current Balance:</span>
              <span className={styles.summaryValue}>${currentBalance.toFixed(2)}</span>
            </div>
            <div className={styles.summaryItem}>
              <span className={styles.summaryLabel}>Stock Value:</span>
              <span className={styles.summaryValue}>${totalStockValue.toFixed(2)}</span>
            </div>
            <div className={styles.summaryItem}>
              <span className={styles.summaryLabel}>Net Worth:</span>
              <span className={styles.summaryValue}>${calculatedNetWorth.toFixed(2)}</span>
            </div>
            <div className={styles.summaryItem}>
              <span className={styles.summaryLabel}>Total All-Time Profit:</span>
              <span className={`${styles.summaryValue} ${totalAllTimeProfit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
                {totalAllTimeProfit >= 0 ? '+' : ''}${totalAllTimeProfit.toFixed(2)}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MyStocks
