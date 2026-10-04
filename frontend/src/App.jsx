import { useEffect, useState } from 'react'
import { api, ApiError } from './api'
import { Avatar } from './components/Avatar'
import { Icon } from './components/Icon'
import { LoginPage } from './pages/LoginPage'
import { ProfilePage } from './pages/ProfilePage'
import { RegisterPage } from './pages/RegisterPage'
import { navigate, useHashRoute } from './useHashRoute'

const PUBLIC_ROUTES = ['/login', '/register']

export default function App() {
  const route = useHashRoute()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    api
      .csrf()
      .then(() => api.me())
      .then(setUser)
      .catch((error) => {
        if (!(error instanceof ApiError && (error.status === 401 || error.status === 403))) {
          setLoadError(error.message)
        }
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (loading) return
    if (user && route !== '/profile') navigate('/profile')
    if (!user && !PUBLIC_ROUTES.includes(route)) navigate('/login')
  }, [loading, user, route])

  const handleLogout = async () => {
    try {
      await api.logout()
    } finally {
      setUser(null)
    }
  }

  let page = null
  if (!loading) {
    if (user && route === '/profile') {
      page = <ProfilePage key={user.id} user={user} onUserChange={setUser} />
    } else if (!user && route === '/register') {
      page = <RegisterPage onAuthenticated={setUser} />
    } else if (!user && route === '/login') {
      page = <LoginPage onAuthenticated={setUser} />
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="#/">
          <Icon name="swords" size={22} />
          Knights
        </a>
        {user && (
          <div className="user-menu">
            <Avatar avatarKey={user.profile.avatar_key} size={32} />
            <span className="user-name">{user.profile.nickname}</span>
            <button type="button" className="secondary" onClick={handleLogout}>
              Log out
            </button>
          </div>
        )}
      </header>
      <main>
        {loading && <p className="muted">Loading…</p>}
        {loadError && <div className="alert" role="alert"><p>{loadError}</p></div>}
        {page}
      </main>
    </div>
  )
}
