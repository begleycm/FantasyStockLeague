import { Navigate, useLocation } from 'react-router-dom'

export default function LeagueRouteGuard({ children }) {
  const location = useLocation()
  const selectedLeagueId = localStorage.getItem('selected_league_id')
  
  // Allow access to Leagues page without a selected league
  if (location.pathname === '/Private/Leagues') {
    return children
  }
  
  // Redirect to Leagues page if no league is selected
  if (!selectedLeagueId) {
    return <Navigate to="/Private/Leagues" replace />
  }
  
  return children
}

