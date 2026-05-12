/**
 * AppRouter — all route declarations live here, nowhere else.
 *
 * Why centralise routes:
 *   A reviewer can see the entire URL structure in one file.
 *   Adding a new page = adding one line here + creating the page component.
 *
 * ProtectedRoute:
 *   Redirects unauthenticated users to /login.
 *   Every route that requires auth wraps its element in <ProtectedRoute>.
 *   This is checked client-side only — the backend ALWAYS validates the JWT.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import LoginPage from '../pages/LoginPage'
import DashboardPage from '../pages/DashboardPage'
import ProjectsPage from '../pages/ProjectsPage'
import ProjectDetailPage from '../pages/ProjectDetailPage'
import TasksPage from '../pages/TasksPage'
import NotFoundPage from '../pages/NotFoundPage'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
        <Route path="/projects/:id" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute><TasksPage /></ProtectedRoute>} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}
