import { Routes, Route } from "react-router";

import Header from "./components/Header/Header";

import Home from "./pages/Home/Home";
import Players from "./pages/Players/Players";
import Teams from "./pages/Teams/Teams";
import TeamDetails from "./pages/TeamDetails/TeamDetails";
import Leagues from "./pages/Leagues/Leagues";
import LeagueDetails from "./pages/LeagueDetails/LeagueDetails";
import Matches from "./pages/Matches/Matches";
import Rankings from "./pages/Rankings/Rankings";

function App() {
  return (
    <>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />

        <Route
          path="/players"
          element={<Players />}
        />

        <Route
          path="/teams"
          element={<Teams />}
        />

        <Route
          path="/teams/:teamId"
          element={<TeamDetails />}
        />

        <Route
          path="/leagues"
          element={<Leagues />}
        />

        <Route
          path="/leagues/:leagueId"
          element={<LeagueDetails />}
        />

        <Route
          path="/matches"
          element={<Matches />}
        />

        <Route
          path="/rankings"
          element={<Rankings />}
        />
      </Routes>
    </>
  );
}

export default App;