const icons = import.meta.glob('../assets/icons/*.svg', { eager: true, query: '?url', import: 'default' })

export function Icon({ name, size = 24, className = '' }) {
  const mask = `url("${icons[`../assets/icons/${name}.svg`]}")`
  return (
    <span
      className={`icon ${className}`}
      aria-hidden="true"
      style={{ width: size, height: size, maskImage: mask, WebkitMaskImage: mask }}
    />
  )
}
