from enum import Enum
from datetime import datetime, timedelta
import jwt, os, requests, time, sqlite3, re, random
import logging as logger
import sentry_sdk
from ._sql import *
from ._scheme import *
#---------------------------- LOAD the constants ----------------------------
VERIFIER_OAUTH_CLIENT_ID        =   os.environ['VERIFIER_OAUTH_CLIENT_ID']
VERIFIER_OAUTH_CLIENT_SECRET    =   os.environ['VERIFIER_OAUTH_CLIENT_SECRET']
JWT_SECRET_KEY                  =   os.environ['JWT_SECRET_KEY']
BOT_AUTH_TOKEN = os.getenv("BOT_AUTH_TOKEN") # The credentails to request to the API
HOSTNAME                        =   os.getenv('HOSTNAME', 'http://localhost:5000')
META_OAUTH_AUTHORIZE_URL = 'https://meta.wikimedia.org/w/rest.php/oauth2/authorize'
META_OAUTH_ACCESS_TOKEN_URL = 'https://meta.wikimedia.org/w/rest.php/oauth2/access_token'
META_PROFILE_URL = 'https://meta.wikimedia.org/w/rest.php/oauth2/resource/profile'
URL = "https://en.wikipedia.org/w/api.php"
TG_BOT_AUTH_TOKEN = os.environ.get('TG_BOT_TOKEN')
TG_GROUP_CHAT_ID = -4006740813
TG_FNF_COORDINATOR_CHAT_ID = -1001169303860
TG_FNFC_GROUP_CHAT_ID = ( TG_GROUP_CHAT_ID, )
WIKIPEDIA_ENDPOINT_FORMAT = "https://{lang}.wikipedia.org/w/api.php"
#---------------------------- LOADED the constants ----------------------------
VERSION = "2.0.0"
# Both IPv4 and IPv6
IPV_PATTERN = re.compile("^(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|(?:[0-9a-fA-F:]+)$")
try:
    with open("VERSION", "r") as f:
        VERSION = f.read().strip()
        logger.info(f"Version {VERSION}")
except:
    pass
sess = requests.Session()
ua = {
    "User-Agent": f"ListGenBot/{VERSION} ({HOSTNAME}) (python-requests) " ,
}
sess.headers = {
    **ua,
    "Authorization" : f"Bearer {BOT_AUTH_TOKEN}"
}
def get_random_hex_color():
    return '#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
INCUBATOR_WIKI_LIST = {
    "wlx",
    "igl",
    "abr",
}
INCUBATOR_PREFIX = "Wp/{lang}/"

#-
class Permission(Enum):
    TASK =  1 << 0
    STATS = 1 << 1
    CATEGORY = 1 << 2
    TOPIC = 1 << 3
    GRANT = 1 << 4
    CAMPAIGN = 1 << 5
    @staticmethod
    def has_access(rights : int, right : int):
        return bool(rights & right)
    @staticmethod
    def rights_to_int(rights : dict) -> int:
        right_int = 0
        for r in rights:
            if rights[r]:
                right_int |= (Permission._member_map_[r].value)
        return right_int
    @staticmethod
    def int_to_rights(right : int):
        rights = {}
        for r in Permission._member_map_:
            if right & (1 << Permission._member_map_[r].value):
                rights[r] = True
        return rights
    @staticmethod
    def grant_rights(grantor_rights : dict, grantee_rights : dict, new_rights : dict) -> int:
        if type(grantor_rights) == int:
            grantor_rights = Permission.int_to_rights(grantor_rights)
        if type(grantee_rights) == int:
            grantee_rights = Permission.int_to_rights(grantee_rights)
        if type(new_rights) == int:
            new_rights = Permission.int_to_rights(new_rights)
        prev_right_int = Permission.rights_to_int(grantee_rights)
        if not grantor_rights['grant']:
            return prev_right_int
        # If the grantor has granting right
        
        for right in new_rights:
            if grantor_rights[right]:
                grantee_rights[right] = True
            else:
                return prev_right_int
        else:
            return Permission.rights_to_int(grantee_rights)




class BaseServer:
    PERMANENT_DB = 'data.db'
    TEMPORARY_DB = 'articles.db'
    LOG_DB = 'logs.db'
    @staticmethod
    def get_parmanent_db():
        conn = sqlite3.connect(BaseServer.PERMANENT_DB)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    @staticmethod
    def get_temporary_db():
        conn = sqlite3.connect(BaseServer.TEMPORARY_DB)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def get_log_db():
        conn = sqlite3.connect(BaseServer.LOG_DB)
        conn.row_factory = sqlite3.Row
        return conn
    @staticmethod
    def log(level, user_id, username, message, conn=None, auto_commit=True):
        if conn is None:
            conn = BaseServer.get_log_db()
        with conn:
            conn.execute(SQL3_INSERT_LOG, {
                'level': level,
                'user_id': user_id,
                'username': username,
                'message': message
            })
            if auto_commit:
                conn.commit()
    @staticmethod
    def init():
        with BaseServer.get_parmanent_db() as conn:
            conn.executescript(SQL1_INIT)
        with BaseServer.get_temporary_db() as conn:
            conn.executescript(SQL2_INIT)
        with BaseServer.get_log_db() as conn:
            conn.executescript(SQL3_INIT)
    @staticmethod
    def get_stats() -> "dict[str, int]":
        stats = {
            'registered_user_count' : 0,
            'total_tasks' : 0,
            'total_articles_served' : 0,
            'total_categories' : 0
        }
        with BaseServer.get_parmanent_db() as conn:
            user_stats = conn.execute(SQL1_GET_STATISTICS_FROM_USER).fetchone()
            stats['registered_user_count'] = user_stats['registered_user_count']
            stats['total_articles_served'] = user_stats['total_articles']
            stats['total_categories'] = user_stats['total_categories']
            stats['total_tasks'] = user_stats['total_tasks']
        return stats
    @staticmethod
    def get_api_endpoint(lang):
        if lang in INCUBATOR_WIKI_LIST:
            return 'https://incubator.wikimedia.org/w/api.php'
        return WIKIPEDIA_ENDPOINT_FORMAT.format(lang=lang)
    @staticmethod
    def get_page_with_prefix(lang, title):
        if lang in INCUBATOR_WIKI_LIST:
            prefix = INCUBATOR_PREFIX.format(lang=lang)
            if title.startswith(prefix):
                return title
            return prefix + title
        return title
    @staticmethod
    def get(*lw, lang='en', **kw) -> dict:
        url = BaseServer.get_api_endpoint(lang)
        return sess.get(url, *lw, **kw).json()
    @staticmethod
    def post(*lw, lang='en', **kw) -> dict:
        url = BaseServer.get_api_endpoint(lang)
        return sess.post(url, *lw, **kw).json()
class BaseUser:
    @staticmethod
    def generate_login_url(redirect_uri='/'):
        endpoint = META_OAUTH_AUTHORIZE_URL
        params = {
            'response_type' : 'code',
            'client_id' : VERIFIER_OAUTH_CLIENT_ID,
            'state' : redirect_uri,
            'redirect_uri' : f'{HOSTNAME}/user/callback',
        }
        return endpoint + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
    @staticmethod
    def generate_access_token(code, state) -> tuple[str, str, str]:
        COOKIE_NAME = 'auth'
        redirect_uri = state
        logger.info(redirect_uri)
        endpoint = META_OAUTH_ACCESS_TOKEN_URL
        params = {
            'grant_type' : 'authorization_code',
            'code' : code,
            'client_id' : VERIFIER_OAUTH_CLIENT_ID,
            'client_secret' : VERIFIER_OAUTH_CLIENT_SECRET,
            'redirect_uri' : f'{HOSTNAME}/user/callback',
        }
        res = requests.post(endpoint, data=params, headers=ua).json()
        if 'error' in res:
            return COOKIE_NAME, '', '/error?code=' + res['error']
        access_token = res['access_token']
        endpoint = META_PROFILE_URL
        profile : dict= requests.get(endpoint, headers={'Authorization': f"Bearer {access_token}", **ua}).json()
        if 'error' in profile:
            sentry_sdk.capture_message(profile['error'], level='error')
            return COOKIE_NAME, '', '/error?code=' + profile['error']
        user_id = profile['sub']
        username = profile['username']
        sentry_sdk.set_user({'id': user_id, 'username': username})
        sentry_sdk.set_extra("profile", profile)
        registered_at = datetime.strptime(profile['registered'] or '20000101000000', '%Y%m%d%H%M%S').isoformat()
        with BaseServer.get_parmanent_db() as conn:
            user = BaseUser.get_by_id(conn.cursor(), user_id)
            if user is None:
                # Create new user
                BaseUser.create(conn, user_id, username, {
                    'TASK': True,
                }, registered_at=registered_at)
                conn.commit()
                logger.info(f"New user {username} created")
        jwt_token = jwt.encode({
            'id': user_id,
            'username': username,
            'exp' : time.time() + 60 * 60 * 24 * 7, # 7 days
            'rights': BaseUser.get_by_id(BaseServer.get_parmanent_db().cursor(), user_id)['rights']
        }, JWT_SECRET_KEY, algorithm='HS256')
        return COOKIE_NAME, jwt_token, redirect_uri
    @staticmethod
    def logout() -> str:
        logger.info('Logging out')
        return 'auth', '', '/'
    @staticmethod
    def logged_in_user(cookies : dict):
        auth_cookie = cookies.get('auth', None)
        if auth_cookie is None:
            return None
        try:
            auth = jwt.decode(auth_cookie, JWT_SECRET_KEY, algorithms=['HS256'])
            return auth
        except Exception as e:
            logger.info(e)
            return None
    @staticmethod
    def rights_to_int(rights):
        return Permission.rights_to_int(rights)
    @staticmethod
    def int_to_rights(right):
        return Permission.int_to_rights(right)
    @staticmethod
    def grant_rights(grantor_rights : dict, grantee_rights : dict, new_rights : dict) -> int:
        return Permission.grant_rights(grantor_rights, grantee_rights, new_rights)
    @staticmethod
    def get_summary(conn : sqlite3.Cursor, user_id):
        return conn.execute(SQL1_GET_USER_SUMMARY, {'user_id': user_id}).fetchone()

    @staticmethod
    def revoke_rights(revoker_rights : dict, revokee_rights : dict, revoked_rights : dict) -> int:
        if type(revoker_rights) == int:
            revoker_rights = BaseUser.int_to_rights(revoker_rights)
        if type(revokee_rights) == int:
            revokee_rights = BaseUser.int_to_rights(revokee_rights)
        if type(revoked_rights) == int:
            revoked_rights = BaseUser.int_to_rights(revoked_rights)
        prev_right_int = BaseUser.rights_to_int(revokee_rights)
        if not revoker_rights['revoke']:
            return prev_right_int
        # If the grantor has granting right
        
        for right in revoked_rights:
            if revoker_rights[right]:
                revokee_rights[right] = False
            else:
                return prev_right_int
        else:
            return BaseUser.rights_to_int(revokee_rights)
    @staticmethod
    def has_access(rights : int, right : int):
        return Permission.has_access(rights, right)

    @staticmethod
    def create(conn : sqlite3.Cursor, user_id, username, rights : int, registered_at):
        if type(rights) == dict:
            rights = BaseUser.rights_to_int(rights)
            print("Giving rights", rights)
        conn.execute(SQL1_INSERT_USER, {
            'username': username,
            'rights': rights,
            'id': user_id,
            'wiki_registered_at': registered_at
        })
    @staticmethod
    def get_by_id(conn : sqlite3.Cursor, id):
        conn.execute("SELECT * FROM `user` WHERE `id` = ? LIMIT 1", (id,))
        return conn.fetchone()
    @staticmethod
    def get_by_username(conn : sqlite3.Cursor, username):
        conn.execute("SELECT * FROM `user` WHERE `username` = ?", (username,))
        return conn.fetchone()
    @staticmethod
    def update_rights(conn : sqlite3.Cursor, id, rights : int):
        return conn.execute("UPDATE `user` SET `rights` = ? WHERE `id` = ? RETURNING *", (rights, id)).fetchone()
    @staticmethod
    def update_username(conn : sqlite3.Cursor, id, username):
        return conn.execute("UPDATE `user` SET `username` = ? WHERE `id` = ? RETURNING *", (username, id)).fetchone()


class Feedback:
    @staticmethod
    def create(conn : sqlite3.Cursor, user_id : int,  ui_score : int, speed_score : int, why_better : str, feature_request : str):
        if why_better:
            why_better = why_better.strip()
            why_better = re.sub('\n+', '\n', why_better)
        else:
            why_better = ''
        if feature_request:
            feature_request = feature_request.strip()
            feature_request = re.sub('\n+', '\n', feature_request)
        else:
            feature_request = ''
        assert ui_score in range(0, 11), "ui_score must be in range 0-10"
        assert speed_score in range(0, 11), "speed_score must be in range 0-10"
        assert len(why_better) <= 1000, "why_better must be less than 1000 characters"
        assert len(feature_request) <= 1000, "feature_request must be less than 1000 characters"
        if why_better!='' or feature_request!='':
            feedback_note = why_better + '\n\n\n' + feature_request
        else:
            feedback_note = ''
        cur = conn.execute(SQL1_INSERT_FEEDBACK, {
            'user_id': user_id,
            'feedback_ui_score': ui_score,
            'feedback_speed_score': speed_score,
            'feedback_note' : feedback_note,
            'why_better': why_better,
            'feature_request': feature_request
        })
        return cur.fetchone()
    @staticmethod
    def get_all(conn : sqlite3.Cursor):
        data = conn.execute(SQL1_GET_ALL_FEEDBACKS).fetchall()
        return [FeedbackScheme.from_dict(d) for d in data]
        

