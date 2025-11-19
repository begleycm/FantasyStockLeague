import { BrowserRouter, Routes, Route } from "react-router-dom"
import Signup from "./PublicPages/Signup/signup.jsx"
import Login from "./PublicPages/Login/login.jsx"
import Home from "./PrivatePages/Home/home.jsx"
import ProtectedRoute from "./components/protectedRoute.jsx"
import LeagueRouteGuard from "./components/LeagueRouteGuard.jsx"
import MatchUp from "./PrivatePages/MatchUp/matchUp.jsx"
import ExploreStocks from "./PrivatePages/ExploreStocks/exploreStocks.jsx"
import Leagues from "./PrivatePages/Leagues/leagues.jsx"

function App() {
  return (
      <BrowserRouter>
        <Routes>
        <Route path="/Signup" element={<Signup></Signup>}></Route>
        <Route path="/Login" element={<Login></Login>}></Route>

        <Route path="/Private/Leagues" element={<ProtectedRoute><Leagues></Leagues></ProtectedRoute>}></Route>
        <Route path="/Private/Home" element={<ProtectedRoute><LeagueRouteGuard><Home></Home></LeagueRouteGuard></ProtectedRoute>}></Route>
        <Route path="/Private/MatchUp" element={<ProtectedRoute><LeagueRouteGuard><MatchUp></MatchUp></LeagueRouteGuard></ProtectedRoute>}></Route>
        <Route path="/Private/ExploreStocks" element={<ProtectedRoute><LeagueRouteGuard><ExploreStocks></ExploreStocks></LeagueRouteGuard></ProtectedRoute>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
