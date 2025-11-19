import { useState, useEffect } from 'react'
import NavBar from "../components/navBar.jsx"
import SearchBar from "./components/SearchBar.jsx"
import PopularStocks from "./components/PopularStocks.jsx"
import AllStocksList from "./components/AllStocksList.jsx"
import StockModal from "./components/StockModal.jsx"
import styles from "./exploreStocks.module.css"

function ExploreStocks() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filteredStocks, setFilteredStocks] = useState([])
  const [allStocks, setAllStocks] = useState([])
  const [selectedStock, setSelectedStock] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const getStocks = async() => {
    const response = await fetch("http://localhost:8000/api/stocks/")
    if (response.ok) {
      const data = await response.json()
      return data
    } else {
      console.log("Error fetching stock data")
      return []
    }
  }

  const transformStockData = (stocks) => {
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
      const stocks = await getStocks()
      const transformedStocks = transformStockData(stocks)
      setAllStocks(transformedStocks)
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
                    <AllStocksList 
                        stocks={searchTerm ? filteredStocks : allStocks}
                        searchTerm={searchTerm}
                        onSearch={handleSearch}
                        onStockClick={handleStockClick}
                    />
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
