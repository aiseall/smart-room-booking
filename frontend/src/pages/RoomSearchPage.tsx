import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api, Room } from '../services/api';
import BookingForm from '../components/BookingForm';

export default function RoomSearchPage() {
  const { t } = useTranslation();
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [capacity, setCapacity] = useState('');
  const [building, setBuilding] = useState('');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const params: Record<string, string> = { start, end };
    if (capacity) params.min_capacity = capacity;
    if (building) params.building = building;
    const results = await api.getAvailableRooms(params);
    setRooms(results);
    setSearched(true);
    setSelectedRoom(null);
  };

  return (
    <div>
      <h2>{t('search.title')}</h2>
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <div>
          <label>{t('search.startTime')}</label><br />
          <input type="datetime-local" value={start} onChange={e => setStart(e.target.value)} required step="1800" />
        </div>
        <div>
          <label>{t('search.endTime')}</label><br />
          <input type="datetime-local" value={end} onChange={e => setEnd(e.target.value)} required step="1800" />
        </div>
        <div>
          <label>{t('search.minCapacity')}</label><br />
          <input type="number" value={capacity} onChange={e => setCapacity(e.target.value)} min="1" />
        </div>
        <div>
          <label>{t('search.building')}</label><br />
          <select value={building} onChange={e => setBuilding(e.target.value)}>
            <option value="">{t('search.allBuildings')}</option>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
          </select>
        </div>
        <div style={{ alignSelf: 'flex-end' }}>
          <button type="submit">{t('search.searchBtn')}</button>
        </div>
      </form>

      {selectedRoom && (
        <BookingForm room={selectedRoom} startTime={start} endTime={end}
          onSuccess={() => { setSelectedRoom(null); handleSearch(new Event('submit') as unknown as React.FormEvent); }}
          onCancel={() => setSelectedRoom(null)} />
      )}

      {searched && rooms.length === 0 && <p>{t('search.noRooms')}</p>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
        {rooms.map(room => (
          <div key={room.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
            <h3>{room.name}</h3>
            <p>{t('search.building')}: {room.building} | {t('search.floor')}: {room.floor}</p>
            <p>{t('search.capacity')}: {room.capacity}</p>
            <p>{t('search.equipment')}: {room.equipment.join(', ') || '-'}</p>
            <button onClick={() => setSelectedRoom(room)}>{t('search.book')}</button>
          </div>
        ))}
      </div>
    </div>
  );
}
