import { api } from '../api'
import { Field, FormErrors } from '../components/Field'
import { useForm } from '../useForm'

export function LoginPage({ onAuthenticated }) {
  const { values, errors, submitting, handleChange, handleSubmit } = useForm(
    { username: '', password: '' },
    async (data) => onAuthenticated(await api.login(data)),
  )

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h1>Welcome back</h1>
      <p className="muted">Log in to continue your quest.</p>
      <FormErrors errors={errors} />
      <Field label="Username" name="username" value={values.username} onChange={handleChange} errors={errors} autoComplete="username" required />
      <Field label="Password" name="password" type="password" value={values.password} onChange={handleChange} errors={errors} autoComplete="current-password" required />
      <button type="submit" disabled={submitting}>
        {submitting ? 'Logging in…' : 'Log in'}
      </button>
      <p className="muted switch">
        No account yet? <a href="#/register">Register</a>
      </p>
    </form>
  )
}
