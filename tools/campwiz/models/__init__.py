from ._sql import *
from ._schema import *
from ..._shared._model import *
import dateparser as dp
from ._content import calculate_word
class PointCalculator:
	def __init__(self):
		self.point = None
		
	def step(self, val):
		if self.point is not None:
			if self.point ^ val:
				self.point = 5
		else:
			self.point = val * 10
	def finalize(self):
		return self.point
class Server(BaseServer):
	@staticmethod
	def get_parmanent_db():
		conn = BaseServer.get_parmanent_db()
		# conn.create_aggregate("calculate_point", 1, PointCalculator)
		return conn
def _notify_tg(chat_id : int, text : str):
	with sentry_sdk.start_span(op="notify_tg") as sp:
		url = f'https://api.telegram.org/bot{TG_BOT_AUTH_TOKEN}/sendMessage'
		params = {
			'chat_id': chat_id,
			'text': text,
		}
		sp.set_data("chat_id", chat_id)
		sp.set_data("text", text)
		r = sess.post(url, params=params)
		return r.json()
def notify_fnf_groups(text):
	for chat_id in TG_FNFC_GROUP_CHAT_ID:
		with sentry_sdk.start_span(op="notify_fnf_groups") as sp:
			sp.set_data("chat_id", chat_id)
			sp.set_data("text", text)
			_notify_tg(chat_id, text)
		
def notify_tool_group(text):
	with sentry_sdk.start_span(op="notify_tool_group") as sp:
		sp.set_data("text", text)
		return _notify_tg(TG_GROUP_CHAT_ID, text)
def notify_users(campaign_id : int, campaign_name : str, campaign_language : str, campaign_start_date : str, campaign_end_date : str, campaign_creator : str):
	"""
	This will send a notification to all the users
	"""
	text = f"""
	A new campaign has been created and pending for approval.
	Campaign ID: {campaign_id}
	Campaign Name: {campaign_name}
	Campaign Language: {campaign_language}
	Campaign Start Date: {campaign_start_date}
	Campaign End Date: {campaign_end_date}
	Campaign Creator: {campaign_creator}


	Click here to approve or reject the campaign: https://tools.wikilovesfolklore.org/campwiz/campaign/{campaign_id}/edit
	"""
	with sentry_sdk.start_span(op="notify_users") as sp:
		sp.set_data("text", text)
		return _notify_tg(TG_GROUP_CHAT_ID, text)
def notify_statistics(text):
	with sentry_sdk.start_span(op="notify_statistics") as sp:
		sp.set_data("text", text)
		notify_fnf_groups(text)
class User(BaseUser):
	@staticmethod
	def get_all(conn : sqlite3.Cursor):
		return conn.execute(SQL1_GET_USER_SUMMARY).fetchall()
	@staticmethod
	def _get_username_map(conn : sqlite3.Cursor, usernames : list[str]) -> dict[str, UserScheme]:
		sql = SQL1_GET_USERS_BY_USERNAME_PREFIX + (
			"(" + ",".join(["?"] * len(usernames)) + ")"
		)
		users = conn.execute(sql, list(usernames))
		return dict(map(lambda x: (x['username'], x), users))
	@staticmethod
	def is_admin(rights : int):
		return User.has_access(rights, Permission.CAMPAIGN.value)
	@staticmethod
	def get_central_ids(usernames : list[str], lang : str = 'en') -> dict[str, int]:
		users = {}
		for username in usernames:
			is_ip = IPV_PATTERN.match(username)
			if is_ip:
				users[username] = "0x%s" % username.replace('.', '').replace(':', '')
		usernames = set(usernames) - set(users.keys())
		if len(usernames) > 0:
			params = {
				'action': 'query',
				'list': 'users',
				'ususers': '|'.join(usernames),
				'format': 'json',
				'usprop': 'centralids',
				'uslimit' : 'max'
			}
			res = Server.get(lang=lang, params=params)
			users_dict = res['query']['users']
			for user in users_dict:
				try:
					users[user['name']] = user['centralids']['CentralAuth']
				except:
					users[user['name']] = user['name']
		return users
	@staticmethod
	def auto_create_users(conn : sqlite3.Cursor, usernames : set[str], lang : str = 'en') -> dict[str, UserScheme]:
		logger.info(f"Creating {len(usernames)} users : {','.join(usernames)}")
		params = {
			'action': 'query',
			'list': 'users',
			'ususers': '|'.join(usernames),
			'format': 'json',
			'usprop': 'registration|centralids',
			'uslimit' : 'max'
		}
		res = Server.get(lang=lang, params=params)
		users_dict = res['query']['users']
		users = []
		for user in users_dict:
			users.append({
				'id': user['centralids']['CentralAuth'],
				'username': user['name'],
				'rights': Permission.TASK.value,
				'wiki_registered_at': user['registration']
			})
		conn.executemany(SQL1_CREATE_USER_IF_NOT_EXISTS, users)
		user_map = User._get_username_map(conn, list(usernames))
		BaseServer.log("create", 1, "system", f"Created {len(usernames)} users : {','.join(usernames)}")
		return user_map
	@staticmethod
	def get_username_map_guaranteed(conn : sqlite3.Cursor, usernames : list[str], lang : str = 'en') -> dict[str, UserScheme]:
		try:
			user_map = User._get_username_map(conn, usernames)
			if len(user_map) != len(usernames):
				included = set(user_map.keys())
				excluded = set(usernames) - included
				new_map = User.auto_create_users(conn, excluded, lang=lang)
				user_map = {**user_map, **new_map}
			return user_map
		except Exception as e:
			print(e)
			return {}
	
class Campaign:
	@staticmethod
	def create(conn: sqlite3.Cursor, campaign: CampaignCreate, created_by_id=1) -> int:
		with sentry_sdk.start_span(op="create_campaign") as sp:
			blacklist = ','.join(campaign.blacklist or [])
			rules = '\n'.join(campaign.rules or [])
			jury = campaign.jury or []
			params = {
				'name': campaign.name,
				'language': campaign.language.value,
				'start_at': campaign.start_at,
				'end_at': campaign.end_at,
				'status': CampaignStatus.pending.value,
				'description': campaign.description,
				'rules': rules,
				'blacklist': blacklist,
				'image': campaign.image,
				'created_by_id': created_by_id,
				'maximumSubmissionOfSameArticle': campaign.maximumSubmissionOfSameArticle,
				'allowExpansions': campaign.allowExpansions,
				'minimumTotalBytes': campaign.minimumTotalBytes,
				'minimumTotalWords': campaign.minimumTotalWords,
				'minimumAddedBytes': campaign.minimumAddedBytes,
				'minimumAddedWords': campaign.minimumAddedWords,
				'secretBallot': campaign.secretBallot,
				'allowJuryToParticipate': campaign.allowJuryToParticipate,
				'allowMultipleJudgement': campaign.allowMultipleJudgement,
			}
			sp.set_data("params", params)
			with sp.start_child(op="create_campaign"):
				new_campaign = conn.execute(SQL1_CREATE_CAMPAIGN, params).fetchone()
			lastCampaignId = new_campaign['id']
			sp.set_data("lastCampaignId", lastCampaignId)
			Campaign.add_jury(conn, lastCampaignId, jury, lang=campaign.language.value)
			return new_campaign
	@staticmethod
	def update(conn: sqlite3.Cursor, campaign: CampaignUpdate, existing_campaign : CampaignScheme) -> int:
		with sentry_sdk.start_span(op="update_campaign") as sp:
			blacklist = ','.join(campaign.blacklist or [])
			rules = '\n'.join(campaign.rules or [])
			params = {
				'id' : campaign.id,
				'name': campaign.name,
				'start_at': campaign.start_at,
				'end_at': campaign.end_at,
				'status': campaign.status.value,
				'description': campaign.description,
				'rules': rules,
				'blacklist': blacklist,
				'image': campaign.image,
				'maximumSubmissionOfSameArticle': campaign.maximumSubmissionOfSameArticle,
				'allowExpansions': campaign.allowExpansions,
				'minimumTotalBytes': campaign.minimumTotalBytes,
				'minimumTotalWords': campaign.minimumTotalWords,
				'minimumAddedBytes': campaign.minimumAddedBytes,
				'minimumAddedWords': campaign.minimumAddedWords,
				'secretBallot': campaign.secretBallot,
				'allowJuryToParticipate': campaign.allowJuryToParticipate,
				'allowMultipleJudgement': campaign.allowMultipleJudgement,
			}
			sp.set_data("params", params)
			jury = campaign.jury or []
			updated_jury = set(map(str, jury))
			existing_jury = Campaign.get_jury(conn, campaign.id, allowed=True)
			existing_jury_usernames = {u['username'] for u in existing_jury}
			removed_jury = existing_jury_usernames - updated_jury
			new_jury = updated_jury - existing_jury_usernames
			if removed_jury:
				Campaign.remove_jury(conn, campaign.id, removed_jury)
			if new_jury:
				Campaign.add_jury(conn, campaign.id, new_jury, lang=existing_campaign['language'])
				
			sql = SQL1_UPDATE_CAMPAIGN_FORMAT.format(updates=", ".join([f"{k} = :{k}" for k in params.keys()]), id=campaign.id)
			up = conn.execute(sql, params)
			updated_campaign = up.fetchone()
			Campaign.update_status(conn, campaign.id)
		return updated_campaign
	@staticmethod
	def _update_status(conn : sqlite3.Cursor, campaign_id : str, status : CampaignStatus, user_id : int = None):
		params = {
			'id': campaign_id,
			'status': status.value,
			'approved_at': datetime.utcnow().isoformat(),
			'approved_by': user_id,

		}
		cur = conn.execute(SQL1_UPDATE_CAMPAIGN_STATUS, params)
		updated_campaign = cur.fetchone()
		return updated_campaign
	@staticmethod
	def get_results(conn : sqlite3.Cursor, campaign_id : str, exclude_submissions : bool = False):
		statistics = None
		if not exclude_submissions:
			results = conn.execute(SQL1_GET_RESULTS_BY_CAMPAIGN_ID, {'campaign_id': campaign_id}).fetchall()
			submissions = [CampaignResultScheme(**r) for r in results]
			statistics = CampaignStatistics(campaign_id, submissions=submissions)
		else:
			submissions = []
			campaign = Campaign.get_by_id(conn, campaign_id)
			statistics = CampaignStatistics(campaign_id, submissions=submissions)
			statistics.total_submissions = campaign['total_submissions']
			statistics.total_points = campaign['total_points']
			statistics.total_newly_created = campaign['total_newly_created']
			statistics.total_expanded = statistics.total_submissions - statistics.total_newly_created
		return statistics
	@staticmethod
	def get_submission_timeline(conn : sqlite3.Cursor, group_by : str = 'language', campaign_id : str = None, ):
		timeline = []
		if group_by == 'language':
			timeline = conn.execute(SQL1_GET_SUBMISSION_TIMELINE_BY_LANGUAGE).fetchall()
		elif group_by == 'user' and campaign_id is not None:
			timeline = conn.execute(SQL1_GET_SUBMISSION_TIMELINE_BY_SUBMITTED_BY_ID, {'campaign_id': campaign_id}).fetchall()
		timeline = list(map(lambda x: Timeline(**x), timeline))
		return timeline
	
	@staticmethod
	def get_submission_timeline_v2(conn : sqlite3.Cursor, group_by : str = 'language', campaign_id : str = None, accumulated : bool = True, year : int | None = None):
		timeline = []
		if group_by == 'language':
			timeline = conn.execute(SQL1_GET_SUBMISSION_TIMELINE_BY_LANGUAGE).fetchall()
			if year:
				timeline = list(filter(lambda x: dp.parse(x['date']).year == year, timeline))
			campaign_ids = set(map(lambda x: x['color'].split('|')[0], timeline))
			id_placeholder = ','.join(map(lambda x: f"'{x}'", campaign_ids))
			campaigns = conn.execute(SQL1_GET_ALL_CAMPAIGN_BY_IDS_FORMAT.format(id_placeholder=id_placeholder)).fetchall()
			grand_total = StatisticsV2()
			campaign_dict = {}
			for c in campaigns:
				campaign = CampaignStatisticsScheme(
					id = c['id'],
					name = f"[{c['language']}] {c['name']}",
					language= Language(c['language']),
					status = c['status'],
					start_at = c['start_at'],
					end_at = c['end_at'],
					total_submissions = c['total_submissions'],
					total_points = c['total_points'],
					total_newly_created = c['total_newly_created'],
					total_expanded = c['total_submissions'] - c['total_newly_created'],
					color = get_random_hex_color(),
				)
				grand_total.total_submissions += campaign.total_submissions
				grand_total.total_points += campaign.total_points
				grand_total.total_newly_created += campaign.total_newly_created
				grand_total.total_expanded += campaign.total_expanded
				campaign_dict[str(c['id'])] = campaign
			dates = {}
			cum_dict = {}
			for t in timeline:
				d : str = (int(dp.parse(t['date']).timestamp() * 1000))
				if d not in dates:
					dates[d] = {'date' : d}
				campaign_id = t['color'].split('|')[0]
				submission_count = t['count']
				if accumulated:
					if campaign_id not in cum_dict:
						cum_dict[campaign_id] = submission_count
					else:
						cum_dict[campaign_id] += submission_count
					dates[d][campaign_id] = cum_dict[campaign_id]
					for k in campaign_dict:
						if k != campaign_id:
							dates[d][k] = cum_dict.get(k, 0)

				else:
					dates[d][campaign_id] = submission_count
			grand_total.entities = campaign_dict
			grand_total.timeline = list(dates.values())
			return grand_total

		elif group_by == 'user' and campaign_id is not None:
			timeline = conn.execute(SQL1_GET_SUBMISSION_TIMELINE_BY_SUBMITTED_BY_ID, {'campaign_id': campaign_id}).fetchall()
			c = Campaign.get_by_id(conn, campaign_id)

			grand_total = StatisticsV2(
				id=c['id'],
				total_submissions = c['total_submissions'],
				total_points = c['total_points'],
				total_newly_created = c['total_newly_created'],
				total_expanded = c['total_submissions'] - c['total_newly_created'],
			)
			user_dict : dict[str, UserStatistics] = {}
			dates = {}
			cum_dict = {}
			for t in timeline:
				d : str = (int(dp.parse(t['date']).timestamp() * 1000))
				if d not in dates:
					dates[d] = {'date' : d}
				user_id = t['color']
				submission_count = t['count']
				if accumulated:
					if user_id not in cum_dict:
						cum_dict[user_id] = submission_count
					else:
						cum_dict[user_id] += submission_count
					dates[d][user_id] = cum_dict[user_id]
					for k in user_dict:
						if k != user_id:
							dates[d][k] = cum_dict.get(k, 0)
				else:
					dates[d][user_id] = submission_count  
				
				if user_id not in user_dict:
					user_dict[user_id] = UserStatistics(
						id = user_id,
						name = user_id,
						color=get_random_hex_color(),
						total_submissions=0,
						total_newly_created=0,
						total_expanded=0,
						total_points=0,
					)
				user_dict[user_id].total_submissions += submission_count
				user_dict[user_id].total_points += t['points']
				user_dict[user_id].total_newly_created += t['newly_created']
				user_dict[user_id].total_expanded += submission_count - t['newly_created']
			grand_total.entities = user_dict
			grand_total.timeline = list(dates.values())
			return grand_total
			


	@staticmethod
	def get_all(conn : sqlite3.Cursor, language : Language=None, status : list[CampaignStatus]=None, limit : int=50, offset : int= 0):
		params = {
			'limit': limit,
			'offset': offset,
			'language': language and language.value,
		}
		sql = SQL1_GET_ALL_CAMPAIGN
		if status:
			status_placeholder = ','.join(map(lambda x: f"'{x.value}'", status))
			if language is not None:
				sql = SQL1_GET_ALL_CAMPAIGN_BY_STATUS_AND_LANGUAGE_FORMAT
			else:
				sql = SQL1_GET_ALL_CAMPAIGN_BY_STATUS_FORMAT
			sql = sql.format(status_placeholder=status_placeholder)
		elif language is not None:
			sql = SQL1_GET_ALL_CAMPAIGN_BY_LANGUAGE
		return conn.execute(sql, params).fetchall()
	@staticmethod
	def add_jury(conn : sqlite3.Cursor, campaign_id : str, jury : list[str], lang : str='en'):
		users = User.get_username_map_guaranteed(conn, jury, lang=lang)
		users = map(lambda v: (v['id'], v['username'], campaign_id), users.values())
		conn.executemany(SQL1_ADD_JURY_TO_CAMPAIGN, users)
		BaseServer.log("create", 1, "system", f"Added {len(jury)} jury to campaign {campaign_id} : {','.join(jury)}")
	@staticmethod
	def remove_jury(conn : sqlite3.Cursor, campaign_id : str, jury : list[str]):
		users = User._get_username_map(conn, jury)
		users = map(lambda v: (v['id'], campaign_id), users.values())
		conn.executemany(SQL1_REMOVE_JURY_FROM_CAMPAIGN, users)
		BaseServer.log("delete", 1, "system", f"Removed {len(jury)} jury from campaign {campaign_id} : {','.join(jury)}")
	@staticmethod
	def get_jury(conn : sqlite3.Cursor, campaign_id : str, allowed : bool=True):
		result = []
		if allowed is None:
			result = conn.execute(SQL1_GET_JURY_BY_CAMPAIGN_ID, {'campaign_id': campaign_id}).fetchall()
		else:
			result = conn.execute(SQL1_GET_JURY_BY_ALLOWED, {'campaign_id': campaign_id, 'allowed' : allowed}).fetchall()
		return result
	@staticmethod
	def _get_by_id(conn : sqlite3.Cursor, id : str):
		return conn.execute(SQL1_GET_CAMPAIGN_BY_ID, {'id': id}).fetchone()
	@staticmethod
	def get_by_ids(conn : sqlite3.Cursor, ids : list[str]):
		id_placeholder = ','.join(map(lambda x: f"?", ids))
		sql = SQL1_GET_ALL_CAMPAIGN_BY_IDS_FORMAT.format(id_placeholder=id_placeholder)
		return conn.execute(sql, ids).fetchall()
	@staticmethod
	def get_by_id(conn : sqlite3.Cursor, id : str):
		return Campaign.update_status(conn, id)
	
	@staticmethod
	def update_status(conn : sqlite3.Cursor, id : str, check_all_judged = False) -> CampaignScheme:
		campaign = Campaign._get_by_id(conn, id)
		if campaign is None:
			raise Exception("Campaign not found")
		now = datetime.utcnow()
		status = campaign['status']
		start_date = dp.parse(campaign['start_at'], region='UTC').replace(hour=0, minute=0, second=0)
		end_date = dp.parse(campaign['end_at'], region='UTC').replace(hour=23, minute=59, second=59)
		if status == CampaignStatus.scheduled.value and now >= start_date:
			logger.info("Scheduled to running")
			BaseServer.log("info", 1, "system", f"Campaign {id} scheduled to running")
			status = CampaignStatus.running.value
		if now > end_date:
			if status == CampaignStatus.running.value: 
				logger.info("Running to evaluating")
				BaseServer.log("info", 1, "system", f"Campaign {id} running to evaluating")
				status = CampaignStatus.evaluating.value
			elif status == CampaignStatus.evaluating.value:
				all_judged = conn.execute(SQL1_UPDATE_CAMPAIGN_STATUS_TO_ENDED, {'campaign_id': id}).fetchone()
				# check if 6 months passed
				evaluation_expiry_date = start_date + timedelta(days=6 * 30)
				evaluation_expired = now > evaluation_expiry_date
				if evaluation_expired or all_judged['unjudged_submissions'] == 0:
					logger.info("Evaluating to ended")
					BaseServer.log("info", 1, "system", f"Campaign {id} evaluating to ended")
					status = CampaignStatus.ended.value
		return conn.execute(SQL1_UPDATE_CAMPAIGN_STATUS, {'id': id, 'status': status}).fetchone()
	


class Submission:
	@staticmethod
	def _fetch_first_revision(lang : str, pageid : int) -> dict[str, str]:
		params = {
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"pageids": pageid,
			"rvprop": "timestamp|user|size|ids|userid",
			"rvlimit": "1",
			"rvdir": "newer",
		}
		info = Server.get(lang=lang, params=params)
		assert 'query' in info, "query not found"
		assert 'pages' in info['query'], 'No pages found'
	
		assert len(info['query']['pages']) == 1, "Must be a single "
		assert pageid in info['query']['pages'], "Page does not match"
		page = info['query']['pages'][pageid]
		assert 'revisions' in page, "No revision found"
		revision = page['revisions'][0]
		return {
			'oldid' : revision['revid'],
			'title' : page['title'],
			'username' : revision['user'],
			'timestamp' : revision['timestamp'],
			'size' : revision['size'],
		}
	@staticmethod
	def _fetch_current_info(lang : str, title : str) -> dict[str, str]:
		"""
		Fetch current information of the article from the API
		"""
		params = {
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"titles": Server.get_page_with_prefix(lang, title),
			"rvprop": "timestamp|tags|user|size|ids|content|userid",
			"rvlimit": "1",
			"indexpageids" : 1,
			'redirects' : 1
		}
		info = Server.get(lang=lang, params=params)
		assert 'query' in info, "query not found"
		assert 'pages' in info['query'], 'No pages found'
	
		assert len(info['query']['pages']) == 1 and len(info['query']['pageids']) == 1, "Must be a single "
		pageid = info['query']['pageids'][0]
		page = info['query']['pages'][pageid]
		if 'missing' in page:
			# return {
			#     'pageid' : pageid,
			#     'title' : title,
			#     'ns' : 0,
			#     'content' : '',
			#     'bytes' : 0,
			#     'words' : 0,
			#     'oldid' : 0,
			# }
			raise Exception("campaign.submission.error.pageNotFound")
		assert 'revisions' in page, page
		revision = page['revisions'][0]
		assert '*' in revision, 'No content'
		stat = {
			'pageid' : pageid,
			'ns' : page['ns'],
			'title' : page['title'],
			'content' : revision['*'],
			'bytes' : revision['size'],
			'words' : calculate_word(revision['*']),
			'oldid' : revision['revid'],
		}
		return stat
	@staticmethod
	def fetch_stats(lang :str, title : str) -> tuple[list[str], dict[str, str | int]]:
		errors = []
		current_info = Submission._fetch_current_info(lang, title)
		pageid = current_info['pageid']
		title = current_info['title']
		first_revision_info = Submission._fetch_first_revision(lang, pageid)
		user_ids = User.get_central_ids([first_revision_info['username']], lang=lang)
		created_by_id = user_ids[first_revision_info['username']]
		errors = []
		stats = {
			'title' : title,
			'pageid' : pageid,
			'oldid' : current_info['oldid'],
			'words' : current_info['words'],
			'bytes' : current_info['bytes'],
			'created_at' : first_revision_info['timestamp'],
			'created_by_username' : first_revision_info['username'],
			'created_by_id' : created_by_id,
			'added_words' : 0,
			'added_bytes' : 0,
		}
		return errors, stats
	@staticmethod
	def submit(conn : sqlite3.Cursor, draft : DraftSubmissionScheme, added_at = None) -> SubmissionScheme:
		params = {
			'campaign_id': draft['campaign_id'],
			'pageid': draft['pageid'],
			'oldid': draft['oldid'],
			'title': draft['title'],
			'created_at': draft['created_at'],
			'created_by_id': draft['created_by_id'],
			'created_by_username': draft['created_by_username'],
			'submitted_by_id': draft['submitted_by_id'],
			'submitted_by_username': draft['submitted_by_username'],
			'total_words': draft['total_words'],
			'total_bytes': draft['total_bytes'],
			'added_words': draft['added_words'],
			'added_bytes': draft['added_bytes'],
			'target_wiki': draft['target_wiki'],
			'newly_created' : draft['newly_created'],
		}
		sql = SQL1_CREATE_SUBMISSION
		if added_at is not None:
			params['submitted_at'] = added_at
			sql = SQL1_CREATE_LATE_SUBMISSION
			print("Submitting late submission")
		cur = conn.execute(sql, params)
		new_submission = cur.fetchone()
		return SubmissionScheme(**new_submission)
	@staticmethod
	def create_draft(conn : sqlite3.Cursor, draft : DraftSubmissionScheme) -> DraftSubmissionScheme:
		params = {
			'campaign_id': draft.campaign_id,
			'pageid': draft.pageid,
			'oldid': draft.oldid,
			'title': draft.title,
			'created_at': draft.created_at,
			'created_by_id': draft.created_by_id,
			'created_by_username': draft.created_by_username,
			'submitted_by_id': draft.submitted_by_id,
			'submitted_by_username': draft.submitted_by_username,
			'total_words': draft.total_words,
			'total_bytes': draft.total_bytes,
			'added_words': draft.added_words,
			'added_bytes': draft.added_bytes,
			'target_wiki': draft.target_wiki,
			'newly_created': draft.submitted_by_username == draft.created_by_username,
			'calculated': draft.calculated or False,
			'passed': draft.passed or False,
		}
		cur = conn.execute(SQL1_CREATE_DRAFT, params)
		new_draft = cur.fetchone()
		return DraftSubmissionScheme(**new_draft)
	@staticmethod
	def get_draft_by_id(conn : sqlite3.Cursor, id : int) -> DraftSubmissionScheme:
		return conn.execute(SQL1_GET_DRAFT_BY_ID, {'id': id}).fetchone()
	@staticmethod
	def update_draft_flags(conn : sqlite3.Cursor, draft_id, calculated : bool, passed : bool, submitted : bool) -> DraftSubmissionScheme:
		params = {
			'id': draft_id,
			'calculated': calculated,
			'passed': passed,
			'submitted': submitted,
		}
		cur = conn.execute(SQL1_UPDATE_DRAFT, params)
		updated_draft = cur.fetchone()
		return DraftSubmissionScheme(**updated_draft)
	@staticmethod
	def delete(conn : sqlite3.Cursor, id : str):
		conn.execute(SQL1_DELETE_SUBMISSION_BY_ID, {'id': id})
	@staticmethod
	def get_next_judgable_id(conn : sqlite3.Cursor, campaign_id : str, current_submission_id : str, judge_id : int):
		"""
		This function would fetch the next submission of this campaign that was not yet judged by the current user
		"""
		params = {
			  'campaign_id': campaign_id,
			'current_submission_id': current_submission_id,
			'judge_id': judge_id,
			}
		sql = """
		 SELECT
			id AS `next_submission_id`
		FROM
			submission
		WHERE
			campaign_id = :campaign_id
		AND
			id > :current_submission_id
		AND
			id NOT IN 
			(
				SELECT
					submission_id
				FROM
					jury_vote
				WHERE
					jury_id = :judge_id
				AND
					campaign_id = :campaign_id
			)
		ORDER BY `id` ASC
		LIMIT 1
		"""
		next_submission = conn.execute(sql, params).fetchone()
		if next_submission is not None:
			return next_submission['next_submission_id']


	@staticmethod
	def get_all_by_campaign_id(conn : sqlite3.Cursor, campaign_id, judgable : bool=None, exclude_judged_user_id : int = None, only_judged_by : int = None):
		params = {'campaign_id': campaign_id}
		sql = SQL1_SELECT_SUBMISSIONS
		if only_judged_by is not None:
			sql = SQL1_SELECT_SUBMISSIONS_JUDGED_BY_USER_ID
			params['jury_id'] = only_judged_by
		if exclude_judged_user_id is not None:
			params['exclude_judged_user_id'] = exclude_judged_user_id 
			sql = SQL1_SELECT_SUBMISSIONS_EXCLUDING_USER_ID
		results = conn.execute(sql, params).fetchall()
		return results
	@staticmethod
	def get_by_id(conn : sqlite3.Cursor, id : str) -> SubmissionScheme:
		d = conn.execute(SQL1_GET_SUBMISSION_BY_ID, {'id': id}).fetchone()
		logger.info(dict(d))
		return d
class Judgement:
	@staticmethod
	def next_unjudged_submission(conn : sqlite3.Cursor, campaign_id : str, judge_id : int):
		params = {
			'campaign_id': campaign_id,
			'jury_id': judge_id,
		}
		next_submission = conn.execute(SQL1_NEXT_UNJUDGED_SUBMISSION, params).fetchone()
		if next_submission is not None:
			return next_submission['id']
		return 0
	@staticmethod
	def add(conn : sqlite3.Cursor, submission_id : int, jury_id : int, vote : int, campaign_id : int, note : str = None):
		params = {
			'submission_id': submission_id,
			'jury_id': jury_id,
			'vote': vote,
			'campaign_id' : campaign_id,
			'note' : note,
		}
		cur = conn.execute(SQL1_ADD_JUDGEMENT, params)
		new_judgement = cur.fetchone()
		return new_judgement
	@staticmethod
	def _get_judgements(conn  : sqlite3.Cursor, submission_id : int, judge_id : int = None) -> list[JudgementScheme]:
		if judge_id is not None:
			sql = SQL1_GET_JUDGEMENTS_BY_SUBMISSION_ID_AND_JUDGE_ID
		else:
			sql = SQL1_GET_JUDGEMENTS_BY_SUBMISSION_ID
		return conn.execute(sql, {'submission_id': submission_id, 'judge_id' : judge_id}).fetchall()
	@staticmethod
	def _get_all_jury(conn : sqlite3.Cursor, submission_id : int) -> list[UserScheme]:
		return conn.execute(SQL1_GET_JURY_BY_SUBMISSION_ID, {'submission_id': submission_id}).fetchall()
	@staticmethod
	def calculate_points(conn : sqlite3.Cursor, submission_id : int):
		"""
		Calculate and update the votes of a submission
		"""
		all_judgements = Judgement._get_judgements(conn, submission_id)
		# all_jury = Judgement._get_all_jury(conn, submission_id)
		total_votes = 0
		negative_votes = 0
		positive_votes = 0
		points = 0
		for judgement in all_judgements:
			if judgement['vote'] == 0:
				negative_votes += 1
			elif judgement['vote'] == 1:
				positive_votes += 1
			total_votes += judgement['vote']
		if total_votes > 0:
			if negative_votes == 0 and positive_votes == total_votes:
				points = 10
			elif positive_votes == 0 and negative_votes == total_votes:
				points = 0
			else:
				points = 5

		params = {
			'id': submission_id,
			'total_votes': total_votes,
			'negative_votes': negative_votes,
			'positive_votes': positive_votes,
			'points' : points,
		}
		cur = conn.execute(SQL1_UPDATE_SUBMISSION_POINTS, params)
		updated_submission = cur.fetchone()
		return SubmissionScheme(**updated_submission)
	@staticmethod
	def verify_judge(conn: sqlite3.Cursor, campaign_id : str, user_id : int):
		v = conn.execute(SQL1_VERIFY_JUDGE, {'campaign_id': campaign_id, 'user_id': user_id}).fetchone()
		return bool(v and v['allowed'])
	
class Notification:
	@staticmethod
	def get_pending_notifications(conn : sqlite3.Cursor, last_update : str) -> Notifications:
		results : Notifications = {}
		new_submissions = Notification.get_new_submissions(conn, last_update)
		for submission in new_submissions:
			campaign_id = submission['campaign_id']
			if campaign_id not in results:
				results[campaign_id] = NotificationCampaignUpdate(
					language=submission['target_wiki'],
					campaign_id=campaign_id,
					new_submissions=[], # List of new submissions would be distributed to all the juries
					new_evaluations={}, # new evaluations would be distributed to the respective submitters
					new_article_talk_page_updates=[], # A template would be added to the talk page of the new articles
					name=None,
					tracker_template=None,
				)
			results[campaign_id].new_submissions.append(NotificationNewSubmission(**submission))
			results[campaign_id].new_article_talk_page_updates.append(submission['title'])
		


		new_evaluations = Notification.get_new_evaluations(conn, last_update)
		for evaluation in new_evaluations:
			campaign_id = evaluation['campaign_id']
			if campaign_id not in results:
				results[campaign_id] = NotificationCampaignUpdate(
					language=evaluation['target_wiki'],
					campaign_id=campaign_id,
					new_submissions=[], # List of new submissions would be distributed to all the juries
					new_evaluations={}, # new evaluations would be distributed to the respective submitters
					new_article_talk_page_updates=[], # A template would be added to the talk page of the new articles
					name=None,
					tracker_template=None,
				)
			if evaluation['submitted_by_username'] not in results[campaign_id].new_evaluations:
				results[campaign_id].new_evaluations[evaluation['submitted_by_username']] = []
			results[campaign_id].new_evaluations[evaluation['submitted_by_username']].append(
				NotificationNewEvaluation(
					jury_username=evaluation['jury_username'],
					title=evaluation['title'],
					vote=evaluation['vote'],
					note=evaluation['note'],
					target_wiki=evaluation['target_wiki'],
					campaign_id=evaluation['campaign_id'],
				)
			)
		campaign_ids = list(results.keys())
		collected_campaigns = Campaign.get_by_ids(conn, campaign_ids)
		for campaign in collected_campaigns:
			
			id : str = campaign['id']
			results[id].name = campaign['name']
			results[id].tracker_template = 'tracker_template' in campaign and campaign['tracker_template']
		return results
	@staticmethod
	def get_new_submissions(conn : sqlite3.Cursor, last_update : str):
		new_submissions = list(map(dict, conn.execute(SQL1_GET_NEW_SUBMISSIONS, {
			"last_update" : last_update
		}).fetchall()))
		return new_submissions
	@staticmethod
	def get_new_evaluations(conn : sqlite3.Cursor, last_update : str):
		new_evaluations = list(map(dict, conn.execute(SQL1_GET_NEW_EVALUATION, {
				"last_update" : last_update
			}).fetchall()))
		return new_evaluations
	
