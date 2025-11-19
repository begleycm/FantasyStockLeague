import { useNavigate, useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import styles from './navBar.module.css';

function navBar() {
  const navigate = useNavigate()
  const location = useLocation()
  const selectedLeagueId = localStorage.getItem('selected_league_id')

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
      return
    }
    
    // If no league is selected, prevent navigation and redirect to Leagues
    if (!selectedLeagueId) {
      e.preventDefault()
      navigate('/Private/Leagues')
      alert('Please select a league first before navigating to other pages.')
    }
  }

  return (
    <>
      <nav className={styles.navbar}>
        <div className={styles.navbarLeft}>
          <h1>Fantasy Stock League</h1>
        </div>
        <div className={styles.navbarRight}>
          <p className={styles.navbarItem}>
            <Link to="/Private/Leagues">Leagues</Link>
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
              to="/Private/MatchUp" 
              onClick={(e) => handleNavigation(e, '/Private/MatchUp')}
              style={!selectedLeagueId ? { opacity: 0.6, cursor: 'not-allowed' } : {}}
            >
              Matchup
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
          <p className={styles.navbarItem}>
            <button className={styles.navbarButton} onClick={handleLogout}>
              Logout
            </button>
          </p>
        </div>
      </nav>
    </>
  )
}

export default navBar