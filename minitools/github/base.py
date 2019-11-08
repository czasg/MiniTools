try:
    from github import Github
except ModuleNotFoundError:
    from minitools import throw_moduleNotFoundError

    throw_moduleNotFoundError('pip install selenium>=3.141.0')


class GithubBase:

    def __init__(self, *account):
        self.github = Github(*account)
        self.init_github()

    def init_github(self):
        self.update_all_repositories()

    def update_all_repositories(self):
        self.all_repositories = self.github.get_user().get_repos()
