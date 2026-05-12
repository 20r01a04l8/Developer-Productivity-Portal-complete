/**
 * main.jsx — React entry point.
 * StrictMode: highlights potential problems in development (double-renders effects).
 * It has zero impact on production builds.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
