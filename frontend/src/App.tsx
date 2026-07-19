import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import FeedPage from "./pages/FeedPage";
import StoryPage from "./pages/StoryPage";

function isAuthenticated(): boolean {
  return !!localStorage.getItem("briefit_token");
}

function ProtectedRoute({ children }: { children: JSX.Element }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <div className="bg-texture min-h-screen">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/feed"
          element={
            <ProtectedRoute>
              <FeedPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/story/:id"
          element={
            <ProtectedRoute>
              <StoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={<Navigate to={isAuthenticated() ? "/feed" : "/login"} replace />}
        />
      </Routes>
    </div>
  );
}
