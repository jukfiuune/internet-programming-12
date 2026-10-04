import { useState } from 'react'
import { api } from '../api'
import { AVATARS } from '../avatars'
import { Avatar } from '../components/Avatar'
import { Field, FormErrors } from '../components/Field'
import { useForm } from '../useForm'

export function ProfilePage({ user, onUserChange }) {
  const [saved, setSaved] = useState(false)
  const { values, setValues, errors, submitting, handleChange, handleSubmit } = useForm(
    { nickname: user.profile.nickname, avatar_key: user.profile.avatar_key },
    async (data) => {
      setSaved(false)
      onUserChange(await api.updateProfile(data))
      setSaved(true)
    },
  )

  const dirty = values.nickname !== user.profile.nickname || values.avatar_key !== user.profile.avatar_key

  return (
    <div className="card profile">
      <div className="profile-header">
        <Avatar avatarKey={user.profile.avatar_key} size={80} />
        <div>
          <h1>{user.profile.nickname}</h1>
          <p className="muted">
            @{user.username} · {user.email}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <FormErrors errors={errors} />
        <Field label="Nickname" name="nickname" value={values.nickname} onChange={(e) => { setSaved(false); handleChange(e) }} errors={errors} maxLength={30} required />

        <fieldset className="avatars">
          <legend>Avatar</legend>
          {Object.entries(AVATARS).map(([key, { label }]) => (
            <label key={key} className={`avatar-option${values.avatar_key === key ? ' selected' : ''}`}>
              <input
                type="radio"
                name="avatar_key"
                value={key}
                checked={values.avatar_key === key}
                onChange={(e) => { setSaved(false); setValues((v) => ({ ...v, avatar_key: e.target.value })) }}
              />
              <Avatar avatarKey={key} size={56} />
              <span>{label}</span>
            </label>
          ))}
          {errors?.avatar_key?.map((message) => (
            <small key={message} className="field-error">{message}</small>
          ))}
        </fieldset>

        <button type="submit" disabled={submitting || !dirty}>
          {submitting ? 'Saving…' : 'Save changes'}
        </button>
        {saved && <p className="success" role="status">Profile updated.</p>}
      </form>
    </div>
  )
}
