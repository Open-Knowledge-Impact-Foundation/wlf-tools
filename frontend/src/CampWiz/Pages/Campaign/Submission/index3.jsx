import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { TableVirtuoso } from 'react-virtuoso';
import Collapse from '@mui/material/Collapse';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import { styled } from '@mui/material/styles';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import HowToVoteIcon from '@mui/icons-material/HowToVote';
import DeleteIcon from '@mui/icons-material/Delete';
import CampaignHeader from '../../../Components/CampaignHeader';
import { AllButton, DetailsButton, SubmitButton, JudgeButton as JButton, isJudgable, BigCircularLoading } from '../../../Components/CampaignButtons';
import { Tab, Tabs } from '@mui/material';
import { useTranslation } from 'react-i18next';
import CampWizServer from '../../../Server';
import { useParams } from 'react-router';
import { Link } from 'react-router-dom';

const Accordion = styled((props) => (
    <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
    border: `1px solid ${theme.palette.divider}`,
    '&:not(:last-child)': {
        borderBottom: 0,
    },
    '&::before': {
        display: 'none',
    },
}));
const JudgeButton = ({ campaignID, submissionID }) => (
    <Button
        variant='contained'
        color='primary'
        size='small'
        LinkComponent={Link}
        to={`/campwiz/campaign/${campaignID}/submission/${submissionID}`}
    >
        <HowToVoteIcon />
    </Button>
)
const Evaluation = ({ vote, jury_username, note, evaluated_at }) => (
    <li
        style={{
            // backgroundColor: '#f0f0f0',
            padding: '1px',
            marginLeft: '1px',
            margin: '1px',
            borderRadius: '5px',
            fontSize: 'small'
        }}>(<b>+{vote}</b> {jury_username}) {note || null}</li>
)
const Submission = ({ campaignID, submissionID, title, tag, submittedAt, points, evaluations = [], judgable = false }) => {
    const colSpan = judgable ? 4 : 3;
    const { i18n, t } = useTranslation()
    return (
        <>
            <tr style={{ fontSize: '15.36px', margin: '2px' }}>
                <td>{title}</td>
                <td>
                    <b style={{
                        backgroundColor: '#00457c',
                        color: 'white',
                        borderRadius: '40px',
                        padding: '5px',
                        display: 'inline-block',
                        minWidth: '20px',
                        textAlign: 'center',
                        minHeight: '20px',
                    }}>
                        {t(tag, { context: 'abbr' })}
                    </b>
                </td>
                <td>{
                    new Date(submittedAt).toLocaleDateString(i18n.language, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: 'numeric',
                        second: 'numeric'
                    })
                }</td>
                <td>{points}</td>
            </tr >
            <tr>
                <td colSpan={colSpan} style={{ padding: '0px' }}>
                    <ul style={{ listStyleType: 'none', padding: 1, margin: 2, }}>
                        {evaluations.map((e, i) => <Evaluation key={i} {...e} />)}
                    </ul>
                </td>
                {judgable && <td style={{ padding: '0px' }}>
                    <JudgeButton campaignID={campaignID} submissionID={submissionID} />
                </td>
                }
            </tr>
        </>
    )
};
const TH = styled('th')({
    fontWeight: 'bold',
    // fontSize: '16px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '1px solid black',
    paddingBottom: '5px',
    textAlign: 'left',
});
const Submissions = ({ judgable = false, submissions = [], campaignID }) => {
    const { t } = useTranslation()
    return <Paper sx={{ width: '100%', padding: '5px', backgroundColor: '#dbf3ec', margin: '5px' }} component='table' elevation={0}>
        <thead>
            <tr className='submissions-nested-header'>
                <TH>{t('campaign.submission.title')}</TH>
                <TH>Tag</TH>
                <TH>Submitted At</TH>
                <TH>{t('campaign.submission.points')}</TH>
            </tr>
        </thead>
        <tbody>
            {
                submissions.map((s, i) => (
                    <Submission
                        key={i}
                        submissionID={s.submission_id}
                        title={s.title}
                        tag={s.tag}
                        submittedAt={s.submitted_at}
                        points={s.points}
                        evaluations={s.evaluations}
                        judgable={judgable}
                        campaignID={campaignID}
                    />
                ))
            }

        </tbody>
    </Paper>
}
const User = ({
    initialExpanded = false,
    username,
    language,
    points = 0,
    submission_count = 0,
    judgable = false,
    submissions = [],
    campaignID
}) => {
    const [expanded, setExpanded] = React.useState(initialExpanded);
    return (
        <>
            <tr onClick={e => setExpanded(!expanded)} style={{ cursor: 'pointer', fontSize: '15px' }}>
                <td style={{ padding: '5px' }}>
                    <ArrowForwardIosSharpIcon sx={{ fontSize: '0.9rem', transform: expanded ? 'rotate(90deg)' : 'unset', textAlign: 'left' }} />
                    &nbsp; {username}
                </td>
                <td style={{ padding: '5px' }}>{submission_count}</td>
                <td style={{ padding: '5px' }}>{points}</td>
            </tr>
            <tr>
                <td colSpan={3} style={{ padding: '0px', margin: '0 auto' }}>
                    <Collapse in={expanded} timeout={500}>
                        <Submissions username={username} judgable={judgable} submissions={submissions} campaignID={campaignID} />
                    </Collapse>
                </td>
            </tr>
        </>
    )
}



const SortedButton = ({ label, sortedBy, setSortedBy, sortOrder, setSortOrder, field, setLoading }) => (
    <TH
        onClick={() => {
            setLoading(true);
            setSortedBy(field);
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        }}
        style={{ cursor: 'pointer' }}
    >
        {label} {sortedBy === field ? sortOrder === 'asc' ? '▲' : '▼' : null}
    </TH>
);
const sorter = (a, b, sortedBy, sortOrder) => {
    if (sortOrder === 'asc') {
        if (typeof a[sortedBy] === 'string') {
            return a[sortedBy].localeCompare(b[sortedBy]);
        }
        return a[sortedBy] - b[sortedBy];
    } else {
        if (typeof a[sortedBy] === 'string') {
            return b[sortedBy].localeCompare(a[sortedBy]);
        }
        return b[sortedBy] - a[sortedBy];
    }
}

function SubmissinList({ judgable, campaign, judgedByMe }) {
    const campaignID = campaign.id;
    const { t } = useTranslation();
    const [loading, setLoading] = React.useState(true);
    const [sortedBy, setSortedBy] = React.useState('points');
    const [sortOrder, setSortOrder] = React.useState('desc');
    const commonSortParams = { sortedBy, setSortedBy, sortOrder, setSortOrder, setLoading };
    const [users, setUsers] = React.useState([]);

    React.useEffect(() => {
        setLoading(true);
        (async () => {
            try {
                const params = {}
                if(judgedByMe === 1) {
                    params.judged_by_me = false;
                } else if(judgedByMe === 2) {
                    params.judged_by_me = true;
                }
                const users = await CampWizServer.Campaign.getSubmissionExport(campaignID, params);
                users.sort((a, b) => sorter(a, b, 'points', 'desc'));
                setUsers(users);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        })();
    }, [judgedByMe, campaignID]);
    React.useEffect(() => {
        if (users.length === 0) return;
        setLoading(true);
        (async () => {
            users.sort((a, b) => sorter(a, b, sortedBy, sortOrder));
            setUsers([...users]);
            setLoading(false);
        })();
    }, [sortedBy, sortOrder]);
    if (loading) return <BigCircularLoading />
    return (
        <div>
            <table style={{ width: '95%', padding: '5px' }}>
                <thead style={{ textAlign: 'left', }}>
                    <tr style={{ borderBottom: '1px solid black' }}>
                        <SortedButton label={t('campaign.submission.submitter')} {...commonSortParams} field="username" />
                        <SortedButton label='Articles' {...commonSortParams} field="submission_count" />
                        <SortedButton label={t('campaign.submission.points')} {...commonSortParams} field="points" />
                    </tr>
                </thead>
                <tbody>
                    {users.length === 0 && <tr>
                        <td
                            colSpan={3}
                            style={{ textAlign: 'center' }}>{t('error.empty')}</td></tr>}
                    {users.map((u, i) => <User key={i} {...u} judgable={judgable} campaignID={campaignID} />)}
                </tbody>
            </table>

        </div>
    );
}
export default function SubmissionListPage() {
    const { t } = useTranslation();
    const { campaignID } = useParams();
    const [judgedByMe, setJudgedByMe] = React.useState(0);
    const [nextSubmissionID, setNextSubmissionID] = React.useState(0);
    const [loading, setLoading] = React.useState(false);
    const [campaign, setCampaign] = React.useState(null);
    React.useEffect(() => {
        (async () => {
            try {
                const campaign = await CampWizServer.Campaign.getCampaign(campaignID, { check_judge: true });
                setCampaign(campaign);
                const judgable = isJudgable(campaign);
                if(judgable) {
                    setNextSubmissionID(await CampWizServer.Page.getNextUnjudgedSubmission(campaignID));
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        })();
    }, [campaignID])
    const judgable = isJudgable(campaign);
    if (loading || campaign === null) return <BigCircularLoading />
    return (
        <div>
            <CampaignHeader campaign={campaign} />
            <div style={{ textAlign: 'center' }}>
                <SubmitButton campaign={campaign} />
                <DetailsButton campaign={campaign} />
                <JButton campaign={campaign} submissionID={nextSubmissionID || null} />
            </div>
            <Tabs value={judgedByMe} onChange={(e, val) => setJudgedByMe(val)} aria-label="Judged By Me" sx={{
                '& .MuiTabs-flexContainer': {
                    display: 'flex',
                    flexDirection: 'row',
                    justifyContent: 'center'
                }
            }}>
                <Tab label={t('campaign.submission.status.all')} />
                {judgable && <Tab label={t('campaign.submission.status.notEvaluated')} />}
                {judgable && <Tab label={t('campaign.submission.status.evaluated')} />}
            </Tabs>
            <SubmissinList judgable={judgable} campaign={campaign} judgedByMe={judgedByMe} />
        </div>
    )
}
