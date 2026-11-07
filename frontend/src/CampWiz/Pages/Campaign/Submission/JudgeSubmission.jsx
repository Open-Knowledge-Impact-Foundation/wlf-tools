import { useCallback, useEffect, useMemo, useState } from "react"
import CampWizServer from "../../../Server";
import PageInfo from "../../../Components/PageInfo";
import CheckIcon from '@mui/icons-material/Check';
import CrossIcon from '@mui/icons-material/Close';
import ListIcon from '@mui/icons-material/List';
import NextIcon from '@mui/icons-material/ArrowForward';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Fab, LinearProgress, Paper, TextField, Typography } from "@mui/material";
import { useNavigate, useParams } from "react-router";
import { Link } from "react-router-dom";
import GavelIcon from '@mui/icons-material/Gavel';
// import useMediaQuery from '@mui/material/useMediaQuery';
import { AllButton, DetailsButton,} from "../../../Components/CampaignButtons";
import LoadingPage from "../../../../Layout/Loader";
import { useTranslation } from "react-i18next";
const JudgeMentBox = ({ judge, campaignID, submissionID, nextSubmissionButton, submitted, setSubmitted }) => {
    const { t } = useTranslation();
    // const [point, setPoint] = useState(0);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [submiting, setSubmiting] = useState(false);
    const [error, setError] = useState(null);
    const judgeWrapper = useCallback(async (point, note) => {
        setSubmiting(true);
        try {
            await judge(point, note);
            setDialogOpen(false);

            setSubmitted(true);
            setError(null);
            
        } catch (e) {
            setError(e);
        } finally {
            setSubmiting(false);
        }
    }, [judge, setSubmitted]);
    const close = useCallback(() => {
        if (submiting) return;
        setDialogOpen(false);
        // setPoint(0);
        setSubmitted(false);
    }, [setSubmitted, submiting]);
    const [note, setNote] = useState('');
    return (
        <div style={{ textAlign: 'center', height: '10%', position: 'relative' }}>
            <Fab variant="extended" color="primary" size="small"
                disabled={dialogOpen}
                sx={{
                    position: "fixed",
                    bottom: (theme) => theme.spacing(3),
                    right: (theme) => theme.spacing(2)
                }}
                onClick={e => setDialogOpen(true)}
            >
                <GavelIcon fontSize='small' /> {t('campaign.submission.action.evaluate', { context: 'add' })}
            </Fab>
            <Button variant="contained" color="primary" size="small"
                sx={{
                    m: 2,
                    p: 1
                }}
                onClick={e => setDialogOpen(true)}
                disabled={dialogOpen}
            >
                <GavelIcon fontSize='small' />
                {t('campaign.submission.action.evaluate', { context: 'add' })}
            </Button>
            {submitted && <Dialog
                open={submitted}
                onClose={close}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogContent sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mt: 4
                }}>
                    <CheckIcon variant="contained" fontSize='large' color='success' />
                    <p style={{ textAlign: 'center', color: 'green', fontWeight: 'bolder' }}>
                        {t('campaign.submission.judgement.evaluationSubmittedSuccessfully')}
                    </p>

                </DialogContent>
                <DialogActions sx={{
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: 'center',
                    justifyContent: 'center',
                    // mb : 1
                }}>
                    {nextSubmissionButton}
                </DialogActions>
            </Dialog>
            }
            {dialogOpen &&
                <Dialog
                    open={dialogOpen}
                    onClose={close}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle sx={{ textAlign: 'center' }}>{t('campaign.submission.action.evaluate', { context: 'title' })}</DialogTitle>
                    <DialogContent>
                        <TextField
                            id="note"
                            label={t('campaign.submission.judgement.note')}
                            multiline
                            rows={4}
                            defaultValue=""
                            variant="outlined"
                            placeholder={t('campaign.submission.judgement.note', { context: 'placeholder' })}
                            onChange={e => setNote(e.target.value)}
                            fullWidth
                            disabled={submiting}
                            sx={{
                                mt: 2
                            }}

                        />

                        {submiting && <LinearProgress color="success" />}
                        {error && <b style={{ color: 'red', textAlign: 'center', display: 'block' }}>{error.message}</b>}
                    </DialogContent>
                    <DialogActions>
                        <Button variant="outlined" color="error" size="small"
                            sx={{
                                m: 2,
                                p: 1
                            }}
                            onClick={close}
                            disabled={submiting}
                        >
                            <LinearProgress />
                            {t('action.cancel')}
                        </Button>
                        <Button variant="contained" color="error" size="small"
                            sx={{
                                m: 2,
                                p: 1
                            }}
                            onClick={e => judgeWrapper(0, note)}
                            disabled={submiting}
                        >
                            <CrossIcon fontSize='small' />
                            {t('campaign.submission.action.reject')}
                        </Button>
                        <Button variant="contained" color="success" size="small"
                            sx={{
                                m: 2,
                                p: 1
                            }}
                            disabled={submiting}
                            onClick={e => judgeWrapper(1, note)}
                        >
                            <CheckIcon fontSize='small' />
                            {t('campaign.submission.action.accept')}
                        </Button>
                    </DialogActions>
                </Dialog>}

        </div>
    )
}
const Preview = ({ title, language, nextSubmissionButton }) => {
    // const { t } = useTranslation();
    const [previewText, setPreviewText] = useState('<p style="text-align: center;">Loading the preview, please wait...</p>');
    // const isMobile = useMediaQuery('(max-width:600px)');
    const wikipediaURL = `https://${language}.wikipedia.org`;
    const baseURL = `${wikipediaURL}/wiki/${title}`
    const styleSheet = `${wikipediaURL}/w/load.php?debug=false&lang=${language}&modules=ext.cite.styles|ext.echo.badgeicons|ext.echo.styles.badge|ext.flaggedRevs.basic|ext.gadget.logo|ext.math.scripts,styles|ext.tmh.thumbnail.styles|ext.uls.nojs|ext.wikimediaBadges|mediawiki.legacy.commonPrint,shared|mediawiki.page.gallery.styles|mediawiki.sectionAnchor|mediawiki.skinning.interface|site.styles|skins.vector.styles|wikibase.client.init|ext.kartographer.style&only=styles&skin=vector`;
    useEffect(() => {
        (async () => {
            const preview = await CampWizServer.Wiki.getParsedWikiText(language, title);
            setPreviewText(preview);
        })();
    }, [title, language]);
    const srcDoc = `<!DOCTYPE html>
            <html style='padding: 10px' >
            <head>
               <base href='${baseURL}' target='_blank'>
               <link rel='stylesheet' href='${styleSheet}' />
            </head>
            <body class='mediawiki ltr sitedir-ltr mw-hide-empty-elt ns-0 ns-subject skin-vector' style='background: white; height: auto'>
            <div class="mw-indicators" style="z-index: 1; position: relative">
               
            </div>
            
               <div id='bodyContent' class='vector-body'>${previewText}</div>
               
               <script type='text/javascript'>
                  (function() {
                     var url = window.location.href;
                     function getAnchor(element) {
                        for (;;) {
                           if (!element) return null;
                           if (element.nodeName === 'A') return element;
                           element = element.parentElement;
                        }
                     }
                     document.body.addEventListener('click', function(e) {
                        var anchor = getAnchor(e.target);
                        if (!anchor) return;
                        var href = anchor.getAttribute('href');
                        if (!href || href[0] != '#') return;
                        // window.location.hash = href;
                        window.location.replace(url + href);
                        e.preventDefault();
                     }, true);
                  })();
               </script>
            </body>
            </html>
            `
    return (
        previewText ? <Paper
            component="iframe"
            elevation={3}
            sx={{
                position: 'relative',
                p: 0,
                m: 0,
                border: 0,
                my: 2,
                alignSelf: 'center',
                height: '80%',
                minHeight: '500px',
                overflowX: 'revert',
                width: '100%',
            }}
            sandbox="allow-popups allow-scripts"
            srcDoc={srcDoc}
        /> : <MissingArticle
            title={title}
            language={language}
            nextSubmissionButton={nextSubmissionButton}
        />
    )
}
const MissingArticle = ({ title, language, nextSubmissionButton }) => {
    // const [nextSubmission, setNextSubmission] = useState(null);
    const url = `https://${language}.wikipedia.org/wiki/${title}`;
    return <Dialog
        open={true}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
    >
        <DialogTitle id="alert-dialog-title">{"Article does not exist"}</DialogTitle>
        <DialogContent>
            <Typography variant="body1" id="alert-dialog-description">
                The article with the title <a href={url} target="_blank" rel="noreferrer">{title}</a> does not exist in the {language}wiki.
                It might be either deleted or moved to another title <b>without keeping redirect</b>.
                Please Click the button below to go to the next submission.
            </Typography>
        </DialogContent>
        <DialogActions>
            {nextSubmissionButton}
        </DialogActions>
    </Dialog>
}
const JudgeSubmission = () => {
    const { t } = useTranslation();

    const { campaignID, submissionID } = useParams();
    const [submission, setSubmission] = useState(null);
    const [nextSubmissionID, setNextSubmissionID] = useState(null);
    const [campaign, setCampaign] = useState(null);
    const [title, setTitle] = useState('');
    const [dialogOpen, setDialogOpen] = useState(false);
    const navigate = useNavigate();
    const NextSubmissionButton = useMemo(() => nextSubmissionID ? (
        <Button variant="contained" color="success" size="small"
            sx={{
                m: 2,
                p: 1,

            }}
            style={{
                textDecoration: 'none',
                color: 'white'
            }}
            onClick={e => {
                setDialogOpen(false);
                navigate(`/campwiz/campaign/${campaignID}/submission/${nextSubmissionID}`
                )}}
        >
            <NextIcon fontSize='small' />
            {t('campaign.submission.judgement.nextSubmission')}
        </Button>) : (
        <Button variant="contained" color="info" size="small"
            sx={{
                m: 2,
                p: 1,

            }}
            style={{
                textDecoration: 'none',
                color: 'white'
            }}
            component={Link}
            to={`/campwiz/campaign/${campaignID}/submission`}
        >
            <ListIcon fontSize='small' />
            {t('campaign.submission.judgement.backToSubmissions')}
        </Button>
    ), [campaignID, navigate, nextSubmissionID, t]);
    const preview = useMemo(() => {
        if (!submission) return <div>{t('campaign.submission.preview', { context: 'loading' })}</div>
        return <Preview title={title} language={submission.target_wiki} nextSubmissionButton={NextSubmissionButton} />
    }, [submission, t, title, NextSubmissionButton]);

    const judge = useCallback(async (point, note) => {
        const judgement = await CampWizServer.Page.judgeSubmission(submission.id, point, note);
        console.log(judgement);
    }, [submission]);

    useEffect(() => {
        // create a new base element and set it's href to the intended url
        (async () => {
            const [subm, camp] = await Promise.all([CampWizServer.Page.getSubmission(submissionID, true), CampWizServer.Campaign.getCampaign(campaignID, { check_judge: true })])
            setSubmission(subm);
            setNextSubmissionID(subm?.next_id);
            setTitle(subm.title);
            // setLanguage(subm.language);
            setCampaign(camp);
        })();
    }, [campaignID, submissionID]);
    if (!submission || !campaign) return <LoadingPage title={t('campaign.submission.loading')} />
    if (campaign.am_i_judge === false) return <div style={{ textAlign: 'center' }}>
        <h1>{t('campaign.error.youAreNotJudge')}</h1>
        <AllButton campaign={campaign} />
    </div>
    return <div>
        {/* <CampaignHeader campaign={campaign} /> */}
        <div style={{ textAlign: 'center' }}>
            <DetailsButton campaign={campaign} />
            <AllButton campaign={campaign} />
        </div>
        <div style={{ textAlign: 'center', height: '8%', position: 'relative' }}>
            {submission && <PageInfo title={title} campaign={campaign} submission={submission} />}
        </div>
        {preview}
        <JudgeMentBox judge={judge} campaignID={campaignID} submissionID={submissionID} nextSubmissionButton={NextSubmissionButton} submitted={dialogOpen} setSubmitted={setDialogOpen} />
    </div>
}
export default JudgeSubmission;
