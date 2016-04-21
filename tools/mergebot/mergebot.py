"""Mergebot is a script which talks to GitHub and submits all ready pull requests.

Mergebot talks to a specified GitHub project and watches for @mentions for its account.
Acceptable commands are:
  @<mergebot-name> merge
"""
import requests
import time

AUTHORIZED_USERS = ["davor"]
BOT_NAME = 'beam-testing'
GITHUB_API_ROOT = 'https://api.github.com'
GITHUB_ORG = 'apache'
GITHUB_PROJ = 'incubator-beam'
GITHUB_REPO_FMT_URL = GITHUB_API_ROOT + '/repos/{0}/{1}'
GITHUB_REPO_URL = GITHUB_REPO_FMT_URL.format(GITHUB_ORG, GITHUB_PROJ)
CMDS = ['merge']
ISSUES_URL = GITHUB_REPO_URL + '/issues'
COMMENT_FMT_URL = ISSUES_URL + '/{pr_num}/comments'
PULLS_URL = GITHUB_REPO_URL + '/pulls'
SECRET_FILE = '../../github_auth/apache-beam.secret'

def main():
  print('Starting up.')
  # Load github key from filesystem
  key_file = open(SECRET_FILE, 'r')
  bot_key = key_file.read().strip()
  print('Loaded key file.')
  # Loop: Forever, once per minute.
  while True:
    print('Loading pull requests from Github at {}.'.format(PULLS_URL))
    # Load list of pull requests from Github
    r = requests.get(PULLS_URL, auth=(BOT_NAME, bot_key))
    if r.status_code != 200:
      print('Oops, that didn\'t work. Error below, waiting then trying again.')
      print(r.text)
      time.sleep(60)
      continue

    print('Loaded.')
    pr_json = r.json()
    # Loop: Each pull request
    for pr in pr_json:
      pr_num = pr['number']
      print('Looking at PR #{}.'.format(pr_num))
      # Load comments for each pull request
      cmt_url = COMMENT_FMT_URL.format(pr_num=pr_num)
      print('Loading comments.')
      r = requests.get(cmt_url, auth=(BOT_NAME, bot_key))
      if r.status_code != 200:
        print('Oops, that didn\'t work. Error below, waiting then trying again.')
        print(r.text)
        continue

      cmt_json = r.json()
      if len(cmt_json) < 1:
        print('No comments on PR #{}. Moving on.'.format(pr_num))
        continue
      # FUTURE: Loop over comments to make sure PR has been LGTMed
      cmt = cmt_json[-1]
      cmt_body = cmt['body'].encode('ascii', 'ignore')
      # Look for @apache-beam request comments
      # FUTURE: Look for @apache-beam reply comments
      if not cmt_body.startswith('@apache-beam'):
        print('Last comment: {}, not a command. Moving on.'.format(cmt_body))
        continue
      cmd_str = cmt_body.split('@apache-beam ', 1)[1]
      cmd = cmd_str.split(' ')[0]
      if cmd not in CMDS:
        # Post back to PR
        post_error('Command was {}, not a valid command.'.format(cmd), pr_num)
        print('Command was {}, not a valid command.'.format(cmd))
        continue

      if cmd == 'merge':
        if cmt['user']['login'] not in AUTHORIZED_USERS:
          post_error('Unauthorized users cannot merge: {}'.format(cmt['user']['login']))
          print('Unauthorized user {} attempted to merge PR {}.'.format(cmt['user']['login'], pr_num))
          continue
        # Kick off merge workflow
        print('Command was merge, merging.')
        if merge(pr_num):
          post_info('Merge of PR#{} succeeded. Please close this pull request.', pr)
        # Clean up
    time.sleep(60)

def merge(pr):
  # Make temp directory and cd into.
  # Clone repository and configure.
  # Rebase PR onto main.
  if not rebase_success:
    post_error('Rebase was not successful. Please rebase against main and try again.', pr)
    return False

  # Check out target branch to here
  if not checkout_success:
    post_error('Error checking out target branch: master. Please try again.', pr)
    return False

  # Merge
  if not merge_success:
    post_error('Merge was not successful against target branch: master. Please try again.', pr)
    return False

  # mvn clean verify
  if not mvn_success:
    post_error('mvn clean verify against HEAD + PR#{} failed. Not merging.'.format(pr), pr)
    return False

  # git push
  if not push_success:
    post_error('Git push failed. Please try again.', pr)
    return False
  return True

def post_error(content, pr_num):
  post("ERROR: {}".format(content), COMMENT_FMT_URL.format(pr_num=pr_num))

def post(content, endpoint):
  payload = {"body": content}
  r = requests.post(endpoint, data=payload)
  if r.

if __name__ == "__main__":
  main()
