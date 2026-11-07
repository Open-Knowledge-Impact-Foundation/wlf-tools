from fastapi import APIRouter, Request, HTTPException
from ..models import *
statistics_router = APIRouter(
    prefix="/statistics",
    tags=["User"],
    responses={404: {"details": "Not found"}},
)
TOP_LIMIT = 10
START_DATE = "2024-02-01 00:00:00"
SQL_GET_TOP_CONTRIBUTOR = """
SELECT
    `submitted_by_username`, `campaign_id`, `target_wiki`,
    COUNT(*) AS `count`,
    SUM(`points`) / 10 AS `point`,
    SUM(`newly_created`) AS `newly_created`
    
FROM
    `submission`
GROUP BY
    `submitted_by_username`, `campaign_id`, `target_wiki`
ORDER BY
    `count` DESC, `point` DESC, `newly_created` DESC
LIMIT :limit
"""
SQL_GET_TOP_CAMPAIGN = """
SELECT
    `campaign_id`,
    COUNT(*) AS `count`,
    SUM(`points`) / 10 AS `point`,
    SUM(`newly_created`) AS `newly_created`, `target_wiki`
FROM
    `submission`
WHERE
     :start_at <= `submitted_at` AND `submitted_at`  < CURRENT_TIMESTAMP
GROUP BY
    `campaign_id`, `target_wiki`
ORDER BY
    `count` DESC, `point` DESC, `newly_created` DESC
LIMIT :limit
"""
SQL_GET_DAILY_UPDATE = """
SELECT
    COUNT(*) AS `count`,
    SUM(`points`) / 10 AS `point`,
    SUM(`newly_created`) AS `newly_created`,
    COUNT(DISTINCT `submitted_by_id`) AS `participants`
FROM
    `submission`
WHERE
     :start_at <= `submitted_at` AND `submitted_at`  < CURRENT_TIMESTAMP
"""


@statistics_router.post("/sendUpdate")
async def sendUpdate2(req : Request):
    """
    Send an statistics update to the respective group

    """
    try:
        import requests,  unicodedata, sqlite3
        assert req.state.user['id'] in (1, 50080034, "50080034", "1"), "Only Admin can send update"
        user_contribs: dict[str, dict[str, set[str]]] = {}
        def _get_stats_fountain(campaign_id):
            url = f'https://fountain.toolforge.org/api/editathons/{campaign_id}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                language = data.get('wiki', 'unknown')
                if language not in user_contribs:
                    user_contribs[language] = {}
                for article in articles:
                    user = unicodedata.normalize('NFC', article['user'])
                    if user not in user_contribs[language]:
                        user_contribs[language][user] = set()
                    user_contribs[language][user].add(unicodedata.normalize('NFC', article['name']))
                users = [unicodedata.normalize('NFC', article['user']) for article in articles]
                articles = [unicodedata.normalize('NFC', article['name']) for article in articles]
                return set(articles), language, set(users)
            else:
                print(f'Error fetching data: {response.status_code}')
                return set(), 'unknown', set()

        def get_stats_from_fountain(mapping, results):
            for campaign_id in mapping:
                fountain_id = mapping[campaign_id].get('fountain_id')
                if not fountain_id:
                    continue
                result, language, users = _get_stats_fountain(fountain_id)
                if language not in results:
                    results[language] = {
                        'campwiz' : set(),
                        'fountain' : set(),
                        'user' : set()
                    }
                results[language]['fountain'].update(result)
                results[language]['user'].update(users)
            return results
        campaign_map = {
            "as": { "fountain_id": "assamese-2026" },
            "bn": { "fountain_id": "fnf2026-bn" },
            "bs": { "fountain_id": "fnf2026-bs" },
            "ce": { "fountain_id": "ff-ce-2026" },
            "hi": { "fountain_id": "feminism-and-folklore-2026-hindi" },
            "en": { "fountain_id": "folklore-2026" },
            "kn": { "fountain_id": "fnf2026-kn" },
            "mad": { "fountain_id": "fnfmad2026" },
            "mni": { "fountain_id": "mni-2026" },
            "mai": { "fountain_id": "feminism-and-folklore-maithili-2026" },
            "cv": { "campwiz_id": "193" },
            "awa": { "campwiz_id": "223" },
            "ba": { "campwiz_id": "194" },
            "dag": { "campwiz_id": "225" },
            "dga": { "campwiz_id": "203" },
            "fat": { "campwiz_id": "246" },
            "ff": { "campwiz_id": "185" },
            "ga": { "campwiz_id": "185" },
            "gu": { "campwiz_id": "198" },
            "ha": { "campwiz_id": "186" },
            "hif": { "campwiz_id": "235" },
            "id": { "campwiz_id": "201" },
            "igl": { "campwiz_id": "214" },
            "kus": { "campwiz_id": "225" },
            "anp": {"fountain_id" : "feminism-and-folklore-angika-2026"},
            "tl-2": { "fountain_id": "peminismo-at-alamat-2026-sa-kamaynilaan" },
            
            "mos": { "campwiz_id": "207" },
            "mr": { "campwiz_id": "224" },
            "ne": { "campwiz_id": "211" },
            "nl": { "campwiz_id": "240" },
            "or": { "campwiz_id": "231" },
            "pcm": { "campwiz_id": "214" },
            "sah": { "campwiz_id": "196" },
            "sat": { "fountain_id": "feminism-and-folklore-2026-santali" },
            "simple": { "fountain_id": "simple-2026" },
            "sd": { "fountain_id": "fnf2026-sd", "campwiz_id": "213" },
            "sr": { "campwiz_id": "250" },
            "sw": { "campwiz_id": "259" },
            "ta": { "campwiz_id": "183" },
            "tcy": { "fountain_id": "fnf2026-tcy" },
            "tl": { "fountain_id": "fnf2026-tl", "campwiz_id": "215" },
            "tt": { "campwiz_id": "191" },
            "tyv": { "campwiz_id": "195" },
            "uz": { "campwiz_id": "255" },
            "abr": { "campwiz_id": "188" },
            "wlx": { "campwiz_id": "205" },
            "guw": { "campwiz_id": "217" },
            "gpe": { "campwiz_id": "243" },
            "tw": { "campwiz_id": "248" },
            "bcl": { "campwiz_id": "237" },
            "kcg": { "campwiz_id": "185" }
            }
        results = {}
        results = get_stats_from_fountain(campaign_map, results)
        with Server.get_parmanent_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            submissions = cursor.execute(SQL1_GET_NEW_SUBMISSIONS, {
                'last_update' : '2026-02-01T00:00:00'
            }).fetchall()
            for row in submissions:
                language = row['target_wiki']
                if language not in results:
                    results[language] = {
                        'campwiz' : set(),
                        'fountain' : set(),
                        'user' : set()
                    }
                title = unicodedata.normalize('NFC', row['title'])
                user = unicodedata.normalize('NFC', row['submitted_by_username'])
                if language not in user_contribs:
                    user_contribs[language] = {}
                if user not in user_contribs[language]:
                    user_contribs[language][user] = set()
                user_contribs[language][user].add(title)
                results[language]['campwiz'].add(title)
                results[language]['user'].add(user)
        # Format the message to be sent to the Telegram channel
        content = "Campaign Statistics:\n\n"
        content += "Language\tUnique\tCampwiz\tFountain\tUsers\n"
        sorted_by_unique_desc = sorted(results.keys(),
         key=lambda x: len(set(results[x]['campwiz']).union(set(results[x]['fountain']))), reverse=True)
        for language in sorted_by_unique_desc:
            campwiz_articles = results[language].get('campwiz', set())
            fountain_articles = results[language].get('fountain', set())
            unique_articles = campwiz_articles.union(fountain_articles)
            users = results[language].get('user', set())
            if len(unique_articles) == 0:
                continue
            content += f"{language}\t\t{len(unique_articles)}\t\t{len(campwiz_articles)}\t\t{len(fountain_articles)}\t\t{len(users)}\n"
        user_rows = []
        article_rows = []
        for language, data in user_contribs.items():
            for user, articles in data.items():
                user_rows.append((language, user, len(articles)))
                for article in articles:
                    article_rows.append((language, article))
        user_rows.sort(key=lambda x: x[2], reverse=True)
        article_rows.sort()
        content += "\nTop Contributors:\n"
        content += "Language\tUser\tUnique Articles\n"
        for language, user, count in user_rows:
            content += f"{language}\t\t{user}\t\t{count}\n"
        content += "\nTop Articles:\n"
        content += "Language\tArticle\n"
        for language, article in article_rows:
            content += f"{language}\t\t{article}\n"
        notify_statistics(content)
        return content
            
    except Exception as e:
        logger.info(e)
        print(e)
        raise HTTPException(status_code=404)



async def sendUpdate(req : Request):
    """
    Send an statistics update to the respective group

    """
    try:
        assert req.state.user['id'] in (1, 50080034), "Only Admin can send update"
        today = dp.parse("today").isoformat(' ')
        NOW = datetime.now().isoformat(' ')
        yesterday = dp.parse("1 day before").isoformat(' ')
        grand = {
            "submissions": 0,
            "points": 0,
            "participants": 0,
            "created": 0,
            "expanded": 0
        }
        daily = {
            "submissions": 0,
            "points": 0,
            "participants": 0,
            "created": 0,
            "expanded": 0
        }
        contributor_list = ''
        wikipedia_list = ''
        with Server.get_parmanent_db() as conn:
            cursor = conn.cursor()
            top_contributors = cursor.execute(SQL_GET_TOP_CONTRIBUTOR, {
                "start_at" : START_DATE,
                "end_at" : NOW,
                "limit" : TOP_LIMIT
            }).fetchall()
            contributor_list = '\n'.join(
                f'- {contributor["submitted_by_username"]} - Total {contributor["count"]} ({contributor["newly_created"]} Created, {contributor["count"] - contributor["newly_created"]} Expanded )'
                for contributor in top_contributors
            )
            top_wikipedia = cursor.execute(SQL_GET_TOP_CAMPAIGN, {
                "start_at" : START_DATE,
                "end_at" : NOW,
                "limit" : TOP_LIMIT
            }).fetchall()
            wikipedia_list = '\n'.join(
                f'- {Language(wiki["target_wiki"]).name} - Total {wiki["count"]} ({wiki["newly_created"]} Created, {wiki["count"] - wiki["newly_created"]} Expanded )'
                for wiki in top_wikipedia
            )
            daily_ = cursor.execute(
                SQL_GET_DAILY_UPDATE,
                    {
                    "start_at" : yesterday,
                    "end_at" : NOW,
                    "limit" : TOP_LIMIT
                }
            ).fetchone()
            logger.info(yesterday)
            daily['created'] = daily_['newly_created'] or 0
            daily['submissions'] = daily_['count'] or 0
            daily['expanded'] = daily['submissions'] - daily['created']
            daily['points'] = daily_['point'] or 0
            daily['participants'] = daily_['participants'] or 0

            grand_ = cursor.execute(
                SQL_GET_DAILY_UPDATE,
                    {
                    "start_at" : START_DATE,
                    "end_at" : NOW,
                    "limit" : TOP_LIMIT
                }
            ).fetchone()
            grand['created'] = grand_['newly_created'] or 0
            grand['submissions'] = grand_['count'] or 0
            grand['expanded'] = grand['submissions'] - grand['created']
            grand['points'] = grand_['point'] or 0
            grand['participants'] = grand_['participants'] or 0

            

            
        msg = f"""
Feminism and Folklore Edit-a-thon 2024
======= Daily Statistics =======
Date: {today} 
======= Since the beginning ========
- Total Submissions: {grand['submissions']}
- Total Points: {grand['points']}
- Total Participants: {grand['participants']}
- Total Articles Created: {grand['created']}
- Total Articles Expanded: {grand['expanded']}


======= Since Yesterday ========
- Total Submissions: {daily['submissions']}
- Total Points: {daily['points']}
- Total Participants: {daily['participants']}
- Total Articles Created: {daily['created']}
- Total Articles Expanded: {daily['expanded']}
======= Leaderboard =======
{wikipedia_list}
======= Top Contributors =======
{contributor_list}
===========================
This is an automated message from CampWiz Tool.
All the data is based on the submissions and points calculated by the tool.
You can also check the statistics realtime using the tool at <https://tools.wikilovesfolklore.org/campwiz/statistics>
    """
        notify_statistics(msg)
        # logger.info(msg)
        return {"status": "success"}
    except Exception as e:
        logger.info(e)
        raise HTTPException(status_code=404)





@statistics_router.get("/updates", response_model=ResponseSingle[Notifications] )
async def get_updates(req : Request, last_update: datetime=None):
    """
    Get updates about notifications pending about:
    1. New Submissions
    2. New Evaluation
    """
    try:
        # assert req.state.user['id'] in (1, 50080034), "Only Admin can send update"
        if not last_update:
            last_update = dp.parse("1 day before").isoformat(' ')
        with Server.get_parmanent_db() as conn:
            cursor = conn.cursor()
            notifications = Notification.get_pending_notifications(cursor, last_update)
        return ResponseSingle[Notifications](data=notifications, success=True)
    except Exception as e:
        logger.info(e)
        print(e)
        raise HTTPException(status_code=404)
