export function Field({ label, name, errors, ...props }) {
  const messages = errors?.[name]
  return (
    <label className="field">
      <span>{label}</span>
      <input name={name} aria-invalid={messages ? 'true' : undefined} {...props} />
      {messages?.map((message) => (
        <small key={message} className="field-error">
          {message}
        </small>
      ))}
    </label>
  )
}

export function FormErrors({ errors }) {
  const messages = [...(errors?.non_field_errors ?? []), ...(errors?.detail ?? [])]
  if (messages.length === 0) return null
  return (
    <div className="alert" role="alert">
      {messages.map((message) => (
        <p key={message}>{message}</p>
      ))}
    </div>
  )
}
