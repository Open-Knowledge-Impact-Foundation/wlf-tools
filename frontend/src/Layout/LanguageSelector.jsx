import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import DialogActions from '@mui/material/DialogActions';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import TranslateIcon from '@mui/icons-material/Translate';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import AddIcon from '@mui/icons-material/Add';
import ListItemIcon from '@mui/material/ListItemIcon';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const languages = [
    { 'code': 'ar', 'name': 'العربية (ar)' },
    { 'code': 'bn', 'name': 'বাংলা (bn)' },
    { "code": "id", "name": "Bahasa Indonesia (id)" },
    { 'code': 'de', 'name': 'Deutsch (de)' },
    { 'code': 'el', 'name': 'Ελληνικά (el)' },
    { 'code': 'en', 'name': 'English (en)' },
    { 'code': 'fr', 'name': 'Français (fr)' },
    { 'code': 'gu', 'name': 'ગુજરાતી (gu)' },
    { 'code': 'hi', 'name': 'हिन्दी (hi)' },
    { 'code': 'ml', 'name': 'മലയാളം (ml)' },
    { 'code': 'ru', 'name': 'Русский (ru)' },
    { 'code': 'ta', 'name': 'தமிழ் (ta)' },
    { 'code': 'tt', 'name': 'Татар (tt)' },
    { 'code': 'sd', 'name': 'سنڌي (sd)' },
    { 'code': 'af', 'name': 'Afrikaans (eksperimenteel) (af)' },
    { 'code': 'as', 'name': 'অসমীয়া (পৰীক্ষামূলক) (as)' },
    { 'code': 'doi', 'name': 'डोगरी (प्रयोगात्मक) (doi)' },
    { 'code': 'es', 'name': 'Español (experimental) (es)' },
    { 'code': 'fi', 'name': 'suomi (kokeellinen) (fi)' },
    { 'code': 'ha', 'name': 'Hausa (gwaji) (ha)' },
    { 'code': 'ht', 'name': 'Kreyòl ayisyen (eksperimantal) (ht)' },
    { 'code': 'hu', 'name': 'magyar (kísérleti) (hu)' },
    { 'code': 'it', 'name': 'Italiano (sperimentale) (it)' },
    { 'code': 'kn', 'name': 'ಕನ್ನಡ (ಪ್ರಾಯೋಗಿಕ) (kn)' },
    { 'code': 'lus', 'name': 'Mizo (experimental) a ni. (lus)' },
    { 'code': 'mai', 'name': 'मैथिली (प्रयोगात्मक) (mai)' },
    { 'code': 'mr', 'name': 'मराठी (प्रायोगिक) (mr)' },
    { 'code': 'ne', 'name': 'नेपाली (प्रयोगात्मक) (ne)' },
    { 'code': 'nl', 'name': 'Nederlands (experimenteel) (nl)' },
    { 'code': 'or', 'name': 'ଓଡିଆ (ପରୀକ୍ଷାମୂଳକ) (or)' },
    { 'code': 'pa', 'name': 'ਪੰਜਾਬੀ (ਪ੍ਰਯੋਗਾਤਮਕ) (pa)' },
    { 'code': 'ru', 'name': 'Русский (экспериментальный) (ru)' },
    { 'code': 'tcy', 'name': 'ತುಳು (ಪ್ರಯೋಗಾತ್ಮಕ) (tcy)' },
    { 'code': 'te', 'name': 'తెలుగు (ప్రయోగాత్మకం) (te)' },
    { 'code': 'th', 'name': 'ไทย (ทดลอง) (th)' },
    { 'code': 'tl', 'name': 'Filipino (pang-eksperimento) (tl)' },
    { 'code': 'tr', 'name': 'Türkçe (deneysel) (tr)' },
    { 'code': 'ur', 'name': 'اردو (تجرباتی) (ur)' },
    { 'code': 'vi', 'name': 'Tiếng Việt (thử nghiệm) (vi)' },


]
const LanguageSelector = ({ close }) => {
    const { t, i18n } = useTranslation();
    return <Dialog open={true} onClose={close}>
        <DialogTitle><TranslateIcon />
            {t('menu.changeLanguage')}
        </DialogTitle>
        <DialogContent>
            <List>
                {languages.map((language, index) => (
                    <ListItem key={language.code} disablePadding>
                        <ListItemButton onClick={() => i18n.changeLanguage(language.code, close)}>
                            <ListItemText primary={language.name} />
                        </ListItemButton>
                    </ListItem>
                ))}
                <Divider />
                {/* Add a new language */}
                <ListItem disablePadding sx={{
                    backgroundColor: 'rules.light',
                }}>
                    <ListItemButton
                        LinkComponent={Link} to='/campwiz/translate'
                    >
                        <ListItemIcon>
                            <AddIcon />
                        </ListItemIcon>
                        <ListItemText primary={t('menu.addNewLanguage')} />
                    </ListItemButton>
                </ListItem>
            </List>
        </DialogContent>
        <DialogActions>
            <Button onClick={close} color="primary" variant='contained'>
                {i18n.t('action.close')}
            </Button>
        </DialogActions>
    </Dialog>
}
export default LanguageSelector;
