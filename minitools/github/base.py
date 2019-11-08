from github import Github  # pip install PyGithub>=1.44.1


class GithubBase:

    def __init__(self, *account):
        self.github = Github(*account)
        self.init_github()

    def init_github(self):
        self.update_all_repositories()

    def update_all_repositories(self):
        self.all_repositories = self.github.get_user().get_repos()
