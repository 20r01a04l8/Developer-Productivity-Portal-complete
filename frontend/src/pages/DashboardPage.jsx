import { Typography, Box } from '@mui/material'
import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  return (
    <Box p={4}>
      <Typography variant="h4">Dashboard</Typography>
      <Typography variant="body1" mt={1} color="text.secondary">
        Welcome, {user}
      </Typography>
    </Box>
  )
}
