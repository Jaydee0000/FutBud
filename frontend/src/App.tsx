import { Routes, Route } from "react-router";

import Header from "./components/Header/Header";

import Home from "./pages/Home/Home";
import TeamDetails from "./pages/TeamDetails/TeamDetails";
import LeagueDetails from "./pages/LeagueDetails/LeagueDetails";
import Rankings from "./pages/Rankings/Rankings";
import PlayerDetails from "./pages/PlayerDetails/PlayerDetails";
import MatchDetails from "./pages/MatchDetails/MatchDetails";

function App() {
  return (
    <>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />


        <Route
          path="/teams/:teamId"
          element={<TeamDetails />}
        />

        <Route
          path="/leagues/:leagueId"
          element={<LeagueDetails />}
        />

        <Route
          path="/rankings"
          element={<Rankings />}
        />

        <Route
          path="/players/:playerId"
          element={<PlayerDetails />}
        />

        <Route
          path="/teams/:teamId"
          element={<TeamDetails />}
        />

        <Route
          path="/teams/:teamId/squad"
          element={<TeamDetails />}
        />

        <Route
          path="/teams/:teamId/results"
          element={<TeamDetails />}
        />

        <Route
          path="/teams/:teamId/stats"
          element={<TeamDetails />}
        />

        <Route
          path="/matches/:matchId"
          element={<MatchDetails />}
        />

        <Route
          path="/matches/:matchId/lineups"
          element={<MatchDetails />}
        />

        <Route
          path="/matches/:matchId/stats"
          element={<MatchDetails />}
        />

        <Route
          path="/matches/:matchId/players"
          element={<MatchDetails />}
        />

        <Route
          path="/matches/:matchId/h2h"
          element={<MatchDetails />}
        />
      </Routes>
    </>
  );
}

export default App;