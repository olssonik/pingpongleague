import { Switch, Route } from "wouter";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Players from "@/pages/Players";
import Games from "@/pages/Games";
import Tournament from "@/pages/Tournament";
import PlayerDetail from "@/pages/PlayerDetail";
import NotFound from "@/pages/not-found";
import TournamentsDetails from "@/pages/TournamentDetails";

function App() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/players" component={Players} />
        <Route path="/players/:username" component={PlayerDetail} />
        <Route path="/games" component={Games} />
        <Route path="/tournament" component={Tournament} />
        <Route path="/tournaments/:id" component={TournamentsDetails} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

export default App;
