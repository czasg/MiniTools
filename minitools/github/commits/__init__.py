from minitools import to_datetime, timekiller
from minitools.github.base import GithubBase


class GithubCommitTimes(GithubBase):

    def __init__(self, *account):
        super(GithubCommitTimes, self).__init__(*account)

    def get_commit_by_datetime(self, from_time, to_time):
        commit_times = 0
        for repo in self.all_repositories:
            commit_times += repo.get_commits(since=to_datetime(from_time), until=to_datetime(to_time)).totalCount
        return commit_times

    def commits_counts(self, start, end):
        current_month_first_day = timekiller.create(start, end, 1)
        current_month_last__day = timekiller.create(start, end, timekiller.get_len_of_month(current_month_first_day))
        return current_month_first_day, self.get_commit_by_datetime(current_month_first_day, current_month_last__day)

    def get_statistics_all_month(self, start_year=None):
        now = timekiller.get_now()
        current_year, current_month = now.year, now.month
        start_year = start_year or current_year
        while start_year <= current_year:
            for month in range(1, 13):
                if month > current_month and start_year == current_year:
                    break
                self.commits_counts(start_year, month)
            start_year += 1

    def get_statistics_appoint_month(self, year=None, month=None):
        now = timekiller.get_now()
        year, month = (year, month) if year and month else (now.year, now.month)
        self.commits_counts(year, month)
