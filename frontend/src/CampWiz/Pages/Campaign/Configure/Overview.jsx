import { Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Typography } from "@mui/material"
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { useCallback, useEffect, useState } from "react";
import CampaignHeader from "../../../Components/CampaignHeader";
import RightArrow from '@mui/icons-material/ArrowForward'
import CampWizServer from "../../../Server";
import { useTranslation } from "react-i18next";
const ApproveButton = ({ onApprove, disabled, t }) => (
    <Button variant="contained" color="success" size="small" sx={{
        m: 1
    }}
        disabled={disabled}
        onClick={onApprove}
    >
        <CheckIcon />  {t('campaign.action.approve')}
    </Button>

)
const RejectButton = ({ onReject, disabled, t }) => (
    <Button variant="contained" color="error" size="small" sx={{
        m: 1
    }}
        onClick={onReject}
        disabled={disabled}
    >
        <CloseIcon />  {t('campaign.action.reject')}
    </Button>

)
const ApprovalPrompt = ({ onApprove, onReject , t}) => {
    const [openPrompt, setOpenPrompt] = useState(false);
    const approvalWrapper = (func) => {
        setOpenPrompt(false);
        func();
    }
    return (
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant='body2' component='h6' sx={{ m: 1 }}>
                {t('campaign.action.approve', {context : 'name'})}
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'center', gap: '1px' }}>
                <ApproveButton onApprove={e => setOpenPrompt(true)} disabled={openPrompt} t={t} />
                <RejectButton onReject={e => setOpenPrompt(true)} disabled={openPrompt} t={t} />
            </Box>
            <Dialog
                open={openPrompt}
                onClose={() => setOpenPrompt(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">{t('campaign.action.approve', {context : 'title'})}</DialogTitle>
                <DialogContent id="alert-dialog-description">
                    {t('campaign.action.approve', {context : 'prompt'})}
                </DialogContent>
                <DialogActions sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
                    <Button onClick={() => setOpenPrompt(false)} variant="outlined" color="error">{t('action.close')}</Button>
                    <RejectButton onReject={e => approvalWrapper(onReject)} t={t} />
                    <ApproveButton onApprove={e => approvalWrapper(onApprove)} t={t} />

                </DialogActions>
            </Dialog>
        </div>
    )
}
const CancelButton = ({ onCancel , t}) => {
    const [reviewPeriod, setReviewPeriod] = useState(5);
    useEffect(() => {
        const interval = setInterval(() => setReviewPeriod(reviewPeriod => {
            if (reviewPeriod <= 0 || reviewPeriod === NaN)
                clearInterval(interval);
            else
                return reviewPeriod - 1;
        }), 1000);
        return () => clearInterval(interval);
    }, []);
    return <Button variant="contained" color="error" disabled={reviewPeriod > 0} onClick={onCancel}>{t('campaign.action.cancel', {count : reviewPeriod})}</Button>
}
const CancelPrompt = ({ onCancel, t }) => {
    const [openPrompt, setOpenPrompt] = useState(false);
    return (
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
            <Button variant="contained" color="error" size="small" sx={{ m: 1 }}
                disabled={openPrompt}
                onClick={e => setOpenPrompt(true)}
            >
                <CloseIcon />  {t('campaign.action.cancel', {context : 'name'})}
            </Button>
            <Dialog
                open={openPrompt}
                onClose={() => setOpenPrompt(false)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title">{t('campaign.action.cancel', {context : 'title'})}</DialogTitle>
                <DialogContent id="alert-dialog-description">
                    {t('campaign.action.cancel', {context : 'prompt'})}
                </DialogContent>
                <DialogActions sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
                    <Button onClick={() => setOpenPrompt(false)} variant="outlined" color="success">{t('action.close')}</Button>
                    <CancelButton onCancel={() => setOpenPrompt(false) || onCancel()} t={t} />

                </DialogActions>
            </Dialog>
        </div>
    )

}
const Buttons = ({ campaign, campaignDispatch, setError }) => {
    const {t} = useTranslation();
    const updateStatus = useCallback(async (status) => {
        try {
            const updatedCampaign = await CampWizServer.Campaign.updateCampaignStatus(campaign.id, status);
            campaignDispatch({ type: 'status', payload: updatedCampaign.status });
            setError(null);
        } catch (e) {
            console.log(e);
            setError(e.message);
        }
    }, [campaignDispatch]);

    const actionButtons = [];
    if (campaign.status === 'pending') {
        const onApprove = () => updateStatus('scheduled');
        const onReject = () => updateStatus('rejected');
        actionButtons.push(<ApprovalPrompt key='approval' onApprove={onApprove} onReject={onReject} t={t} />);
    } 
    if (campaign.status !== 'cancelled' && campaign.status !== 'rejected' && campaign.status !== 'ended') {
        const onCancel = () => updateStatus('cancelled');
        actionButtons.push(<CancelPrompt key='cancel' onCancel={onCancel} t={t} />);
    }
    return actionButtons.length > 0 && (
        <Typography variant='body1' sx={{ m: 1, display: 'flex', flexDirection: 'row', }} component='fieldset'>
            <legend>{t('campaign.action.*')}</legend>
            <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', flexWrap: 'wrap' }}>
                {actionButtons}
            </div>
        </Typography>
    )
}
const CampaignOverview = ({ campaign, campaignDispatch, showActions = false }) => {
    const [error, setError] = useState(null);
    const {t} = useTranslation();
    const hasCampaignRights = CampWizServer.BaseServer.hasRight(CampWizServer.RIGHTS.CAMPAIGN);
    return (
        <Box component='div' sx={{ backgroundColor: 'rules.light', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant='h4' sx={{ m: 1 }}>
                {t('campaign.step.overview')}
            </Typography>
            <CampaignHeader campaign={campaign} />
            {hasCampaignRights && showActions && (
                <Buttons campaign={campaign} campaignDispatch={campaignDispatch} setError={setError} />
            )}
            <Typography variant='body1' sx={{ m: 1, display: 'flex', flexDirection: 'row',  maxWidth : '99%' }} component='fieldset'>
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
            <Typography variant='body1' sx={{ m: 1, }} component='fieldset'>
                <legend>{t('campaign.jury')}</legend>
                {campaign.jury?.map((judge, index) => <Chip key={index} label={judge} />)}
            </Typography>
            {/* <Typography variant='body1' sx={{ m: 1, backgroundColor: 'pink' }} component='fieldset'>
                <legend>Blacklist</legend>
                {campaign.blackListedUsers?.map((judge, index) => <Chip key={index} label={judge} />)}
            </Typography> */}
            <Typography variant='body1' sx={{ m: 1,  maxWidth : '99%' }} component='fieldset'>
                <legend>{t('campaign.description')}</legend>
                {campaign.description}
            </Typography>

        </Box>
    )
}
export default CampaignOverview;