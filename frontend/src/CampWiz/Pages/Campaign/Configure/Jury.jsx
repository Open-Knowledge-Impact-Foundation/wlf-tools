
import Checkbox from "@mui/material/Checkbox";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import UserInputMultiple from "../../../Components/UserInput"
import GavelIcon from '@mui/icons-material/Gavel';
import { useTranslation } from "react-i18next";
const JuryPage = ({ campaign, campaignDispatch }) => {
    const {t} = useTranslation();
    return (
        <FormGroup>
            <FormControlLabel
                sx={{ m: 1 }}
                control={
                    <Checkbox
                        checked={campaign.allowJuryToParticipate}
                        onChange={(e) => {
                            campaignDispatch({ type: 'allowJuryToParticipate', payload: e.target.checked })
                        }}
                    />
                }
                label={t('campaign.allowJuryToParticipate')}
            />
            <FormControlLabel
                sx={{ m: 1 }}
                control={
                    <Checkbox
                        checked={campaign.secretBallot}
                        onChange={(e) => {
                            campaignDispatch({ type: 'secretBallot', payload: e.target.checked })
                        }}
                    />
                }
                label={t('campaign.secretBallot')}
            />
            <FormControlLabel
                sx={{ m: 1 }}
                disabled
                control={
                    <Checkbox
                        checked={campaign.allowMultipleJudgement}
                        onChange={(e) => {
                            campaignDispatch({ type: 'allowMultipleJudgement', payload: e.target.checked })
                        }}
                    />
                }
                label={t('campaign.allowMultipleJudgements')}
            />
            <UserInputMultiple
                users={campaign.jury}
                onChange={jury => campaignDispatch({ type: 'jury', payload: jury })}
                icon={<GavelIcon />}
                fieldName={t('campaign.jury')}
                language={campaign.language}
            />
        </FormGroup>
    )
}
export default JuryPage;
