import { useState, useEffect } from 'react'
import styles from './LeagueLeaderboard.module.css'

function LeagueLeaderboard() {
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchLeaderboard()
  }, [])

  const fetchLeaderboard = async () => {
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
      const response = await fetch(`http://localhost:8000/api/leagues/${leagueId}/leaderboard/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setLeaderboard(data.leaderboard || [])
        setError('')
      } else if (response.status === 401) {
        setError('Your session has expired. Please log in again.')
        localStorage.removeItem('access_token')
        localStorage.removeItem('selected_league_id')
        window.location.href = '/Login'
      } else {
        const errorData = await response.json().catch(() => ({}))
        if (errorData.error === 'You are not a participant in this league') {
          setError('Leaderboard not available - you are not a participant in this league')
        } else if (errorData.error === 'League not found') {
          setError('League not found')
        } else {
          setError(errorData.error || errorData.detail || 'Failed to load leaderboard')
        }
        setLeaderboard([])
      }
    } catch (err) {
      console.error('Error fetching leaderboard:', err)
      setError('Network error. Please try again.')
      setLeaderboard([])
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.leagueSection}>
        <h2>League Leaderboard (Power Rankings)</h2>
        <div className={styles.leaderboard}>
          <div className={styles.loading}>Loading leaderboard...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.leagueSection}>
        <h2>League Leaderboard (Power Rankings)</h2>
        <div className={styles.leaderboard}>
          <div className={styles.errorMessage}>{error}</div>
        </div>
      </div>
    )
  }

  if (leaderboard.length === 0) {
    return (
      <div className={styles.leagueSection}>
        <h2>League Leaderboard (Power Rankings)</h2>
        <div className={styles.leaderboard}>
          <div className={styles.emptyState}>
            <p>No leaderboard data available yet.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.leagueSection}>
      <h2>League Leaderboard (Power Rankings)</h2>
      <div className={styles.leaderboard}>
        <ol>
          {leaderboard.map((entry, index) => (
            <li
              key={index}
              className={entry.is_current_user ? styles.userTeam : ''}
            >
              {entry.username} | ${entry.net_worth.toLocaleString()}
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}

export default LeagueLeaderboard
