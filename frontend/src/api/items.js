const API_BASE = '/api/items'

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `Request failed (${response.status})`)
  }
  if (response.status === 204) return null
  return response.json()
}

async function request(url, options) {
  try {
    const response = await fetch(url, options)
    return await handleResponse(response)
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        'Unable to connect to the server. Please check whether the backend is running.'
      )
    }

    throw error
  }
}



export async function getItems(
  search = '',
  sortBy = 'title',
  sortOrder = 'asc'
) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.append('search', search.trim())
  }

  params.append('sort_by', sortBy)
  params.append('sort_order', sortOrder)

  return request(`${API_BASE}?${params.toString()}`)
}

export async function getItem(id) {
  return request(`${API_BASE}/${id}`)
}

export async function createItem(data) {
  return request(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function updateItem(id, data) {
  return request(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function deleteItem(id) {
  return request(`${API_BASE}/${id}`, {
    method: 'DELETE',
  })
}
