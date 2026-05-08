import { useTranslation } from 'react-i18next';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  return (
    <button onClick={() => i18n.changeLanguage(i18n.language === 'zh' ? 'en' : 'zh')}
      style={{ background: 'none', border: '1px solid #ccc', padding: '4px 12px', borderRadius: 4, cursor: 'pointer' }}>
      {i18n.language === 'zh' ? 'EN' : '中文'}
    </button>
  );
}
