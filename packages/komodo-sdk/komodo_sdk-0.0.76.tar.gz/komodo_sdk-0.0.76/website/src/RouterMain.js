import React, { useContext } from "react";
import {
  HashRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import "./App.css";
import Login from "./auth/Login";
import ChatBot from "./pages/chatBot";
import Profile from "./pages/profile/Profile";
import Settings from "./pages/settings/Settings";
import Chat from "./pages/chat/Chat";
import Details from "./pages/chat/Details";
import Terms from "./pages/privacy/Terms";
import Privacy from "./pages/privacy/Privacy";
import Signup from "./auth/Signup";
import Pricing from "./pages/pricing/Pricing";
import Home from "./components/Home";
import Document from "./pages/Document";
import { Helmet } from "react-helmet";
import roleContext from "../src/contexts/roleContext";
import NavigateBack from "./components/NavigateBack";

function Authorization() {
  const user = JSON.parse(localStorage.getItem("komodoUser"));
  return user?.email !== null &&
    user?.email !== undefined &&
    user?.email !== "" ? (
    <Outlet />
  ) : (
    <Navigate to={"/"} />
  );
}

function App() {
  const agentContext = useContext(roleContext);
  const menu = agentContext?.agentType?.features;

  return (
    <>
      <Helmet>
        <title>
          {agentContext?.agentType?.name && agentContext?.agentType?.company
            ? `${agentContext?.agentType?.name} - ${agentContext?.agentType?.company}`
            : ""}
        </title>
      </Helmet>

      <Router>
        <Routes>
          <Route path="/terms" element={<Terms />} />

          {agentContext?.agentType?.type === "retail" && (
            <Route path="/" strict>
              <Route index element={<Home />} />
              <Route path="/home" strict element={<Home />} />
              <Route path="/pricing" element={<Pricing />} />
            </Route>
          )}

          {agentContext?.agentType?.type === "enterprise" && (
            <Route path="/" strict>
              <Route index element={<Login />} />
              <Route path="/login" strict element={<Login />} />
              <Route path="/signup" strict element={<Signup />} />
            </Route>
          )}

          {/* </Route> */}

          <Route element={<Authorization />}>
            {menu?.includes("chat") && (
              <>
                <Route path="/chat" element={<Chat />} />
                <Route path="/details/:id" element={<Details />} />
              </>
            )}

            {menu?.includes("chatdoc") && (
              <>
                <Route path="/chatdoc" element={<ChatBot />} />
                <Route path="/chatdoc/:id" element={<ChatBot />} />
              </>
            )}

            {menu?.includes("reportbuilder") && (
              <>
                <Route path="/document" element={<Document />} />
              </>
            )}

            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/privacy" element={<Privacy />} />
          </Route>
          {/* <Route path="*" element={<Navigate to="/chat" />} /> */}
          <Route path="*" element={<NavigateBack />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
