const BASE = '/api/v1';

let token: string | null = localStorage.getItem('token');

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw { status: res.status, detail: body.detail || res.statusText };
  }
  return res.json();
}

export const api = {
  login: async (username: string, password: string) => {
    const data = await request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    token = data.access_token;
    localStorage.setItem('token', token);
    return data;
  },
  logout: () => {
    token = null;
    localStorage.removeItem('token');
  },
  getMe: () => request<{ id: string; name: string; role: string }>('/auth/me'),
  getRooms: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<Room[]>(`/rooms${qs}`);
  },
  getAvailableRooms: (params: Record<string, string>) => {
    const qs = '?' + new URLSearchParams(params).toString();
    return request<Room[]>(`/rooms/available${qs}`);
  },
  getMyBookings: () => request<Booking[]>('/bookings'),
  createBooking: (data: { room_id: string; start_time: string; end_time: string; title: string }) =>
    request<Booking>('/bookings', { method: 'POST', body: JSON.stringify(data) }),
  cancelBooking: (id: string) => request(`/bookings/${id}`, { method: 'DELETE' }),
  checkIn: (id: string) => request(`/bookings/${id}/check-in`, { method: 'POST' }),
  getUtilization: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<Utilization>(`/admin/utilization${qs}`);
  },
  isLoggedIn: () => !!token,
};

export interface Room {
  id: string;
  name: string;
  building: string;
  floor: number;
  capacity: number;
  equipment: string[];
  is_active: boolean;
}

export interface Booking {
  id: string;
  room_id: string;
  user_id: string;
  title: string;
  start_time: string;
  end_time: string;
  status: string;
  room?: { id: string; name: string; building: string; floor: number; capacity: number };
  checked_in: boolean;
}

export interface Utilization {
  period: { start: string; end: string };
  rooms: {
    room_id: string;
    room_name: string;
    building: string;
    total_bookings: number;
    no_show_count: number;
    utilization_percent: number;
  }[];
  by_building: Record<string, { total_bookings: number; no_show_count: number; total_hours: number }>;
  summary: { total_rooms: number; total_bookings: number; total_no_shows: number };
}
