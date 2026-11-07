from fastapi import APIRouter, HTTPException, Query, Request
from ..models import *
campaign_router = APIRouter(
    prefix="/campaign",
    tags=["Campaign"],
    responses={404: {"details": "error.notFound"}},
)


@campaign_router.get("/", response_model=ResponseMultiple[CampaignScheme])
async def list_campaigns(language : Language = None, status : Annotated[list[CampaignStatus] | None, Query()] = None, limit : int=50, offset : int= 0):
    """
    This endpoint is used to get all campaigns.
    """
    try:
        with Server.get_parmanent_db() as conn:
            campaigns = Campaign.get_all(conn.cursor(), language=language, status=status, limit=limit, offset=offset)
        result = [CampaignScheme.from_dict(campaign) for campaign in campaigns]
        return ResponseMultiple[CampaignScheme](success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@campaign_router.get('/timeline', response_model=ResponseMultiple[Timeline])
def timeline(req : Request, group_by : str, campaign_id : str | None = None):
    """
    This endpoint is used to get all campaigns.
    """
    try:
        with Server.get_parmanent_db() as conn:
            result = Campaign.get_submission_timeline(conn.cursor(), group_by=group_by, campaign_id=campaign_id)
        return ResponseMultiple[CampaignScheme](success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
@campaign_router.get('/timeline2', response_model=ResponseSingle[StatisticsV2])
def timeline(req : Request, group_by : str, campaign_id : str | None = None, accumulated : bool = True, year : int | None = None):
    """
    This endpoint is used to get all campaigns.
    """
    try:
        with Server.get_parmanent_db() as conn:
            result = Campaign.get_submission_timeline_v2(conn.cursor(), group_by=group_by, campaign_id=campaign_id, accumulated=accumulated, year=year)
        return ResponseSingle[StatisticsV2](success=True, data=result)
    except Exception as e:
        raise e
        raise HTTPException(status_code=404, detail=str(e))
#---------------------------------- GET A CAMPAIGN ----------------------------------#
@campaign_router.get("/{campaign_id}", response_model=ResponseSingle[CampaignScheme])
async def get_campaign(req : Request, campaign_id: int, check_judge : bool = False):
    """
    This endpoint is used to get a campaign by id.
    """
    try:
        user_id = req.state.user['id']
        with Server.get_parmanent_db() as conn:
            campaign = Campaign.get_by_id(conn.cursor(), campaign_id)
            if not campaign:
                raise Exception("campaign.error.notFound")
            result = CampaignScheme.from_dict(campaign)
            if check_judge:
                is_judge = Judgement.verify_judge(conn.cursor(), campaign_id, user_id)
                result.am_i_judge = bool(is_judge)
            
            return ResponseSingle[CampaignScheme](success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
#------------------------------------------------------------------------------

#---------------------------------- LIST ALL the Jury ----------------------------------#
@campaign_router.get("/{campaign_id}/jury", response_model=ResponseMultiple[JudgeScheme])
async def list_jury(campaign_id: int):
    """
    This endpoint is used to get a campaign by id.
    """
    try:
        with Server.get_parmanent_db() as conn:
            jury = Campaign.get_jury(conn.cursor(), campaign_id, allowed=True)
        if jury is None:
            raise Exception("campaign.jury.notFound")
        result = []
        for judge in jury:
            result.append(JudgeScheme.from_dict(judge))
        return ResponseMultiple[JudgeScheme](success=True, data=result)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
#------------------------------------------------------------------------------

#---------------------------------- Add or Remove a Jury ----------------------------------#



#------------------------------------------------------------------------------
CampaignCreateByOrganizeIt
@campaign_router.post("/organizeit", response_model=ResponseSingle[CampaignScheme])
async def create_campaign_from_organizeit(req : Request, campaign: CampaignCreateByOrganizeIt):
    """
    This endpoint is used to create a new campaign from OrganizeIt data.
    """
    try:
        if campaign.name is not None:
            assert len(campaign.name.strip()) > 0, "Campaign name cannot be empty"
        assert campaign.start_at, "Campaign start date cannot be empty"
        assert campaign.end_at, "Campaign end date cannot be empty"
        jury_list = campaign.jury
        if len(jury_list) < 1:
            raise Exception("At least one jury must be selected")
        with Server.get_parmanent_db() as conn:
            # Fetch the user by User name
            # If not found, create the user by fetching from 
            # mediawiki API
            creator = User.get_username_map_guaranteed(
                    conn.cursor(), [campaign.created_by_username],
            )
            if not creator:
                raise Exception("Creator user not found")
            print(creator)
            creator_id = creator[campaign.created_by_username]['id']
            new_campaign = Campaign.create(
                conn.cursor(), campaign, creator_id
            )
        result = CampaignScheme.from_dict(new_campaign)
        notify_users(
            campaign_id=new_campaign['id'],
            campaign_name=new_campaign['name'],
            campaign_language=new_campaign['language'],
            campaign_start_date=new_campaign['start_at'],
            campaign_end_date=new_campaign['end_at'],
            campaign_creator=campaign.created_by_username,
        )
        BaseServer.log("info", req.state.user['id'], campaign.created_by_username,
                          f"Created a new campaign {result.name} with id {result.id}"
                          f" from OrganizeIt campaign creation")
        return ResponseSingle[CampaignScheme](success=True, data=result)
    except sqlite3.IntegrityError as e:
        raise e
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
#------------------------------------------------------------------------------

#---------------------------------- CREATE A CAMPAIGN ----------------------------------#
@campaign_router.post("/", response_model=ResponseSingle[CampaignScheme])
async def create_campaign(req : Request, campaign: CampaignCreate):
    """
    This endpoint is used to create a new campaign.
    """
    try:
        # assert User.is_admin(req.state.user['rights']), "You don't have `campaign` rights"
        if campaign.name is not None:
            assert len(campaign.name.strip()) > 0, "Campaign name cannot be empty"
        assert campaign.start_at, "Campaign start date cannot be empty"
        assert campaign.end_at, "Campaign end date cannot be empty"
        jury_list = campaign.jury
        if len(jury_list) < 1:
            raise Exception("At least one jury must be selected")
        with Server.get_parmanent_db() as conn:
            new_campaign = Campaign.create(conn.cursor(), campaign, req.state.user['id'])
        result = CampaignScheme.from_dict(new_campaign)
        notify_users(
            campaign_id=new_campaign['id'],
            campaign_name=new_campaign['name'],
            campaign_language=new_campaign['language'],
            campaign_start_date=new_campaign['start_at'],
            campaign_end_date=new_campaign['end_at'],
            campaign_creator=req.state.user['username'],
        )
        BaseServer.log("info", req.state.user['id'], req.state.user['username'],
                          f"Created a new campaign {result.name} with id {result.id}")
        return ResponseSingle[CampaignScheme](success=True, data=result)
    except sqlite3.IntegrityError as e:
        raise e
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
#------------------------------------------------------------------------------

#---------------------------------- UPDATE A CAMPAIGN ----------------------------------#
@campaign_router.post("/{campaign_id}", response_model=ResponseSingle[CampaignScheme])
async def update_campaign(req : Request, campaign_id: int, campaign: CampaignUpdate):
    try:
        assert User.is_admin(req.state.user['rights']), "You don't have `campaign` rights"
        jury_list = campaign.jury
        if len(jury_list) < 1:
            raise Exception("At least one jury must be selected")
        if campaign.name is not None:
            assert len(campaign.name.strip()) > 0, "Campaign name cannot be empty"
        assert campaign.start_at, "Campaign start date cannot be empty"
        assert campaign.end_at, "Campaign end date cannot be empty"
        with Server.get_parmanent_db() as conn:
            existing_campaign = Campaign.get_by_id(conn, campaign_id)
            updated_campaign = Campaign.update(conn, campaign, existing_campaign)
            cmp = CampaignScheme.from_dict(updated_campaign)
            BaseServer.log("info", req.state.user['id'], req.state.user['username'],
                            f"Updated campaign {cmp.name} with id {cmp.id}"
                            f" with data: " + str(campaign))

            return ResponseSingle[CampaignScheme](success=True, data=cmp)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    
#---------------------------------- GET RESULTS OF A CAMPAIGN ----------------------------------#
@campaign_router.get("/{campaign_id}/result", response_model=ResponseSingle[CampaignStatistics])
async def get_campaign_result(req : Request, campaign_id: int, exclude_submissions : bool = False):

    """
    This endpoint is used to get a campaign by id.
    """
    try:
        with Server.get_parmanent_db() as conn:
            campaign = Campaign.get_by_id(conn.cursor(), campaign_id)
            if not campaign:
                raise Exception("Campaign not found")
            results = Campaign.get_results(conn.cursor(), campaign_id, exclude_submissions=exclude_submissions)
            return ResponseSingle[CampaignStatistics](success=True, data=results)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))


#----------------------------- Get submissions of a campaign -----------------------------#
@campaign_router.get("/{campaign_id}/submissions", response_model=ResponseMultiple[CampaignParticipant])
async def get_campaign_submissions(req : Request, campaign_id: int, judged_by_me : bool = None):
    """
    This endpoint is used to get a campaign by id.
    """
    my_user_id = req.state.user['id']
    try:
        with Server.get_parmanent_db() as conn:
            SQL_GET_SUBMISSIONS_EVALUATIONS_ALL = """
                SELECT
                    (SELECT `username` FROM `user` WHERE `id` = `jury_vote`.`jury_id`) AS `jury_username`,
                    `jury_vote`.`vote` AS `jury_vote`,
                    `jury_vote`.`note` AS `jury_note`,
                    `jury_vote`.`created_at` AS `jury_vote_date`,
                    `submission`.`id` AS `submission_id`,
                    `submission`.`title` AS `submission_title`,
                    `submission`.`created_at` AS `submission_date`,
                    `submission`.`newly_created` AS `submission_newly_created`,
                    (`submission`.`points` / 10) AS `submission_points`,
                    `submission`.`submitted_by_username` AS `submitted_by`
                FROM
                    `submission`

                LEFT JOIN
                    `jury_vote`
                ON
                    `jury_vote`.`submission_id` = `submission`.`id`
                WHERE
                    `submission`.`campaign_id` = :campaign_id
            """
            SQL_CONDITION_JUDGED_BY_USER = """
                AND
                    `submission`.`id`
                IN
                    (
                        SELECT
                            `submission_id`
                        FROM
                            `jury_vote`
                        WHERE
                            `jury_id` = :jury_id
                        AND
                            `campaign_id` = :campaign_id
                    )
            """
            SQL_CONDITION_NOT_JUDGED_BY_USER = """
                AND
                    `submission`.`id`
                NOT IN
                    (
                        SELECT
                            `submission_id`
                        FROM
                            `jury_vote`
                        WHERE
                            `jury_id` = :jury_id
                        AND
                            `campaign_id` = :campaign_id
                    )
            """
            
            sql = SQL_GET_SUBMISSIONS_EVALUATIONS_ALL
            if judged_by_me == True:
                sql += SQL_CONDITION_JUDGED_BY_USER
            elif judged_by_me == False:
                sql += SQL_CONDITION_NOT_JUDGED_BY_USER
            
            users : dict[str, CampaignParticipant] = {}
            submissions_ : dict[int, CampaignSubmission] = {}
            cur = conn.execute(sql, {'campaign_id': campaign_id, 'jury_id': my_user_id})
            for evaluation in cur:
                submitter = evaluation['submitted_by']
                submission_id = evaluation['submission_id']
                if submitter not in users:
                    users[submitter] = CampaignParticipant(
                        username=submitter,
                        points=0,
                        submission_count=0,
                        submissions=[]
                    )
                if submission_id not in submissions_:
                    submissions_[submission_id] = CampaignSubmission(
                        title=evaluation['submission_title'],
                        submission_id=submission_id,
                        points=evaluation['submission_points'],
                        submitted_at=evaluation['submission_date'],
                        tag=(
                            'campaign.submission.tags.newlyCreated' if evaluation['submission_newly_created']
                            else 'campaign.submission.tags.expanded'),
                        evaluations=[]
                    )
                    users[submitter].submission_count += 1
                    users[submitter].points += evaluation['submission_points']
                    users[submitter].submissions.append(submissions_[submission_id])
                if evaluation['jury_username']:
                    ev = CampaignSubmissionEvaluation(
                        jury_username=evaluation['jury_username'],
                        vote = evaluation['jury_vote'],
                        note = evaluation['jury_note'],
                        date=evaluation['jury_vote_date']
                    )
                    submissions_[submission_id].evaluations.append(ev)
            result = list(users.values())
            return ResponseMultiple[CampaignParticipant](success=True, data=result)

                
                
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
#------------------------------------------------------------------------------

#---------------------------------- Next unjudged submission ----------------------------------#
@campaign_router.get("/{campaign_id}/next", response_model=ResponseSingle[int])
async def get_next_submission(req : Request, campaign_id: int):
    """
    This endpoint is used to get a campaign by id.
    """
    try:
        with Server.get_parmanent_db() as conn:
            submission_id = Judgement.next_unjudged_submission(conn.cursor(), campaign_id, req.state.user['id'])
            return ResponseSingle[int](success=True, data=submission_id)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))



#------------------------------------------------------------------------------
#---------------------------------- Approve, reject or cancel a CAMPAIGN ----------------------------------#
@campaign_router.post("/{campaign_id}/status", response_model=ResponseSingle[CampaignScheme])
async def approve_campaign(req : Request, campaign_id: int, update : CampaignStatusUpdate):
    """
    Approve, reject or cancel a campaign
    It can be cancelled by both the admin and the campaign owner
    But it can be approved or rejected only by the admin.
    """
    try:
        user = req.state.user
        
        with Server.get_parmanent_db() as conn:
            campaign = Campaign.get_by_id(conn.cursor(), campaign_id)
            assert campaign is not None, "Campaign not found"
            assert campaign['status'] not in (UpdatableStatus.cancelled.value, UpdatableStatus.ended.value), "Campaign is already cancelled or ended"
            is_admin = User.is_admin(user['rights'])
        
            if update.status in (UpdatableStatus.cancelled, UpdatableStatus.ended):
                assert is_admin, "Only admin or campaign owner can cancel or end a campaign"
            elif update.status in (UpdatableStatus.scheduled, UpdatableStatus.rejected):
                assert is_admin, "Only admin can approve or reject a campaign"
            campaign = Campaign._update_status(conn.cursor(), campaign_id, update.status, req.state.user)
            result = CampaignScheme.from_dict(campaign)
            BaseServer.log("info", req.state.user['id'], req.state.user['username'],
                            f"Updated campaign {result.name} with id {result.id}"
                            f" with data: " + str(update))
            return ResponseSingle[CampaignScheme](success=True, data=result)
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=403, detail=str(e))

#---------------------------------- Import judgements from fountain ----------------------------------#
@campaign_router.post("/{campaign_id}/fountain", response_model=ResponseSingle[str])
def import_evaluations_from_fountain(campaign_id : str, data_in_fountain : dict):
    # Import from fountain
    try:
        language = data_in_fountain['wiki']
        articles = data_in_fountain['articles']
        evaluations = []
        mark_map = data_in_fountain['marks']
        for article in articles:
            title = article['name']
            submitter = article['user']
            marks = article['marks']
            for mark in marks:
                jury = mark['user']
                if jury == submitter:
                    continue
                comment = mark['comment']
                mark_key = next(iter(mark['marks'].keys()))
                mark_index = mark['marks'][mark_key]
                point = mark_map[mark_key]['values'][mark_index]['value']
                evaluation = {
                    'campaign_id' : campaign_id,
                    'title' : title,
                    'jury_username' : jury,
                    'vote' : point,
                    'note' : comment or None
                }
                evaluations.append(evaluation)
        SQL_INSERT_EVALUATION = """
        INSERT OR IGNORE INTO
            `jury_vote`
            (`campaign_id`, `submission_id`, `jury_id`, `vote`, `note`)
        VALUES
            (
                :campaign_id,
                (SELECT `id` FROM `submission` WHERE `title` = :title AND `campaign_id` = :campaign_id),
                (SELECT `id` FROM `user` WHERE `username` = :jury_username),
                :vote,
                :note
            );
        """
        with Server.get_parmanent_db() as conn:
            Campaign.add_jury(conn.cursor(), campaign_id, data_in_fountain['jury'], language)
            conn.executemany(SQL_INSERT_EVALUATION, evaluations)
        return ResponseSingle[str](success=True, data='OK')
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

