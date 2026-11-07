import { useCallback, useEffect, useMemo, useState } from "react";
import 'react-data-grid/lib/styles.css';
import { useParams } from "react-router";
import CampWizServer from "../../../Server";
import CampaignHeader from "../../../Components/CampaignHeader";
import { TreeDataGrid as DataGrid2, SelectColumn } from 'react-data-grid';

import JudgeIcon from '@mui/icons-material/HowToVote';
import DeleteIcon from '@mui/icons-material/Delete';
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import { Box, Button, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import LinearProgress from "@mui/material/LinearProgress";
import { AllButton, DetailsButton, SubmitButton } from "../../../Components/CampaignButtons";
import LoadingPage from "../../../../Layout/Loader";
import Tabs from "@mui/material/Tabs"
import Tab from "@mui/material/Tab"
import Chip from "@mui/material/Chip"

import { useTranslation } from "react-i18next";
const rowGrouper = (rows, key) => {
    const result = {};
    rows.forEach(row => {
        const value = row[key];
        if (!result[value]) {
            result[value] = [];
        }
        result[value].push(row);
    });
    return result;
};
const DeleteButton = ({ onDelete, disabled = false }) => {
    const [reviewPeriod, setReviewPeriod] = useState(5);
    const { t } = useTranslation();
    useEffect(() => {
        const interval = setInterval(() => setReviewPeriod(reviewPeriod => {
            if (reviewPeriod <= 0 || reviewPeriod === NaN)
                clearInterval(interval);
            else
                return reviewPeriod - 1;
        }), 1000);
        return () => clearInterval(interval);
    }, []);
    return <Button variant="contained" color="error" disabled={reviewPeriod > 0 || disabled} onClick={onDelete}>{t('campaign.submission.action.delete', { count: reviewPeriod })}</Button>
}
const Judgements = ({ submissionID, onClose }) => {
    const { t } = useTranslation();
    const [judgements, setJudgements] = useState([]);
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        setLoading(true);
        (async () => {
            const judgements = await CampWizServer.Page.getJudgements(submissionID);
            setJudgements(judgements);
            setLoading(false);
            console.log(judgements);
        })()
    }, [submissionID]);
    return <Dialog
        open={submissionID != null}
        onClose={onClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
    >
        <DialogTitle id="alert-dialog-title">{t('campaign.submission.judgement.*')}</DialogTitle>
        <DialogContent id="alert-dialog-description">
            <table style={{ width: '99%', textAlign: 'center' }}>
                <thead>
                    <tr>
                        <th>{t('campaign.submission.judge')}</th>
                        <th>{t('campaign.submission.points')}</th>
                        <th>{t('campaign.submission.note')}</th>
                    </tr>
                </thead>
                <tbody>
                    {loading ? <tr><td colSpan={3}><LinearProgress /></td></tr> :
                        judgements.map(judgement => <tr key={judgement.id}>
                            <td>{judgement.judge_username}</td>
                            <td>{judgement.vote}</td>
                            <td>{judgement.note}</td>
                        </tr>)}
                </tbody>

            </table>
        </DialogContent>
        <DialogActions sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
            <Button onClick={onClose} variant="contained" color="success" disabled={loading}>{t('action.close')}</Button>
        </DialogActions>
    </Dialog>


}
const Submissions = ({ submissions, judgable, setSubmissionToDelete, campaignID, setSubmissionToSeeJudgements }) => {
    const {t} = useTranslation()
    const [expandedGroupIds, setExpandedGroupIds] = useState(new Set());
    const isMobile = 8;
    const columns = useMemo(() => {
        const columns = [
            { key: 'submitted_by_username', name: 'Submitter', frozen: false , maxWidth : 230},
            { key: 'title', name: t('campaign.submission.name'),frozen: false , renderGroupCell: ({ childRows }) => t('campaign.submission.lists.total', { count: childRows.length }), cellClass: 'rdg-cell-center', maxWidth : 230},
            {
                key :'newly_created', name: t('campaign.submission.tags.*'), width: 60,
                renderCell: (params) => (
                    <Chip label={t(params.row.newly_created ? 'campaign.submission.tags.newlyCreated' : 'campaign.submission.tags.expanded', { context: 'abbr' })} color="info" />
                )
            },
            {
                key: 'points', name: 'Points', renderGroupCell: ({ childRows }) => t('campaign.submission.lists.total', { count: childRows?.reduce((acc, row) => acc + row.points, 0) / 10 , context : 'points'}),
                renderCell: ({ row }) => row.points / 10, width: 100, sortable: true
            },
        ];
        if (judgable) {
            columns.push({
                key: 'action', name: 'Action', renderCell: (params) => {
                    const url = `/campwiz/campaign/${campaignID}/submission/${params.row.id}`
                    return <Box
                        sx={{
                            // display: 'flex',
                            // flexDirection: 'column',
                            // justifyContent: 'center',
                            // alignItems: 'center',
                            // flexWrap: 'wrap',
                        }} component='span'>
                        <Button variant="contained" color="primary" size="small"
                            component={Link}
                            to={url}
                            target="_self"
                        // style={{ color: 'white' }}
                        >
                            <JudgeIcon fontSize='small' />
                        </Button>
                        <Button variant="contained" color="error" size="small" onClick={(event) => setSubmissionToDelete(params.row.id) || event.stopPropagation()} >
                            <DeleteIcon fontSize='small' />
                        </Button>
                    </Box>
                }
            })
        }
        return columns;
    }, [judgable, setSubmissionToDelete, campaignID, t]);
    return <DataGrid2
        columns={columns}
        rows={submissions}
        rowKeyGetter={r => r.id}
        groupBy={['submitted_by_username']}
        rowGrouper={rowGrouper}
        expandedGroupIds={expandedGroupIds}
        onExpandedGroupIdsChange={setExpandedGroupIds}
        enableVirtualization
        className="rdg-light submissions-rdg"
        rowClass={() => 'submissions-rdg-row'}
        onCellClick={({ row }) => setSubmissionToSeeJudgements(row.id)}
        defaultColumnOptions={{
            width : '100%'
        }}
        style={{
            // fontSize : '10px'
        }}
        
    />

}
const SubmissionList = () => {
    const { t } = useTranslation();
    const { campaignID } = useParams();
    const [submissions, setSubmissions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [campaign, setCampaign] = useState(null);
    const [judgedByMe, setJudgedByMe] = useState(0);
    const [deleting, setDeleting] = useState(false);
    const [submissionToDelete, setSubmissionToDelete] = useState(null);
    const [submissionToSeeJudgements, setSubmissionToSeeJudgements] = useState(null);

    const judgable = campaign?.am_i_judge && (campaign?.status == 'running' || campaign?.status == 'evaluating');
    useEffect(() => {
        (async () => {
            setLoading(true);
            const campaign = await CampWizServer.Campaign.getCampaign(campaignID, {
                check_judge: true
            })
            setCampaign(campaign);
            setLoading(false);
        })()
    }, [campaignID, judgedByMe]);
    useEffect(() => {
        setLoading(true);
        (async () => {
            const params = {}
            if (judgedByMe > 0)
                params['judged_by_me'] = judgedByMe == 2;
            const submissions = await CampWizServer.Campaign.getSubmissions(campaignID, params);
            setSubmissions(submissions);
            setLoading(false);
        })()
    }, [campaignID, judgedByMe]);
    const deleteSubmission = useCallback(async (submissionID) => {
        try {
            setDeleting(true);
            await CampWizServer.Campaign.deleteSubmission(submissionID);
            setDeleting(false);
            setSubmissionToDelete(null);
        } catch (e) {
            console.error(e);
        }

        setSubmissions(submissions.filter(submission => submission.id != submissionID));
    }, [campaignID, submissions]);
    if (!campaign) return <LoadingPage />


    return (
        <div>
            <CampaignHeader campaign={campaign} />
            <Dialog
                open={submissionToDelete != null}
                onClose={() => setSubmissionToDelete(null)}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"

            >
                <DialogTitle id="alert-dialog-title">{t('campaign.submission.action.delete', { context: 'title' })}</DialogTitle>
                <DialogContent id="alert-dialog-description">
                    {t('campaign.submission.action.delete', { context: 'prompt' })}
                </DialogContent>
                <DialogActions sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
                    {deleting && <LinearProgress />}
                    <Button onClick={() => setSubmissionToDelete(null)} variant="outlined" color="success" disabled={deleting}>{t('action.cancel')}</Button>
                    <DeleteButton onDelete={() => deleteSubmission(submissionToDelete)} disabled={deleting} />
                </DialogActions>
            </Dialog>
            <div style={{ textAlign: 'center' }}>
                <SubmitButton campaign={campaign} />
                <DetailsButton campaign={campaign} />
                <AllButton campaign={campaign} />
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
            <Typography variant="h6" component="h6" gutterBottom sx={{ textAlign: 'center', p: 2 }}>
                {t('campaign.submission.action.see')}
            </Typography>
            {submissionToSeeJudgements && <Judgements submissionID={submissionToSeeJudgements} onClose={() => setSubmissionToSeeJudgements(null)} />}
            {/* <DataGrid
                rows={submissions}
                loading={loading}
                density="compact"
                sx={{
                    '& .MuiDataGrid-row': {
                        cursor: 'pointer'
                    }
                }}
                // getRowId={(row) => row.submissionID}
                onRowClick={(params, event) => setSubmissionToSeeJudgements(params.row.id)}
                columns={columns}
                initialState={{
                    pagination: {
                        page: 1,
                        pageSize: 25
                    }
                }}
                autoHeight
                disableSelectionOnClick
                hideFooterSelectedRowCount

            /> */}
            <Submissions
                submissions={submissions}
                judgable={judgable}
                setSubmissionToDelete={setSubmissionToDelete}
                campaignID={campaignID}
                setSubmissionToSeeJudgements={setSubmissionToSeeJudgements}
            />
        </div>
    )
};
export default SubmissionList;