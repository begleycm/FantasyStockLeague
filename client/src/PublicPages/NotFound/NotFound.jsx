import { Link } from 'react-router-dom'
import styles from './NotFound.module.css'

function NotFound() {
  const isAuthenticated = localStorage.getItem('access_token')

  return (
    <div className={styles.notFoundContainer}>
      <div className={styles.notFoundContent}>
        <h1 className={styles.errorCode}>404</h1>
        <h2 className={styles.errorTitle}>Page Not Found</h2>
        <p className={styles.errorMessage}>
          The page you're looking for doesn't exist or has been moved.
        </p>
      </div>
    </div>
  )
}

export default NotFound

