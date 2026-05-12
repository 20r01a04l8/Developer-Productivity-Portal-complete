/**
 * LoginPage — form validation with React Hook Form + Yup.
 *
 * Why React Hook Form over controlled inputs:
 *   Uncontrolled by default — no re-render on every keystroke.
 *   Yup schema keeps validation rules out of JSX.
 *   `resolver` bridges RHF and Yup in one line.
 */
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import { Box, Button, TextField, Typography, Paper } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Min 6 characters').required('Password is required'),
})

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: yupResolver(schema),
  })

  const onSubmit = async (values) => {
    // Phase 2: replace with real auth API call
    // const { data } = await authClient.post('/login', values)
    // login(data.data.access_token, values.email)
    login('mock-token', values.email)
    navigate('/')
  }

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
      <Paper sx={{ p: 4, width: 360 }}>
        <Typography variant="h5" mb={3} fontWeight={700}>Sign In</Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)} display="flex" flexDirection="column" gap={2}>
          <TextField
            label="Email"
            {...register('email')}
            error={!!errors.email}
            helperText={errors.email?.message}
          />
          <TextField
            label="Password"
            type="password"
            {...register('password')}
            error={!!errors.password}
            helperText={errors.password?.message}
          />
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            Sign In
          </Button>
        </Box>
      </Paper>
    </Box>
  )
}
