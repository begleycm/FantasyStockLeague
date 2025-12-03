import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import NavBar from '../components/navBar.jsx'
import styles from './leagues.module.css'

function Leagues() {
  const [username, setUsername] = useState('')
  const [leagues, setLeagues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isSuperuser, setIsSuperuser] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [leagueName, setLeagueName] = useState('')
  const [joinLeagueId, setJoinLeagueId] = useState('')
  const navigate = useNavigate()

  // Fetch user leagues
  const fetchLeagues = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      navigate('/Login')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/leagues/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        // Handle new response format with is_superuser flag
        if (data.leagues) {
          setLeagues(data.leagues)
          setIsSuperuser(data.is_superuser || false)
        } else {
          // Fallback for old format
          setLeagues(data)
          setIsSuperuser(false)
        }
      } else if (response.status === 404) {
        // Endpoint might not exist yet, set empty array
        setLeagues([])
      } else {
        setError('Failed to load leagues')
      }
    } catch (err) {
      console.error('Error fetching leagues:', err)
      setLeagues([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }

  // Get username from localStorage
  useEffect(() => {
    const storedUsername = localStorage.getItem('username')
    if (storedUsername) {
      setUsername(storedUsername)
    }
    fetchLeagues()
  }, [])

  // Handle create league
  const handleCreateLeague = async (e) => {
    e.preventDefault()
    const token = localStorage.getItem('access_token')
    
    if (!leagueName.trim()) {
      setError('League name is required')
      return
    }

    // Start date is no longer required - will be set when 8 players join

    try {
      const response = await fetch('http://localhost:8000/api/leagues/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: leagueName,
        }),
      })

      if (response.ok) {
        setShowCreateModal(false)
        setLeagueName('')
        setError('')
        fetchLeagues() // Refresh leagues list
      } else {
        const errorData = await response.json()
        // Handle different error formats
        let errorMessage = 'Failed to create league'
        if (errorData.errors) {
          // Handle validation errors
          const errorMessages = Object.entries(errorData.errors).map(([field, messages]) => {
            return `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
          })
          errorMessage = errorMessages.join('; ')
        } else if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (typeof errorData === 'string') {
          errorMessage = errorData
        }
        setError(errorMessage)
        console.error('Create league error:', errorData)
      }
    } catch (err) {
      setError('Network error. Please try again.')
    }
  }

  // Handle join league
  const handleJoinLeague = async (e) => {
    e.preventDefault()
    const token = localStorage.getItem('access_token')
    
    if (!joinLeagueId.trim()) {
      setError('League ID is required')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/leagues/join/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          league_id: joinLeagueId,
        }),
      })

      if (response.ok) {
        const responseData = await response.json()
        setShowJoinModal(false)
        setJoinLeagueId('')
        setError('')
        
        // Auto-select the league after joining
        if (responseData.league && responseData.league.league_id) {
          localStorage.setItem('selected_league_id', responseData.league.league_id)
        }
        
        fetchLeagues() // Refresh leagues list
      } else {
        const errorData = await response.json()
        // Handle different error formats
        const errorMessage = errorData.error || errorData.detail || 'Failed to join league'
        setError(errorMessage)
        console.error('Join league error:', errorData)
      }
    } catch (err) {
      setError('Network error. Please try again.')
    }
  }

  // Handle league click - navigate to home with selected league
  const handleLeagueClick = (leagueId, isParticipant, participantCount, event) => {
    
    // Superusers can only select leagues they are participants in
    if (isSuperuser && !isParticipant) {
      return // Don't allow navigation for non-participant leagues
    }
    
    // Prevent selection if league doesn't have all 8 participants
    if (participantCount < 8) {
      return // Don't allow navigation for leagues that don't have all participants
    }
    
    localStorage.setItem('selected_league_id', leagueId)
    navigate('/Private/Home')
  }

  const handleDeleteLeague = async (leagueId, leagueName, e) => {
    e.stopPropagation() // Prevent card click
    
    const confirmed = window.confirm(
      `Are you sure you want to delete the league "${leagueName}"? This action cannot be undone.`
    )
    
    if (!confirmed) {
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      setError('Please log in')
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/leagues/${leagueId}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        // Refresh leagues list
        fetchLeagues()
        setError('')
      } else {
        const errorData = await response.json()
        setError(errorData.error || errorData.detail || 'Failed to delete league')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Error deleting league:', err)
    }
  }


  return (
    <>
      <NavBar />
      <div className={styles.leaguesContainer}>
        <div className={styles.leaguesContent}>
          <div className={styles.header}>
            <h1 className={styles.welcomeText}>
              Welcome, <span className={styles.username}>{username || 'User'}</span>!
              {isSuperuser && <span className={styles.superuserBadge}>Superuser</span>}
            </h1>
            <p className={styles.subtitle}>
              {isSuperuser ? 'View all leagues (select only leagues you participate in)' : 'Manage your fantasy stock leagues'}
            </p>
          </div>

          {error && <div className={styles.errorMessage}>{error}</div>}

          <div className={styles.actions}>
            <button
              className={styles.createButton}
              onClick={() => {
                setShowCreateModal(true)
                setError('')
              }}
            >
              Create League
            </button>
            <button
              className={styles.joinButton}
              onClick={() => {
                setShowJoinModal(true)
                setError('')
              }}
            >
              Join League
            </button>
          </div>

          <div className={styles.leaguesSection}>
            <h2 className={styles.sectionTitle}>
              {isSuperuser ? 'All Leagues' : 'Your Leagues'}
            </h2>
            {loading ? (
              <div className={styles.loading}>Loading leagues...</div>
            ) : leagues.length === 0 ? (
              <div className={styles.emptyState}>
                <p>You're not in any leagues yet.</p>
                <p>Create a new league or join an existing one to get started!</p>
              </div>
            ) : (
              <div className={styles.leaguesGrid}>
                {leagues.map((leagueItem) => {
                  const league = leagueItem.league || leagueItem
                  const leagueId = league.league_id
                  const isAdmin = leagueItem.leagueAdmin !== undefined ? leagueItem.leagueAdmin : false
                  const isParticipant = leagueItem.isParticipant !== undefined ? leagueItem.isParticipant : true
                  const participantCount = league.participant_count || 0
                  
                  if (!leagueId) {
                    console.error('League missing league_id:', league)
                    return null
                  }
                  
                  // Check if league has all participants (8)
                  const hasAllParticipants = participantCount >= 8
                  const isNotFull = participantCount < 8
                  
                  // For superusers, disable clicking if not a participant
                  // Also disable if league doesn't have all 8 participants
                  const isClickable = (!isSuperuser || isParticipant) && hasAllParticipants
                  const cardStyle = isClickable ? {} : { opacity: 0.6, cursor: 'not-allowed' }
                  
                  return (
                    <div
                      key={leagueId}
                      className={styles.leagueCard}
                      style={cardStyle}
                      onClick={(e) => handleLeagueClick(leagueId, isParticipant, participantCount, e)}
                    >
                      <h3 className={styles.leagueName}>
                        {league.name}
                        {isAdmin && <span className={styles.adminBadge}>Admin</span>}
                        {isSuperuser && !isParticipant && <span className={styles.viewOnlyBadge}>View Only</span>}
                        {isNotFull && <span className={styles.viewOnlyBadge}>Not Ready</span>}
                      </h3>
                      <div className={styles.leagueInfo}>
                        <p className={styles.leagueDetail}>
                          <span className={styles.label}>Participants:</span> {participantCount}/8
                          {isNotFull && <span style={{ color: '#f59e0b', marginLeft: '8px' }}>(Waiting for more players)</span>}
                        </p>
                        {league.start_date ? (
                          <>
                            <p className={styles.leagueDetail}>
                              <span className={styles.label}>Start Date:</span> {(() => {
                                // Parse date string to avoid timezone issues
                                const [year, month, day] = league.start_date.split('T')[0].split('-').map(Number)
                                const date = new Date(year, month - 1, day)
                                return date.toLocaleDateString()
                              })()}
                            </p>
                            <p className={styles.leagueDetail}>
                              <span className={styles.label}>End Date:</span> {(() => {
                                // Parse date string to avoid timezone issues
                                const [year, month, day] = league.end_date.split('T')[0].split('-').map(Number)
                                const date = new Date(year, month - 1, day)
                                return date.toLocaleDateString()
                              })()}
                            </p>
                          </>
                        ) : (
                          <p className={styles.leagueDetail} style={{ color: '#6b7280', fontStyle: 'italic' }}>
                            Start date will be set automatically when 8 players join
                          </p>
                        )}
                        <p className={styles.leagueDetail}>
                          <span className={styles.label}>League ID:</span> {leagueId}
                        </p>
                        {isSuperuser && !isParticipant && (
                          <p className={styles.leagueDetail} style={{ color: '#6b7280', fontStyle: 'italic' }}>
                            You are not a participant in this league
                          </p>
                        )}
                        {isNotFull && (
                          <p className={styles.leagueDetail} style={{ color: '#f59e0b', fontStyle: 'italic' }}>
                            This league needs 8 participants before it can be selected
                          </p>
                        )}
                        {(isAdmin) && (
                          <button
                            className={styles.deleteButton}
                            onClick={(e) => handleDeleteLeague(leagueId, league.name, e)}
                            title={isSuperuser ? 'Delete league (Superuser)' : 'Delete league (Admin)'}
                          >
                            Delete League
                          </button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create League Modal */}
      {showCreateModal && (
        <div className={styles.modalOverlay} onClick={() => setShowCreateModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>Create New League</h2>
            <form onSubmit={handleCreateLeague}>
              <div className={styles.formGroup}>
                <label htmlFor="leagueName">League Name</label>
                <input
                  type="text"
                  id="leagueName"
                  value={leagueName}
                  onChange={(e) => setLeagueName(e.target.value)}
                  placeholder="Enter league name"
                  required
                />
              </div>
              <div className={styles.infoMessage}>
                <p>Note: Start date will be set once 8 players join the league.</p>
              </div>
              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelButton} onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className={styles.submitButton}>
                  Create League
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join League Modal */}
      {showJoinModal && (
        <div className={styles.modalOverlay} onClick={() => setShowJoinModal(false)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>Join League</h2>
            <form onSubmit={handleJoinLeague}>
              <div className={styles.formGroup}>
                <label htmlFor="leagueId">League ID</label>
                <input
                  type="text"
                  id="leagueId"
                  value={joinLeagueId}
                  onChange={(e) => setJoinLeagueId(e.target.value)}
                  placeholder="Enter league ID"
                  required
                />
              </div>
              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelButton} onClick={() => setShowJoinModal(false)}>
                  Cancel
                </button>
                <button type="submit" className={styles.submitButton}>
                  Join League
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </>
  )
}

export default Leagues

