import { useState, useEffect } from 'react'
import NavBar from "../components/navBar.jsx"
import SearchBar from "./components/SearchBar.jsx"
import PopularStocks from "./components/PopularStocks.jsx"
import AllStocksList from "./components/AllStocksList.jsx"
import StockModal from "./components/StockModal.jsx"
import styles from "./exploreStocks.module.css"

const CACHE_KEY = 'stocks_cache'
const CACHE_TIMESTAMP_KEY = 'stocks_cache_timestamp'
const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes in milliseconds (matches backend API cooldown)

function ExploreStocks() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredStocks, setFilteredStocks] = useState([])
  const [allStocks, setAllStocks] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Cache utility functions
  const getCachedStocks = () => {
    try {
      const cachedData = localStorage.getItem(CACHE_KEY)
      const cachedTimestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY)
      
      if (cachedData && cachedTimestamp) {
        const timestamp = parseInt(cachedTimestamp, 10)
        const now = Date.now()
        const age = now - timestamp
        
        // Check if cache is still valid (less than CACHE_DURATION old)
        if (age < CACHE_DURATION) {
          console.log(`Using cached stocks data (${Math.round(age / 1000)}s old)`)
          return JSON.parse(cachedData)
        } else {
          console.log('Cache expired, fetching fresh data')
          // Clear expired cache
          localStorage.removeItem(CACHE_KEY)
          localStorage.removeItem(CACHE_TIMESTAMP_KEY)
        }
      }
    } catch (error) {
      console.error('Error reading cache:', error)
    }
    return null
  }

  const setCachedStocks = (stocks) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(stocks))
      localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString())
      console.log('Stocks data cached')
    } catch (error) {
      console.error('Error caching stocks:', error)
    }
  }

  const getStocks = async() => {
    try {
      const response = await fetch("http://localhost:8000/api/stocks/")
      if (response.ok) {
        const data = await response.json()
        console.log("Received stocks data:", data)
        return Array.isArray(data) ? data : []
      } else {
        console.error("Error fetching stock data:", response.status, response.statusText)
        const errorData = await response.json().catch(() => ({}))
        console.error("Error details:", errorData)
        return []
      }
    } catch (error) {
      console.error("Error fetching stock data:", error)
      return []
    }
  }

  const transformStockData = (stocks) => {
    if (!Array.isArray(stocks) || stocks.length === 0) {
      console.log("No stocks to transform")
      return []
    }
    
    return stocks.map(stock => {
      const currentPrice = parseFloat(stock.current_price) || 0
      const startPrice = parseFloat(stock.start_price) || 0
      const change = currentPrice - startPrice
      const changePercent = startPrice !== 0 ? (change / startPrice) * 100 : 0
      
      return {
        ...stock,
        price: currentPrice,
        current_price: currentPrice,
        change: change,
        changePercent: changePercent
      }
    })
  }

  useEffect(() => {
    const fetchStocks = async () => {
      setIsLoading(true)
      
      // Try to load from cache first for instant display
      const cachedStocks = getCachedStocks()
      if (cachedStocks && cachedStocks.length > 0) {
        const cachedTimestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY)
        const age = cachedTimestamp ? Math.round((Date.now() - parseInt(cachedTimestamp, 10)) / 1000) : 0
        const remainingTime = Math.round((CACHE_DURATION - (Date.now() - parseInt(cachedTimestamp, 10))) / 1000)
        console.log(`Using cached stocks (${age}s old, ${remainingTime}s remaining). Not calling API.`)
        const transformedCached = transformStockData(cachedStocks)
        setAllStocks(transformedCached)
        setIsLoading(false)
        // Cache is valid, don't fetch fresh data
        return
      }
      
      // Only fetch if cache is expired or doesn't exist
      console.log("Cache expired or missing. Fetching fresh stocks data from API...")
      try {
        const stocks = await getStocks()
        console.log("Raw stocks received:", stocks.length)
        
        if (stocks.length > 0) {
          const transformedStocks = transformStockData(stocks)
          console.log("Transformed stocks:", transformedStocks.length)
          
          // Update state with fresh data
          setAllStocks(transformedStocks)
          
          // Cache the fresh data
          setCachedStocks(stocks)
        } else {
          setAllStocks([])
        }
      } catch (error) {
        console.error("Error fetching fresh stocks:", error)
        setAllStocks([])
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchStocks()
  }, [])

  const popularStocks = allStocks.slice(0, 8)

  const handleSearch = (term) => {
    setSearchTerm(term)
    if (term.trim() === '') {
      setFilteredStocks([])
    } else {
      const filtered = allStocks.filter(stock => 
        stock.ticker.toLowerCase().includes(term.toLowerCase()) ||
        stock.name.toLowerCase().includes(term.toLowerCase())
      )
      setFilteredStocks(filtered)
    }
  }

  const handleStockClick = (stock) => {
    setSelectedStock(stock)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedStock(null)
  }

  return (
    <>
        <NavBar></NavBar>
        <div className={styles.exploreStocksContainer}>
            <div className={styles.contentContainer}>
                <div className={styles.leftSide}>
                    <PopularStocks stocks={popularStocks} onStockClick={handleStockClick} />
                </div>
                <div className={styles.rightSide}>
                    {isLoading && allStocks.length === 0 ? (
                        <div style={{ padding: '20px', textAlign: 'center' }}>
                            Loading stocks...
                        </div>
                    ) : (
                        <AllStocksList 
                            stocks={searchTerm ? filteredStocks : allStocks}
                            searchTerm={searchTerm}
                            onSearch={handleSearch}
                            onStockClick={handleStockClick}
                        />
                    )}
                </div>
            </div>
        </div>
        <StockModal 
          stock={selectedStock} 
          isOpen={isModalOpen} 
          onClose={handleCloseModal} 
        />
    </>
  )
}

export default ExploreStocks
