import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';
import LanguageSwitcher from './LanguageSwitcher';
import { useEffect, useState } from 'react';

export default function Layout() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [role, setRole] = useState('');

  useEffect(() => {
    api.getMe().then(u => setRole(u.role)).catch(() => navigate('/login'));
  }, [navigate]);

  const handleLogout = () => {
    api.logout();
    navigate('/login');
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 20 }}>
      <nav style={{ display: 'flex', gap: 16, alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: 12, marginBottom: 20 }}>
        <strong>{t('app.title')}</strong>
        <Link to="/search">{t('app.search')}</Link>
        <Link to="/bookings">{t('app.myBookings')}</Link>
        {(role === 'facility_admin') && <Link to="/admin">{t('app.admin')}</Link>}
        <div style={{ flex: 1 }} />
        <LanguageSwitcher />
        <button onClick={handleLogout} style={{ cursor: 'pointer' }}>{t('app.logout')}</button>
      </nav>
      <Outlet />
    </div>
  );
}
