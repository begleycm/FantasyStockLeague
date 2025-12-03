import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import UsernameModal from './UsernameModal.jsx';
import styles from './navBar.module.css';

function navBar() {
  const navigate = useNavigate()
  const location = useLocation()
  const selectedLeagueId = localStorage.getItem('selected_league_id')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [username, setUsername] = useState(localStorage.getItem('username') || '')
  const [isUsernameModalOpen, setIsUsernameModalOpen] = useState(false)

  useEffect(() => {
    // Listen for username updates
    const handleUsernameUpdated = (event) => {
      if (event.detail && event.detail.username) {
        setUsername(event.detail.username)
      }
    }
    
    window.addEventListener('usernameUpdated', handleUsernameUpdated)
    
    return () => {
      window.removeEventListener('usernameUpdated', handleUsernameUpdated)
    }
  }, [])

  const handleLogout = () => {
    const confirmed = window.confirm('Are you sure you want to logout?')
    if (confirmed) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('selected_league_id')
      navigate('/Login')
    }
  }

  const handleNavigation = (e, path) => {
    // Always allow navigation to Leagues page
    if (path === '/Private/Leagues') {
      setIsMobileMenuOpen(false)
      return
    }
    
    // If no league is selected, prevent navigation and redirect to Leagues
    if (!selectedLeagueId) {
      e.preventDefault()
      setIsMobileMenuOpen(false)
      navigate('/Private/Leagues')
      alert('Please select a league first before navigating to other pages.')
    } else {
      setIsMobileMenuOpen(false)
    }
  }

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  return (
    <>
      <nav className={styles.navbar}>
        <div className={styles.navbarLeft}>
          <h1 className={styles.navbarTitle}>Fantasy Stock League</h1>
        </div>
        <button 
          className={styles.hamburgerButton}
          onClick={toggleMobileMenu}
          aria-label="Toggle menu"
        >
          <span className={styles.hamburgerLine}></span>
          <span className={styles.hamburgerLine}></span>
          <span className={styles.hamburgerLine}></span>
        </button>
        <div className={`${styles.navbarRight} ${isMobileMenuOpen ? styles.mobileMenuOpen : ''}`}>
          <p className={styles.navbarItem}>
            <Link to="/Private/Leagues" onClick={() => setIsMobileMenuOpen(false)}>Leagues</Link>
          </p>
          <p className={styles.navbarItem}>
            <Link 
              to="/Private/Home" 
              onClick={(e) => handleNavigation(e, '/Private/Home')}
              style={!selectedLeagueId ? { opacity: 0.6, cursor: 'not-allowed' } : {}}
            >
              Home
            </Link>
          </p>
          <p className={styles.navbarItem}>
            <Link 
              to="/Private/ExploreStocks" 
              onClick={(e) => handleNavigation(e, '/Private/ExploreStocks')}
              style={!selectedLeagueId ? { opacity: 0.6, cursor: 'not-allowed' } : {}}
            >
              Explore Stocks
            </Link>
          </p>
          {username && (
            <p className={styles.navbarItem}>
              <button 
                className={styles.usernameButton} 
                onClick={() => {
                  setIsUsernameModalOpen(true)
                  setIsMobileMenuOpen(false)
                }}
                title="Click to change username"
              >
                {username}
              </button>
            </p>
          )}
          <p className={styles.navbarItem}>
            <button className={styles.navbarButton} onClick={handleLogout}>
              Logout
            </button>
          </p>
        </div>
      </nav>
      <UsernameModal 
        isOpen={isUsernameModalOpen} 
        onClose={() => setIsUsernameModalOpen(false)} 
      />
    </>
  )
}

export default navBar