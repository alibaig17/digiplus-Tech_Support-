import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";

import Dashboard from "./pages/Dashboard";
import Tickets from "./pages/Tickets";
import TicketDetails from "./pages/TicketDetails";
import KnowledgeBase from "./pages/KnowledgeBase";
import Search from "./pages/Search";
import Analytics from "./pages/Analytics";
import Profile from "./pages/Profile";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout><Dashboard /></Layout>} />
      <Route path="/tickets" element={<Layout><Tickets /></Layout>} />
      <Route path="/tickets/:id" element={<Layout><TicketDetails /></Layout>} />
      <Route path="/knowledge-base" element={<Layout><KnowledgeBase /></Layout>} />
      <Route path="/search" element={<Layout><Search /></Layout>} />
      <Route path="/analytics" element={<Layout><Analytics /></Layout>} />
      <Route path="/profile" element={<Layout><Profile /></Layout>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
