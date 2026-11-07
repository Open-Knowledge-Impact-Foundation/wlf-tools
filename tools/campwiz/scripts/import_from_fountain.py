BASE_URL =  'https://tools.wikilovesfolklore.org/api/campwiz'
from dotenv import load_dotenv
import os, json, time
load_dotenv()
AUTH_TOKEN = os.getenv('AUTH')
print(f"Using AUTH_TOKEN: {AUTH_TOKEN}")
from requests import Session

sess = Session()
sess.cookies.update({
    'auth': f'{AUTH_TOKEN}'
})

def get_checked_submissions(code : str):
    fp_name = f'./fountain_data/{code}-submitted.json'
    try:
        with open(fp_name, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        print(f"File not found: {fp_name}")
        return set()
def save_checked_submissions(code : str, submissions : set):
    """
    Saves the list of checked submissions to a file.
    """
    fp_name = f'./fountain_data/{code}-submitted.json'
    data = list(submissions)
    with open(fp_name, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved checked submissions to {fp_name}")
def create_draft(campaign_id, title, submitter):
    """
    Creates a draft submission for the specified campaign.
    """
    url = f'{BASE_URL}/submission/draft/late'
    payload = {
        "campaign_id": f'{campaign_id}',
        "title": title,
        "submitted_by_username": submitter
    }
    response = sess.post(url, json=payload)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to create draft: {response.status_code} - {response.text}")
        return None

def check_draft(draft_id) -> bool:
    """
    Checks the status of a draft submission.
    """
    while True:
        url = f'{BASE_URL}/submission/draft/{draft_id}'
        response = sess.get(url)
        if response.status_code == 200:
            params = response.json()
            data = params.get('data', {})
            if data['calculated']:
                return data['passed']
        time.sleep(1)  # Wait for 3 seconds before checking again
def submit_draft(draft_id, added_at : str):
    """
    Submits a draft for review.
    """
    url = f'{BASE_URL}/submission/late'
    payload = {
        "draft_id": draft_id,
        "added_at": added_at
    }
    response = sess.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to submit draft: {response.status_code} - {response.text}")
        return None

def _get_fountain_data(code : str):
    """
    Fetches fountain data from the API using the provided code.
    """
    data = None
    try:
        with open(f'./fountain_data/{code}.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Fountain data for code {code} not found locally. Fetching from API...")
        url = f'https://fountain.toolforge.org/api/editathons/{code}'
        response = sess.get(url)
        if response.status_code == 200:
            data = response.json()
            # Save the fetched data locally for future use
            with open(f'./fountain_data/{code}.json', 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            raise Exception(f"Failed to fetch fountain data: {response.status_code} - {response.text}")
    return data
def _get_submission_data(code):
    """
    Fetches submission data for a specific campaign from the API.
    """
    data = _get_fountain_data(code)
    if not data:
        raise ValueError(f"No data found for code {code}")
    articles = data.get('articles', [])
    submissions = []
    for article in articles:
        title = article.get('name')
        if not title:

            continue
        submitter = article.get('user')
        if not submitter:
            continue
        date_added = article.get('dateAdded')
        if not date_added:
            continue
        submissions.append({
            'title': title,
            'submitter': submitter,
            'date_added': date_added,
        })
    return submissions


    
def import_from_fountain():
    code_mapping = {
       input('Enter the Fountain code for the campaign: '): input('Enter the Campaign ID: ')
    }
    print("Starting import from Fountain...")
    for code, campaign_id in code_mapping.items():
        already_submitted = get_checked_submissions(code)
        submissions = _get_submission_data(code)
        for submission in submissions:
            try:
                if submission['title'] in already_submitted:
                    print(f"Skipping already submitted: {submission['title']}")
                    continue
                print(f"Title: {submission['title']}, Submitter: {submission['submitter']}, Date Added: {submission['date_added']}")
                draft = create_draft(campaign_id, submission['title'], submission['submitter'])
                if check_draft(draft['id']):
                    print(f"Draft created successfully: {draft['id']}")
                    if submit_draft(draft['id'], submission['date_added']):
                        print(f"Draft submitted successfully: {draft['id']}")
                    else:
                        print(f"Failed to submit draft: {draft['id']}")
                already_submitted.add(submission['title'])
                save_checked_submissions(code, already_submitted)
                time.sleep(2)
            except Exception as e:
                print(f"Error processing submission {submission['title']}: {e}")
            # break

if __name__ == "__main__":
    import_from_fountain()
else:
    # This script is intended to be run as a standalone tool
    # It should not be imported as a module
    raise ImportError("This script is intended to be run as a standalone tool, not imported as a module.")