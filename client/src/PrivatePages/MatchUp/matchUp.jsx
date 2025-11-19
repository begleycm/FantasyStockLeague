import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavBar from "../components/navBar.jsx"
import TeamCard from "./components/TeamCard.jsx"
import styles from "./matchUp.module.css"

function MatchUp() {
  const [matchup, setMatchup] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [weekNumber, setWeekNumber] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchMatchup()
  }, [])

  const fetchMatchup = async () => {
    const leagueId = localStorage.getItem('selected_league_id')
    if (!leagueId) {
      setError('Please select a league first')
      setLoading(false)
      navigate('/Private/Leagues')
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      setError('Please log in')
      setLoading(false)
      navigate('/Login')
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/leagues/${leagueId}/matchup/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setMatchup(data)
        setWeekNumber(data.week_number)
        setError('')
      } else if (response.status === 401) {
        setError('Your session has expired. Please log in again.')
        localStorage.removeItem('access_token')
        localStorage.removeItem('selected_league_id')
        window.location.href = '/Login'
      } else {
        const errorData = await response.json().catch(() => ({}))
        if (errorData.error === 'You are not a participant in this league') {
          setError('Matchup not available - you are not a participant in this league')
        } else if (errorData.error === 'League not found') {
          setError('League not found')
        } else if (errorData.error === 'League has not started yet') {
          setError('League has not started yet')
        } else if (errorData.error === 'No matchup found for current week') {
          setError('No matchup found for current week')
        } else {
          setError(errorData.error || errorData.detail || 'Failed to load matchup')
        }
        setMatchup(null)
      }
    } catch (err) {
      console.error('Error fetching matchup:', err)
      setError('Network error. Please try again.')
      setMatchup(null)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <>
        <NavBar />
        <div className={styles.matchUpContainer}>
          <div className={styles.matchupHeader}>
            <h1>Loading matchup...</h1>
          </div>
        </div>
      </>
    )
  }

  if (error) {
    return (
      <>
        <NavBar />
        <div className={styles.matchUpContainer}>
          <div className={styles.matchupHeader}>
            <h1>Matchup</h1>
          </div>
          <div style={{ textAlign: 'center', padding: '40px', color: '#ef4444' }}>
            <p>{error}</p>
          </div>
        </div>
      </>
    )
  }

  if (!matchup || !matchup.player1 || !matchup.player2) {
    return (
      <>
        <NavBar />
        <div className={styles.matchUpContainer}>
          <div className={styles.matchupHeader}>
            <h1>Matchup</h1>
          </div>
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
            <p>No matchup data available</p>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
        <NavBar></NavBar>
        <div className={styles.matchUpContainer}>
            <div className={styles.matchupHeader}>
                <h1>Week {weekNumber || 'N/A'}</h1>
            </div>
            
            <div className={styles.teamsContainer}>
                <TeamCard 
                    team={matchup.player1} 
                    isPlayer1={true}
                />
                <TeamCard 
                    team={matchup.player2} 
                    isPlayer1={false}
                />
            </div>
        </div>
    </>
  )
}

export default MatchUp
