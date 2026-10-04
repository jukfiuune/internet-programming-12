export class ApiError extends Error {
  constructor(status, errors) {
    super(Object.values(errors).flat().join(' '))
    this.status = status
    this.errors = errors
  }
}

function getCookie(name) {
  const match = document.cookie.split('; ').find((row) => row.startsWith(`${name}=`))
  return match ? decodeURIComponent(match.split('=')[1]) : null
}

async function ensureCsrfToken() {
  if (!getCookie('csrftoken')) {
    await fetch('/api/auth/csrf/', { credentials: 'same-origin' })
  }
  return getCookie('csrftoken')
}

async function request(method, path, body) {
  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (method !== 'GET') headers['X-CSRFToken'] = await ensureCsrfToken()

  let response
  try {
    response = await fetch(`/api/auth/${path}`, {
      method,
      headers,
      credentials: 'same-origin',
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, { detail: ['Cannot reach the server.'] })
  }

  if ([502, 503, 504].includes(response.status)) {
    throw new ApiError(response.status, { detail: ['Cannot reach the server.'] })
  }

  const data = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, data?.errors ?? { detail: [`Request failed (${response.status}).`] })
  }
  return data
}

export const api = {
  csrf: () => ensureCsrfToken(),
  me: () => request('GET', 'me/'),
  register: (data) => request('POST', 'register/', data),
  login: (data) => request('POST', 'login/', data),
  logout: () => request('POST', 'logout/'),
  updateProfile: (data) => request('PATCH', 'me/', data),
}
