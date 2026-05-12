/**
 * TaskContext — shared task state.
 * fetchTasksByProject scopes the fetch to a specific project.
 */
import { createContext, useContext, useState, useCallback } from 'react'
import taskClient from '../api/taskClient'

const TaskContext = createContext(null)

export function TaskProvider({ children }) {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchTasksByProject = useCallback(async (projectId) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await taskClient.get(`/?project_id=${projectId}`)
      setTasks(data.data?.items ?? [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <TaskContext.Provider value={{ tasks, loading, error, fetchTasksByProject }}>
      {children}
    </TaskContext.Provider>
  )
}

export function useTasks() {
  const ctx = useContext(TaskContext)
  if (!ctx) throw new Error('useTasks must be used inside <TaskProvider>')
  return ctx
}
