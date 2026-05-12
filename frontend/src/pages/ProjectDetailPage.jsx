import { Typography, Box } from '@mui/material'
import { useParams } from 'react-router-dom'

export default function ProjectDetailPage() {
  const { id } = useParams()
  return (
    <Box p={4}>
      <Typography variant="h4">Project Detail</Typography>
      <Typography variant="body2" color="text.secondary" mt={1}>
        Project ID: {id} — Phase 2
      </Typography>
    </Box>
  )
}
