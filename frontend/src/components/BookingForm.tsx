import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api, Room } from '../services/api';

interface Props {
  room: Room;
  startTime: string;
  endTime: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export default function BookingForm({ room, startTime, endTime, onSuccess, onCancel }: Props) {
  const { t } = useTranslation();
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.createBooking({ room_id: room.id, start_time: startTime, end_time: endTime, title });
      onSuccess();
    } catch (err: unknown) {
      const apiErr = err as { status: number; detail: string };
      setError(apiErr.status === 409 ? t('booking.conflict') : apiErr.detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #ddd', padding: 16, borderRadius: 8, margin: '12px 0' }}>
      <h3>{t('booking.create')} - {room.name} ({room.building})</h3>
      <p>{startTime} ~ {endTime}</p>
      <form onSubmit={handleSubmit}>
        <input type="text" value={title} onChange={e => setTitle(e.target.value)}
          placeholder={t('booking.title')} required style={{ width: '100%', padding: 8, marginBottom: 8 }} />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={loading} style={{ marginRight: 8 }}>
          {loading ? '...' : t('booking.create')}
        </button>
        <button type="button" onClick={onCancel}>{t('booking.cancel')}</button>
      </form>
    </div>
  );
}
