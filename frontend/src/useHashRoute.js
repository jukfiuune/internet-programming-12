import { useEffect, useState } from 'react'

const read = () => window.location.hash.replace(/^#/, '') || '/'

export function navigate(path) {
  window.location.hash = path
}

export function useHashRoute() {
  const [route, setRoute] = useState(read)

  useEffect(() => {
    const onChange = () => setRoute(read())
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])

  return route
}
