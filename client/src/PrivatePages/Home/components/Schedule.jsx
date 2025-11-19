import { useState, useEffect } from 'react'
import styles from './Schedule.module.css'

function Schedule() {
  const [schedule, setSchedule] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentWeek, setCurrentWeek] = useState(null)
  const username = localStorage.getItem('username') || 'You'

  useEffect(() => {
    fetchSchedule()
  }, [])

  const fetchSchedule = async () => {
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
      const response = await fetch(`http://localhost:8000/api/leagues/${leagueId}/schedule/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setSchedule(data.schedule || [])
        setCurrentWeek(data.current_week)
        setError('')
      } else if (response.status === 401) {
        setError('Your session has expired. Please log in again.')
        localStorage.removeItem('access_token')
        localStorage.removeItem('selected_league_id')
        window.location.href = '/Login'
      } else {
        const errorData = await response.json().catch(() => ({}))
        if (errorData.error === 'You are not a participant in this league') {
          setError('Schedule not available - you are not a participant in this league')
        } else if (errorData.error === 'League not found') {
          setError('League not found')
        } else {
          setError(errorData.error || errorData.detail || 'Failed to load schedule')
        }
        setSchedule([])
      }
    } catch (err) {
      console.error('Error fetching schedule:', err)
      setError('Network error. Please try again.')
      setSchedule([])
    } finally {
      setLoading(false)
    }
  }

  const getMatchupText = (matchup) => {
    let text = `Week ${matchup.week_number}: ${username} vs ${matchup.opponent_username}`
    if (matchup.is_winner === true) {
      text += ' ✓ (Won)'
    } else if (matchup.is_winner === false) {
      text += ' ✗ (Lost)'
    }
    return text
  }

  if (loading) {
    return (
      <div className={styles.scheduleSection}>
        <h2>Schedule</h2>
        <div className={styles.schedule}>
          <div className={styles.loading}>Loading schedule...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.scheduleSection}>
        <h2>Schedule</h2>
        <div className={styles.schedule}>
          <div className={styles.errorMessage}>{error}</div>
        </div>
      </div>
    )
  }

  if (schedule.length === 0) {
    return (
      <div className={styles.scheduleSection}>
        <h2>Schedule</h2>
        <div className={styles.schedule}>
          <div className={styles.emptyState}>
            <p>No schedule available yet.</p>
            <p>The schedule will be created when the league starts.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.scheduleSection}>
      <h2>Schedule</h2>
      <div className={styles.schedule}>
        <div className={styles.scheduleList}>
          {schedule.map((matchup, index) => (
            <div
              key={index}
              className={`${styles.gameItem} ${matchup.is_current_week ? styles.currentWeek : ''}`}
            >
              {getMatchupText(matchup)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Schedule
