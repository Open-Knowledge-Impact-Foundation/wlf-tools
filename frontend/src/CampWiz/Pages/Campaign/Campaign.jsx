import { useEffect, useState, lazy } from "react";
import { useParams } from "react-router"
import CampaignHeader from "../../Components/CampaignHeader";
import RightArrow from '@mui/icons-material/ArrowForward'
import CampWizServer from "../../Server";
import RuleIcon from '@mui/icons-material/Rule';
import GavelIcon from '@mui/icons-material/Gavel';
import LoadingPage from "../../../Layout/Loader";
import { Box, Chip, List, Typography } from "@mui/material";
import { AllButton, SubmissionListButton, SettingsButton, SubmitButton, JudgeButton, isJudgable } from "../../Components/CampaignButtons";
import { useTranslation } from "react-i18next";
const CampaignResults = lazy(() => import('./CampaignResults'));
const Rules = ({ rules }) => {
    return (
        <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1px',
            p: 1,
            m: 1,
            border: 1,
            backgroundColor: 'rules.main',
            // color : 'black'
        }}>
            <Typography variant='h5' sx={{ textAlign: 'center', m: 1 }}>
                <RuleIcon /> &nbsp;
                Rules</Typography>
            <ol>
                {rules?.map((rule, index) => (
                    <Typography variant='body1' key={index} component='li'>
                        {rule}
                    </Typography>
                ))}
            </ol>
        </Box>

    )
}
const Jury = ({ jury }) => {
    const {t} = useTranslation();
    return (
        <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1px',
            p: 1,
            m: 1,
            border: 1,
            backgroundColor: 'rules.main',
            // color : 'black'
        }}>
            <Typography variant='h5' sx={{ textAlign: 'center', m: 1 }}>
                <GavelIcon />
                &nbsp; {t('campaign.jury')}</Typography>
            <List sx={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '1px',
                p: 1,
                m: 1,
                flexWrap: 'wrap'
            }}>
                {jury?.map((judge, index) => <Chip key={index} label={judge} />)}
            </List>
        </Box>
    )
}

const Campaign = () => {
    const {t} = useTranslation();
    const { campaignID } = useParams();
    const [campaign, setCampaign] = useState(null);
    const [jury, setJury] = useState(null);
    const [loading, setLoading] = useState(true);
    const [nextSubmissionID, setNextSubmissionID] = useState(null);
    const [error, setError] = useState(null);
    const hasCampaignRights = CampWizServer.BaseServer.hasRight(CampWizServer.RIGHTS.CAMPAIGN);
    useEffect(() => {
        (async () => {
            setLoading(true);
            try {
                const campaign = await CampWizServer.Campaign.getCampaign(campaignID, {
                    check_judge: true
                })
                if(!campaign) throw new Error("Campaign not found");
                setCampaign(campaign);
                const jury = await CampWizServer.Campaign.getJury(campaignID);
                setJury(jury);
                setError(null);
                if(isJudgable(campaign)) {
                    CampWizServer.Page.getNextUnjudgedSubmission(campaignID)
                    .then(setNextSubmissionID)
                }
            }
            catch (e) {
                setError(e.message);
            } finally {
                setLoading(false);
            }
        })()
    }, [campaignID]);
    if (loading) return <LoadingPage title={t('campaign.loading')} />
    if (error) return <div>{t(error, {defaultValue : error})}</div>
    return (
        <Box sx={{
            backgroundColor: 'list.light'
        }}>
            <CampaignHeader campaign={campaign} />
            <div style={{ textAlign: 'center' }}>
                <SubmitButton campaign={campaign} />
                <JudgeButton campaign={campaign} submissionID={nextSubmissionID} />
                <SubmissionListButton campaign={campaign} />
                {hasCampaignRights && <SettingsButton campaign={campaign} />}
                <AllButton campaign={campaign} />
                
            </div>
            <div style={{ display: 'flex', flexDirection: 'col', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Typography variant='body1' sx={{ m: 1, display: 'flex', flexDirection: 'row',  maxWidth : 'max-content', textAlign:'center' }} component='fieldset'>
                <legend>{t('campaign.duration')}</legend>
                <Typography variant='body1' sx={{ m: 1, textAlign: 'left',  }} component='fieldset'>
                    <legend>{t('campaign.startDate')}</legend>
                    {campaign.start_at}
                </Typography>
                <RightArrow sx={{
                    m: 1,
                    alignSelf: 'center'
                }} />
                <Typography variant='body1' sx={{ m: 1, textAlign: 'left',  }} component='fieldset'>
                    <legend>{t('campaign.endDate')}</legend>
                    {campaign.end_at}
                </Typography>
            </Typography>
            </div>
            
            <Typography variant='body1' sx={{ m: 1,  maxWidth : '99%' }} component='fieldset'>
                <legend>{t('campaign.description')}</legend>
                {campaign.description}
            </Typography>
            {jury && <Jury jury={jury} />}
            {['ended', 'running', 'evaluating'].includes(campaign.status) && <CampaignResults campaign={campaign} />}
        </Box>
    )
}
export default Campaign;