import NavBar from "../components/navBar.jsx"
import LeagueLeaderboard from "./components/LeagueLeaderboard.jsx"
import Schedule from "./components/Schedule.jsx"
import MyStocks from "./components/MyStocks.jsx"
import styles from "./home.module.css"

function Home() {
  return (
    <>
        <NavBar></NavBar>
        <div className={styles.homeContainer}>
            <div className={styles.leftSide}>
                <LeagueLeaderboard />
                <Schedule />
            </div>
            <div className={styles.rightSide}>
                <MyStocks />
            </div>
        </div>
    </>
  )
}

export default Home