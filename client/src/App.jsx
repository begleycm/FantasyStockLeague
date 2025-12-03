import { BrowserRouter, Routes, Route } from "react-router-dom"
import Signup from "./PublicPages/Signup/signup.jsx"
import Login from "./PublicPages/Login/login.jsx"
import Home from "./PrivatePages/Home/home.jsx"
import ProtectedRoute from "./components/protectedRoute.jsx"
import LeagueRouteGuard from "./components/LeagueRouteGuard.jsx"
import ExploreStocks from "./PrivatePages/ExploreStocks/exploreStocks.jsx"
import Leagues from "./PrivatePages/Leagues/leagues.jsx"
import NotFound from "./PublicPages/NotFound/NotFound.jsx"

function App() {
  return (
      <BrowserRouter>
        <Routes>
        <Route path="/Signup" element={<Signup></Signup>}></Route>
        <Route path="/Login" element={<Login></Login>}></Route>

        <Route path="/Private/Leagues" element={<ProtectedRoute><Leagues></Leagues></ProtectedRoute>}></Route>
        <Route path="/Private/Home" element={<ProtectedRoute><LeagueRouteGuard><Home></Home></LeagueRouteGuard></ProtectedRoute>}></Route>
        <Route path="/Private/ExploreStocks" element={<ProtectedRoute><LeagueRouteGuard><ExploreStocks></ExploreStocks></LeagueRouteGuard></ProtectedRoute>}></Route>
        
        {/* Catch-all route for 404 */}
        <Route path="*" element={<NotFound></NotFound>}></Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
