from requests import Session
from dotenv import load_dotenv
import os, time
from mtei import MeteiToBengali
load_dotenv()
WIKIPEDIA_ENDPOINT_FORMAT = "https://{lang}.wikipedia.org/w/api.php"
CAMPWIZ_BOT_TOKEN = os.getenv('CAMPWIZ_BOT_ACCESS_TOKEN')
sess = Session()
class BaseServer:
    @staticmethod
    def get(*lw, lang='en', **kw) -> dict:
        url = WIKIPEDIA_ENDPOINT_FORMAT.format(lang=lang)
        return sess.get(url, *lw, **kw).json()
    @staticmethod
    def post(*lw, lang='en', **kw) -> dict:
        url = WIKIPEDIA_ENDPOINT_FORMAT.format(lang=lang)
        return sess.post(url, *lw, **kw).json()
sess.headers.update({
    'User-Agent': 'CampWiz Bot/1.0',
    'Accept': 'application/json',
    'Authorization': f'Bearer {CAMPWIZ_BOT_TOKEN}'
})
LANGUAGE_CONFIGURATIONS = {
    'mni' : {
        'subscription_category' : 'Category:CampWiz Subscriptions',
        'subscription_template' : 'User:CampWiz Bot/WLF/Statistics',
        'submission_evaluation_template' : 'User:CampWiz Bot/WLF/submission evaluated',
        'campaign_template' : 'WLF2024',
        'new_submission_template' : 'User:CampWiz Bot/WLF/Statistics/new submission',
        'campaign_non_evaluated_category' : 'Category:WLF2024 non evaluated submissions',
        'campaign_evaluated_category' : 'Category:WLF2024 evaluated submissions',
        'campaign_submissions_category' : 'Category:WLF2024 submissions',
    }
}
def query_with_continue(lang, params, method='get'):
    while True:
        response = BaseServer.get(lang=lang, params=params)
        yield response
        if 'continue' in response:
            params.update(response['continue'])
        else:
            break
def get_csrf_token(lang):
    time.sleep(2)
    params = {
        'action': 'query',
        'meta': 'tokens',
        'type': 'csrf',
        'format': 'json'
    }
    response = BaseServer.get(lang=lang, params=params)
    assert 'error' not in response, response['error']
    assert 'query' in response, response
    assert 'tokens' in response['query'], response
    assert 'csrftoken' in response['query']['tokens'], response
    return response['query']['tokens']['csrftoken']
def send_message(lang, title, message, summary, csrf=None, sectiontitle='New message from CampWiz Bot'):
    if csrf is None:
        csrf = get_csrf_token(lang)
    params = {
        'action': 'edit',
        'title': title,
        'summary': summary,
        'text': message,
        'token': csrf,
        'sectiontitle': sectiontitle,
        'section': 'new',
        'format': 'json',
        'notminor': '1',
        'bot': '1',
        # 'captchaid' : '1276565941',
        # 'captchaword' : 'antsoprah'
    }
    response = BaseServer.post(lang=lang, data=params)
    print(response)
def edit_page(lang, title, text, summary, csrf=None, recreate=True):
    if csrf is None:
        csrf = get_csrf_token(lang)
    params = {
        'action': 'edit',
        'title': title,
        'summary': summary,
        'text': text,
        'token': csrf,
        'format': 'json',
        'notminor': '1',
        'bot': '1',
        'recreate': recreate
    }
    response = BaseServer.post(lang=lang, data=params)
    print(response)
def get_all_subscriptions(lang):
    subscription_category = LANGUAGE_CONFIGURATIONS[lang]['subscription_category']
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'format': 'json',
        'cmtitle': subscription_category,
        'cmlimit': 'max',
        'cmprop': 'title'
    }

    response_iterator = query_with_continue(lang, params)
    csrf = get_csrf_token(lang)
    for response in response_iterator:
        subscribers = response['query']['categorymembers']
        subscriber_pages = [subscriber['title'] for subscriber in subscribers]
        for subscriber in subscriber_pages:
            test_article = 'WLF2024'
            send_message(lang, subscriber,sectiontitle=f'{{{{subst:{LANGUAGE_CONFIGURATIONS[lang]["submission_evaluation_template"]}/title|article={test_article}|status=approved}}}}',
                        message= f'{{{{subst:{LANGUAGE_CONFIGURATIONS[lang]["submission_evaluation_template"]}|article={test_article}|status=approved}}}}', csrf=csrf,summary='Bot: Subscription')
def get_recentchanges():
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "generator": "recentchanges",
        "formatversion": "2",
        "rvprop": "ids|timestamp|flags|comment|user|content",
        "rvslots": "main",
        "grcdir": "newer",
        "grcexcludeuser": "CampWiz Bot",
        "grcshow": "!bot",
        "grctype": "edit|new",
        "grctoponly": 1
    }
    response_iterator = query_with_continue('mni', params)
    for response in response_iterator:
        for page in response['query']['pages']:
            page_title = page['title']
            page_id = page['pageid']
            page_revisions = page['revisions']
            if len(page_revisions) == 0:
                continue
            revision = page_revisions[0]
            revision_id = revision['revid']
            revision_timestamp = revision['timestamp']
            revision_comment = revision['comment']
            revision_user = revision['user']
            revision_content = revision['slots']['main']['content']


            # Transliteration
            transliterated_page_title = MeteiToBengali.transliterate(page_title)
            transliterated_revision_comment = MeteiToBengali.transliterate(revision_comment)
            transliterated_revision_content = MeteiToBengali.transliterate(revision_content)
            
            # Comment
            comment = f'New edit by {revision_user} on [{page_title}]({page_id}) at {revision_timestamp} with comment: {transliterated_revision_comment}'
            edit_page('mni', f"User:CampWiz Bot/Test/{transliterated_page_title}", transliterated_revision_content, comment, recreate=False)
            
            break
