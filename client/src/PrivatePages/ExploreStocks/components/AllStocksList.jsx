import { useState } from 'react'
import SearchBar from './SearchBar.jsx'
import Pagination from '../../../components/Pagination.jsx'
import styles from './AllStocksList.module.css'

function AllStocksList({ stocks, searchTerm, onSearch, onStockClick }) {
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  // Calculate pagination
  const totalPages = Math.ceil(stocks.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentStocks = stocks.slice(startIndex, endIndex)

  const handlePageChange = (page) => {
    setCurrentPage(page)
  }

  return (
    <div className={styles.allStocksSection}>
      <div className={styles.sectionHeader}>
        <h2>{searchTerm ? `Search Results (${stocks.length})` : 'All Stocks'}</h2>
        <SearchBar onSearch={onSearch} />
      </div>
      
      <div className={styles.stocksTable}>
        <div className={styles.tableHeader}>
          <div>Ticker</div>
          <div>Company Name</div>
          <div>Price</div>
          <div>Change</div>
          <div>Change %</div>
        </div>
        <div className={styles.stocksTableBody}>
          {currentStocks.length === 0 ? (
            <div className={styles.noResults}>
              {searchTerm ? `No stocks found for "${searchTerm}"` : 'No stocks available'}
            </div>
          ) : (
            currentStocks.map((stock, index) => (
              <div 
                key={index} 
                className={styles.stockRow}
                onClick={() => onStockClick && onStockClick(stock)}
                style={{ cursor: onStockClick ? 'pointer' : 'default' }}
              >
                <div className={styles.ticker}>{stock.ticker}</div>
                <div className={styles.stockName}>{stock.name}</div>
                <div className={styles.price}>${stock.price.toFixed(2)}</div>
                <div className={`${styles.change} ${stock.change >= 0 ? styles.positive : styles.negative}`}>
                  {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
                </div>
                <div className={`${styles.changePercent} ${stock.changePercent >= 0 ? styles.positive : styles.negative}`}>
                  {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <Pagination 
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  )
}

export default AllStocksList
