import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { useCallback, useEffect, useReducer } from 'react';
import Paper from '@mui/material/Paper';
import Autocomplete from '@mui/material/Autocomplete';
import SaveIcon from '@mui/icons-material/Save';
import RightArrow from '@mui/icons-material/ArrowRight';
import LeftArrow from '@mui/icons-material/ArrowLeft';
import CircularProgress from '@mui/material/CircularProgress';
import languages from "./languages.json";
import CampWizServer from '../../Server';

const splitTranslations = (preTranslations) => {
    const MAX_FIELD_NUMS = 10;
    const minSteps = Math.ceil(Object.keys(preTranslations).length / MAX_FIELD_NUMS);
    const splitted = Object.keys(preTranslations).reduce((acc, key, index) => {
        const step = Math.floor(index / minSteps);
        if (!acc[step])
            acc[step] = {};
        acc[step][key] = preTranslations[key];
        return acc;
    }, []);
    return splitted;
}
const languageOptions = languages.map((language) => ({ label: language.name, value: language.code }));
const configurations = {
    language: '',
    step: -1,
    translations: {},
    splitted: [],
    loading: false
}
const reducer = (state, action) => {
    switch (action.type) {
        case 'language':
            return { ...state, language: action.payload };
        case 'translations':
            return { ...state, translations: action.payload };
        case 'step':
            return { ...state, step: action.payload };
        case 'splitted':
            {
                if (action.step === undefined)
                    return { ...state, splitted: action.payload };
                const sp = state.splitted;
                sp[action.step] = { ...sp[action.step], ...action.payload };
                return { ...state, splitted: [...sp] };
            }
        case 'loading':
            return { ...state, loading: action.payload };
        default:
            return state;
    }
}
const LanguageSelector = ({ configurations, configurationDispatch }) => {
    return <Autocomplete
        disablePortal
        id="combo-box-demo"
        options={languageOptions}
        sx={{ width: 300, m: 2 }}
        renderInput={(params) => <TextField {...params} label="Language" />}
        onChange={(event, value) => configurationDispatch({ type: 'language', payload: value })}
    />
}
const Step = ({ i, configurationDispatch, saveTranslations, state }) => i > -1 && (
    <Paper sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', m: 3 }}>
        {
            Object.keys(state.splitted[i]).map(key => (
                <TextField
                    key={key}
                    id="outlined-multiline-flexible"
                    label={key}
                    placeholder={state.translations[key] || ""}
                    multiline
                    helperText={state.translations[key] || ""}
                    sx={{ m: 2 }}
                    maxRows={4}
                    value={state.splitted[i][key]}
                    onChange={(event) => configurationDispatch({ type: 'splitted', payload: { [key]: event.target.value }, step: i })}
                />
            ))
        }
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-evenly', width: '100%' }}>
            <Button variant="contained" sx={{ m: 2 }} disabled={i == 0 || state.loading} onClick={() => configurationDispatch({ type: 'step', payload: i - 1 })}><LeftArrow /> Previous </Button>
            {i < state.splitted.length - 2 ? (
                <Button
                    sx={{ m: 2 }}
                    variant="contained"
                    disabled={state.loading}
                    onClick={() => configurationDispatch({ type: 'step', payload: i + 1 })}
                >Next <RightArrow />
                </Button>) : (
                <Button
                    variant="contained"
                    sx={{ m: 2 }}
                    color='success'
                    onClick={saveTranslations}
                    disabled={state.loading}
                >
                    {state.loading ? <CircularProgress size={24} sx={{ color: 'success.main' }} /> :
                    <SaveIcon />} Save
                </Button>
            )}
        </div>
    </Paper>
)
const Translator = () => {
    const [state, configurationDispatch] = useReducer(reducer, configurations);
    useEffect(() => {
        configurationDispatch({ type: 'loading', payload: true });
        CampWizServer.User.getTranslations('en').then((translations) => {
            configurationDispatch({ type: 'translations', payload: translations });
            configurationDispatch({ type: 'loading', payload: false });
        })
    }, []);
    useEffect(() => {
        if (!state.language)
            return;
        const language = typeof state.language === 'string' ? state.language : state.language.value;
        configurationDispatch({ type: 'loading', payload: true });
        CampWizServer.User.getTranslations(language).then((translations) => {
            configurationDispatch({ type: 'splitted', payload: splitTranslations(translations) });
            configurationDispatch({ type: 'step', payload: 0 });
            configurationDispatch({ type: 'loading', payload: false });
        })
    }, [state.language]);
    const saveTranslations = useCallback(() => {
        const language = typeof state.language === 'string' ? state.language : state.language.value;
        const merged = state.splitted.reduce((acc, splitted) => ({ ...acc, ...splitted }), {});
        configurationDispatch({ type: 'loading', payload: true });
        CampWizServer.User.saveTranslations(language, merged).then((translations) => {
            configurationDispatch({ type: 'translations', payload: translations });
            configurationDispatch({ type: 'splitted', payload: splitTranslations(translations) });
            configurationDispatch({ type: 'loading', payload: false });
        })
    }, [state.splitted, state.language]);
    return <Paper sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', m: 3 }}>
        <h3 style={{ textAlign: 'center', 'margin': 2 }} > Thank you for your interest in translating WikiFolklore! </h3>
        <p> Please select a language to translate to: </p>
        <LanguageSelector configurations={state} configurationDispatch={configurationDispatch} />
        {state.step > -1 && <Step i={state.step} splitted={state.splitted} configurationDispatch={configurationDispatch} saveTranslations={saveTranslations} state={state} />}

    </Paper>
}
export default Translator;