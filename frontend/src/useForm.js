import { useState } from 'react'
import { ApiError } from './api'

export function useForm(initialValues, onSubmit) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setErrors(null)
    try {
      await onSubmit(values)
    } catch (error) {
      setErrors(error instanceof ApiError ? error.errors : { detail: [error.message] })
    } finally {
      setSubmitting(false)
    }
  }

  return { values, setValues, errors, submitting, handleChange, handleSubmit }
}
