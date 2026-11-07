import Button from '@mui/material/Button';
import CampaignIcon from '@mui/icons-material/Campaign';
import AddIcon from '@mui/icons-material/Add';
import ListIcon from '@mui/icons-material/List';
import SettingsIcon from '@mui/icons-material/Settings';
import GavelIcon from '@mui/icons-material/Gavel';
import { Link } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import { Trans } from 'react-i18next';
const JUDGABLE_STATUS = ['running', 'evaluating'];
export const isJudgable = (campaign) => campaign?.am_i_judge && JUDGABLE_STATUS.includes(campaign?.status);
export const DetailsButton = ({ campaign }) => (
    <Button variant="contained" color="primary" size="small" sx={{
        p: 1,
        pr: 2,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/${campaign.id}`}
    >
        <CampaignIcon />&nbsp; <Trans i18nKey="campaign.step.details" />
    </Button>
)
export const SubmitButton = ({ campaign }) => campaign?.status == 'running' && (
    <Button variant="contained" color="success" size="small" sx={{
        p: 1,
        pr: 2,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/${campaign.id}/submission/new`}
    >
        <AddIcon /> &nbsp; <Trans i18nKey="campaign.submission.new" />
    </Button>
)
export const AllButton = () => (
    <Button variant="contained" color="primary" size="small" sx={{
        padding: 1,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign`}
    >
        <ListIcon /> &nbsp; <Trans i18nKey="campaign.all" />
    </Button>
)
export const SettingsButton = ({ campaign }) => !(['cancelled', 'rejected', 'ended'].includes(campaign?.status)) && (
    <Button variant="contained" color="primary" size="small" sx={{
        padding: 1,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/${campaign.id}/edit`}
    >
        <SettingsIcon /> &nbsp; <Trans i18nKey="campaign.action.settings" />
    </Button>
)
export const SubmissionListButton = ({ campaign }) => (
    <Button variant="contained" color="primary" size="small" sx={{
        padding: 1,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/${campaign.id}/submission`}
        disabled={(['scheduled', 'rejected', 'pending'].includes(campaign?.status))}
    >
        <GavelIcon /> &nbsp; <Trans i18nKey="campaign.submission.list" />
    </Button>
)
export const CreateButton = () => (
    <Button variant="contained" color="primary" size="small" sx={{
        padding: 1,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/new`}
    >
        <AddIcon /> &nbsp; <Trans i18nKey="campaign.action.create" />
    </Button>
)
export const JudgeButton = ({ campaign, submissionID }) => (
    <Button variant="contained" color="primary" size="small" sx={{
        padding: 1,
        m: 1
    }}
        component={Link}
        to={`/campwiz/campaign/${campaign?.id}/submission/${submissionID}`}
        disabled={!submissionID  || isJudgable(campaign) == false}
    >
        <GavelIcon /> &nbsp; <Trans i18nKey="campaign.submission.judge" />
    </Button>
)
export const BigCircularLoading = (props) => (
    <CircularProgress
        sx={{ 
            margin: '0 auto',
            display: 'block',
            width: '100%' 
        }}
        size={150}
    />
)