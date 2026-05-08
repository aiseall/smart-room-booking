import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api, Booking } from '../services/api';

export default function MyBookingsPage() {
  const { t } = useTranslation();
  const [bookings, setBookings] = useState<Booking[]>([]);

  const load = () => api.getMyBookings().then(setBookings);
  useEffect(() => { load(); }, []);

  const handleCancel = async (id: string) => {
    await api.cancelBooking(id);
    load();
  };

  const handleCheckIn = async (id: string) => {
    await api.checkIn(id);
    load();
  };

  const statusColor: Record<string, string> = {
    confirmed: '#1976d2', checked_in: '#388e3c', completed: '#666',
    cancelled: '#999', no_show: '#d32f2f', auto_released: '#f57c00',
  };

  return (
    <div>
      <h2>{t('app.myBookings')}</h2>
      {bookings.length === 0 && <p>{t('booking.noBookings')}</p>}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #eee' }}>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('booking.title')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.room')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('search.startTime')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('search.endTime')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('booking.status')}</th>
            <th style={{ padding: 8 }}></th>
          </tr>
        </thead>
        <tbody>
          {bookings.map(b => (
            <tr key={b.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{b.title}</td>
              <td style={{ padding: 8 }}>{b.room?.name || b.room_id}</td>
              <td style={{ padding: 8 }}>{new Date(b.start_time).toLocaleString()}</td>
              <td style={{ padding: 8 }}>{new Date(b.end_time).toLocaleString()}</td>
              <td style={{ padding: 8, color: statusColor[b.status] || '#000' }}>
                {t(`booking.${b.status}` as const)}
              </td>
              <td style={{ padding: 8 }}>
                {b.status === 'confirmed' && (
                  <>
                    <button onClick={() => handleCheckIn(b.id)} style={{ marginRight: 8 }}>
                      {t('booking.checkIn')}
                    </button>
                    <button onClick={() => handleCancel(b.id)}>{t('booking.cancel')}</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
