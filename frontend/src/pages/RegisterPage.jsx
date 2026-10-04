import { api } from '../api'
import { Field, FormErrors } from '../components/Field'
import { useForm } from '../useForm'

export function RegisterPage({ onAuthenticated }) {
  const { values, errors, submitting, handleChange, handleSubmit } = useForm(
    { username: '', email: '', nickname: '', password: '', password_confirm: '' },
    async (data) => onAuthenticated(await api.register(data)),
  )

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <h1>Create account</h1>
      <p className="muted">Pick a name worthy of a knight.</p>
      <FormErrors errors={errors} />
      <Field label="Username" name="username" value={values.username} onChange={handleChange} errors={errors} autoComplete="username" required />
      <Field label="Email" name="email" type="email" value={values.email} onChange={handleChange} errors={errors} autoComplete="email" required />
      <Field label="Nickname" name="nickname" value={values.nickname} onChange={handleChange} errors={errors} maxLength={30} required />
      <Field label="Password" name="password" type="password" value={values.password} onChange={handleChange} errors={errors} autoComplete="new-password" required />
      <Field label="Confirm password" name="password_confirm" type="password" value={values.password_confirm} onChange={handleChange} errors={errors} autoComplete="new-password" required />
      <button type="submit" disabled={submitting}>
        {submitting ? 'Creating account…' : 'Register'}
      </button>
      <p className="muted switch">
        Already registered? <a href="#/login">Log in</a>
      </p>
    </form>
  )
}
