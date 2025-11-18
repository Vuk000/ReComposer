// Error types for API error handling

export interface ApiError {
  detail?: string
  message?: string
  error?: string
}

export interface AxiosErrorResponse {
  response?: {
    data?: ApiError
    status?: number
    statusText?: string
  }
  message?: string
}

