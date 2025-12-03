import { useState, useEffect } from 'react'
import styles from './UsernameModal.module.css'

function UsernameModal({ isOpen, onClose }) {
  const [newUsername, setNewUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const currentUsername = localStorage.getItem('username') || ''

  useEffect(() => {
    if (isOpen) {
      setNewUsername(currentUsername)
      setError('')
      setSuccess('')
    }
  }, [isOpen, currentUsername])

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (!newUsername || newUsername.trim() === '') {
      setError('Username cannot be empty')
      return
    }

    if (newUsername === currentUsername) {
      setError('Please enter a different username')
      return
    }

    setLoading(true)

    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch('http://localhost:8000/api/user/update-username/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: newUsername.trim(),
        }),
      })

      const data = await response.json()
      if (response.ok) {
        setSuccess(data.message || 'Username updated successfully')
        // Update localStorage
        localStorage.setItem('username', data.username || newUsername.trim())
        
        // Dispatch event to notify other components
        window.dispatchEvent(new CustomEvent('usernameUpdated', { 
          detail: { username: data.username || newUsername.trim() } 
        }))
        
        // Close modal after a short delay
        setTimeout(() => {
          onClose()
        }, 1500)
      } else {
        if (data.errors && data.errors.username) {
          setError(data.errors.username[0] || 'Failed to update username')
        } else {
          setError(data.error || 'Failed to update username')
        }
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>Change Username</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="currentUsername">Current Username</label>
            <input
              type="text"
              id="currentUsername"
              value={currentUsername}
              disabled
              className={styles.inputDisabled}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="newUsername">New Username</label>
            <input
              type="text"
              id="newUsername"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              placeholder="Enter new username"
              required
              disabled={loading}
              className={styles.input}
              autoFocus
            />
          </div>

          {error && <div className={styles.errorMessage}>{error}</div>}
          {success && <div className={styles.successMessage}>{success}</div>}

          <div className={styles.modalActions}>
            <button 
              type="button"
              className={styles.cancelButton}
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className={styles.submitButton}
              disabled={loading || !newUsername || newUsername.trim() === '' || newUsername === currentUsername}
            >
              {loading ? 'Updating...' : 'Update Username'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UsernameModal

