/**
 * App.jsx — provider composition root.
 *
 * Provider nesting order matters:
 *   ThemeProvider  → MUI theme available everywhere
 *   AuthProvider   → auth state available to all children
 *   ProjectProvider → project state available to all children
 *   TaskProvider   → task state available to all children
 *   AppRouter      → reads auth state to guard routes
 *
 * Rule: a provider must wrap every component that consumes its context.
 * AppRouter is inside AuthProvider so ProtectedRoute can call useAuth().
 */
import { ThemeProvider, CssBaseline } from '@mui/material'
import theme from './theme'
import { AuthProvider } from './context/AuthContext'
import { ProjectProvider } from './context/ProjectContext'
import { TaskProvider } from './context/TaskContext'
import AppRouter from './router/AppRouter'

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <ProjectProvider>
          <TaskProvider>
            <AppRouter />
          </TaskProvider>
        </ProjectProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
