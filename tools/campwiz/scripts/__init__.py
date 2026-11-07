from requests import Session
from dotenv import load_dotenv
import os, dataclasses
load_dotenv()
WIKIPEDIA_ENDPOINT_FORMAT = "https://{lang}.wikipedia.org/w/api.php"
CAMPWIZ_BOT_TOKEN = os.getenv('CAMPWIZ_BOT_ACCESS_TOKEN')
sess = Session()
@dataclasses.dataclass
class Notification:
    username : str
    message_template : str
    data : dict[str, str | int]
    sectiontitletemplate : str
    summary : str
    new : bool = True
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
def _send_message(lang, title, message, summary, csrf=None, sectiontitle='New message from CampWiz Bot'):
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
def notify_users(lang : str, messages : list[Notification]):
    csrf = get_csrf_token(lang)
    for message in messages:
        talk_page = f'User talk:{message.username}'
        message_text = f"""
        {{{{subst:{message.message_template}
        | article   =   {message.data.get('article')}
        | status    =   {message.data.get('status')}
        | judge username    =   {message.data.get('judge')}
        | by        =      {message.data.get('submitter')}
        | submission id     =   {message.data.get('submission id')}
        | campaign name =   {message.data.get('campaign name')}
        | campaign id   =   {message.data.get('campaign id')}
        | given by bot  = yes
        }}}}
        - ~~~~
        """
        section = f"{{{{subst:{message.sectiontitletemplate}|article={message.data.get('article')}|status={message.data.get('status')}}}}}"
        _send_message(
            lang = lang,
            title = talk_page,
            message =message.message_template.format(**message.data), 
            summary = message.summary,
            csrf = csrf,
            sectiontitle = section
        )
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
            _send_message(lang, subscriber,sectiontitle=f'{{{{subst:{LANGUAGE_CONFIGURATIONS[lang]["submission_evaluation_template"]}/title|article={test_article}|status=approved}}}}',
                        message= f'{{{{subst:{LANGUAGE_CONFIGURATIONS[lang]["submission_evaluation_template"]}|article={test_article}|status=approved}}}}', csrf=csrf,summary='Bot: Subscription')
notice = Notification(
    username="CampWiz Bot",
    message_template="CampWiz Notification",
    data = {
        "article" : "Article Name",
        "judge username" : "Judge Name",
        "status" : "approved",
        "note" : "This is a test note",
        "by" : "Nokib Sarkar"
    },
    sectiontitletemplate="CampWiz Notification/title",
    summary="Bot: Subscription"
)
notify_users('test', [notice])