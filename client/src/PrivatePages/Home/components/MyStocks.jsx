import { useState, useEffect } from 'react'
import Pagination from '../../../components/Pagination.jsx'
import styles from './MyStocks.module.css'

function MyStocks() {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentBalance, setCurrentBalance] = useState(0)
  const [netWorth, setNetWorth] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 9

  useEffect(() => {
    fetchOwnedStocks()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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

    try {
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
          priceAtStartOfWeek: parseFloat(stock.price_at_start_of_week) || 0,
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
        
        setError('')
      } else if (response.status === 401) {
        // Token expired or invalid
        setError('Your session has expired. Please log in again.')
        localStorage.removeItem('access_token')
        localStorage.removeItem('selected_league_id')
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

  // Calculate totals
  const totalStockValue = stocks.reduce((sum, stock) => sum + (stock.currentPrice * stock.shares), 0)
  // Calculate weekly profit using price_at_start_of_week
  const totalWeeklyProfit = stocks.reduce((sum, stock) => {
    if (stock.priceAtStartOfWeek > 0) {
      return sum + ((stock.currentPrice - stock.priceAtStartOfWeek) * stock.shares)
    }
    return sum
  }, 0)
  
  // Net worth = stock value + current balance
  const calculatedNetWorth = netWorth > 0 ? netWorth : (totalStockValue + currentBalance)

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
              <div>Week Start Price</div>
              <div>Current Price</div>
              <div>Weekly Profit</div>
              <div>Shares</div>
            </div>
            <div className={styles.stockTableBody}>
              {currentStocks.map((stock, index) => {
                // Calculate weekly profit using price_at_start_of_week
                const weeklyProfit = stock.priceAtStartOfWeek > 0 
                  ? (stock.currentPrice - stock.priceAtStartOfWeek) * stock.shares
                  : 0
                const profitPercent = stock.priceAtStartOfWeek > 0 
                  ? ((stock.currentPrice - stock.priceAtStartOfWeek) / stock.priceAtStartOfWeek) * 100 
                  : 0
                
                return (
                  <div key={index} className={styles.stockRow}>
                    <div className={styles.ticker}>{stock.ticker}</div>
                    <div className={styles.stockName}>{stock.name}</div>
                    <div className={styles.startPrice}>
                      {stock.priceAtStartOfWeek > 0 ? `$${stock.priceAtStartOfWeek.toFixed(2)}` : 'N/A'}
                    </div>
                    <div className={styles.currentPrice}>${stock.currentPrice.toFixed(2)}</div>
                    <div className={`${styles.profit} ${weeklyProfit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
                      {stock.priceAtStartOfWeek > 0 ? (
                        <>${weeklyProfit.toFixed(2)} ({profitPercent.toFixed(1)}%)</>
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
              <span className={styles.summaryLabel}>Total Weekly Profit:</span>
              <span className={`${styles.summaryValue} ${totalWeeklyProfit >= 0 ? styles.profitPositive : styles.profitNegative}`}>
                {totalWeeklyProfit >= 0 ? '+' : ''}${totalWeeklyProfit.toFixed(2)}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MyStocks
