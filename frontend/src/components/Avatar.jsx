import { AVATARS } from '../avatars'
import { Icon } from './Icon'

export function Avatar({ avatarKey, size = 64 }) {
  const { color, label, icon } = AVATARS[avatarKey] ?? AVATARS['knight-1']
  return (
    <span className="avatar" role="img" aria-label={`${label} avatar`} style={{ width: size, height: size, background: color }}>
      <Icon name={icon} size={Math.round(size * 0.6)} />
    </span>
  )
}
