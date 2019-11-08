from minitools.github.commits import GithubCommitTimes


class SGithubCommitTimes(GithubCommitTimes):

    def commits_counts(self, start, end):
        time, count = super().commits_counts(start, end)
        print(time, count)


if __name__ == '__main__':
    h = SGithubCommitTimes('account', 'password')
    h.get_statistics_all_month()
    h.get_statistics_appoint_month()
