/**
 * Extracts a human-readable message from any thrown value.
 * Axios interceptors already normalise errors to `new Error(message)`,
 * but this handles edge cases (network errors, unexpected throws).
 */
export function getErrorMessage(error) {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  return 'An unexpected error occurred'
}
