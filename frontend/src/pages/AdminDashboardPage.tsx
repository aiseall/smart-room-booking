import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api, Utilization } from '../services/api';

export default function AdminDashboardPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<Utilization | null>(null);

  useEffect(() => { api.getUtilization().then(setData); }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div>
      <h2>{t('admin.title')}</h2>
      <p>{t('admin.period')}: {data.period.start} ~ {data.period.end}</p>

      <div style={{ display: 'flex', gap: 20, marginBottom: 20 }}>
        <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, textAlign: 'center' }}>
          <div style={{ fontSize: 32 }}>{data.summary.total_bookings}</div>
          <div>{t('admin.totalBookings')}</div>
        </div>
        <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, textAlign: 'center' }}>
          <div style={{ fontSize: 32, color: '#d32f2f' }}>{data.summary.total_no_shows}</div>
          <div>{t('admin.noShows')}</div>
        </div>
        <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, textAlign: 'center' }}>
          <div style={{ fontSize: 32 }}>{data.summary.total_rooms}</div>
          <div>{t('admin.room')}</div>
        </div>
      </div>

      <h3>{t('admin.building')}</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 20 }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #eee' }}>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.building')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.totalBookings')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.noShows')}</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data.by_building).map(([b, stats]) => (
            <tr key={b} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{b}</td>
              <td style={{ padding: 8 }}>{stats.total_bookings}</td>
              <td style={{ padding: 8 }}>{stats.no_show_count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>{t('admin.room')}</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #eee' }}>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.room')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.building')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.totalBookings')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.noShows')}</th>
            <th style={{ textAlign: 'left', padding: 8 }}>{t('admin.utilization')}</th>
          </tr>
        </thead>
        <tbody>
          {data.rooms.map(r => (
            <tr key={r.room_id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{r.room_name}</td>
              <td style={{ padding: 8 }}>{r.building}</td>
              <td style={{ padding: 8 }}>{r.total_bookings}</td>
              <td style={{ padding: 8 }}>{r.no_show_count}</td>
              <td style={{ padding: 8 }}>{r.utilization_percent}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
