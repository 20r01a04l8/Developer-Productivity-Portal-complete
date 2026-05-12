/**
 * ProjectContext — shared project state for the entire app.
 *
 * Why separate from AuthContext:
 *   Single Responsibility — auth state and domain state are different concerns.
 *   ProjectContext can be unmounted/reset without touching auth.
 *
 * API calls live here, not in components.
 * Components call `useProjects().fetchProjects()` — they don't know about Axios.
 */
import { createContext, useContext, useState, useCallback } from 'react'
import projectClient from '../api/projectClient'

const ProjectContext = createContext(null)

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchProjects = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await projectClient.get('/')
      setProjects(data.data?.items ?? [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <ProjectContext.Provider value={{ projects, loading, error, fetchProjects }}>
      {children}
    </ProjectContext.Provider>
  )
}

export function useProjects() {
  const ctx = useContext(ProjectContext)
  if (!ctx) throw new Error('useProjects must be used inside <ProjectProvider>')
  return ctx
}
