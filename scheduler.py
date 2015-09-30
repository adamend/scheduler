"""
Next thing to try:
- Generate a random (valid) schedule.
- Count number of problems (over min/under max per sheet)
- Randomly swap two games (possibly limiting the swap pool to only valid swaps?)
- Count number of problems
- If lower, replace schedule and repeat
"""

from collections import OrderedDict
import itertools
import math
import random


TEAM_NAMES = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    ## 'G',
    ## 'H',
    ## 'I',
    ## 'J',
]
SHEET_NAMES = [
    'A',
    'B',
    'C',
    ## 'D',
    ## 'E'
]


class InvalidSchedule(Exception): pass
class UnbalancedSchedule(Exception): pass


class ScheduleMaker(object):

    def __init__(self, team_names, sheet_names):
        self.team_names = team_names
        self.sheet_names = sheet_names
        self.schedule = None

    def make_schedule(self):
        iterations = invalid = unbalanced = 0
        self.create_valid_schedule()
        self.balance_schedule()
        return self.schedule

    def create_pairings(self):
        return [game for game in itertools.combinations(self.team_names, 2)]

    def create_valid_schedule(self):
        self.pairings = self.create_pairings()
        self.week_count = len(self.pairings) / len(self.sheet_names)

        self.schedule = []
        while not self.schedule:
            pairings = self.pairings[:]
            try:
                for i in range(self.week_count):
                    week_pairings = []
                    used_teams = []
                    for sheet in self.sheet_names:
                        available_pairings = [p for p in pairings if p[0] not in used_teams and p[1] not in used_teams]
                        game = random.choice(available_pairings)
                        pairings.remove(game)
                        used_teams.extend(game)
                        week_pairings.append(game)
                    self.schedule.append(week_pairings)
            except IndexError:
                self.schedule = []

    def balance_schedule(self):
        print '------------------Initial schedule--------------------'
        self.print_schedule()
        best_score = self.score_schedule()
        print 'Score:', best_score

        iteration = 0
        while best_score > 0:
            iteration += 1
            print '----------Iteration {}----------'.format(iteration)
            new_schedule = self.tweak_schedule()
            self.print_schedule()
            new_score = self.score_schedule()
            print 'Best score:', best_score, '  New score:', new_score
            if new_score < best_score:
                print 'This is better, keeping it'
                best_score = new_score
                self.schedule = new_schedule

    def score_schedule(self):
        team_sheet_counts = OrderedDict()
        sheet_count_model = OrderedDict()
        for sheet in self.sheet_names:
            sheet_count_model[sheet] = 0
        for team in self.team_names:
            team_sheet_counts[team] = sheet_count_model.copy()

        for week in self.schedule:
            for sheet_index, game in enumerate(week):
                sheet = self.sheet_names[sheet_index]
                team_sheet_counts[game[0]][sheet] += 1
                team_sheet_counts[game[1]][sheet] += 1

        average_per_sheet = float(self.week_count) / float(len(self.sheet_names))
        max_per_sheet = int(math.ceil(average_per_sheet))
        min_per_sheet = int(math.floor(average_per_sheet))
        score = 0
        for team, counts in team_sheet_counts.items():
            print team, counts.items()
            for count in counts.values():
                if count > max_per_sheet or count < min_per_sheet:
                    score += 1
        return score

    def tweak_schedule(self):
        schedule = self.schedule[:]
        week = random.choice(schedule)
        game1, game2 = random.sample(week, 2)
        game1_index = week.index(game1)
        game2_index = week.index(game2)
        week[game1_index], week[game2_index] = week[game2_index], week[game1_index]

        week_index = schedule.index(week)
        print '----------Swapped sheet {} and {} on week {}----------'.format(
            self.sheet_names[game1_index], self.sheet_names[game2_index], week_index + 1)
        return schedule

    def print_schedule_header(self):
        """Prints ASCII schedule header with sheet names."""
        header = '| Sheet 1 | Sheet 2 |'
        header_parts = ['']
        for sheet in self.sheet_names:
            header_parts.append(' Sheet {} '.format(sheet))
        header_parts.append('')
        print '|'.join(header_parts)

    def print_schedule(self):
        """Prints an ASCII schedule."""
        self.print_schedule_header()
        for week in self.schedule:
            week_parts = ['']
            for game in week:
                week_parts.append('  {} - {}  '.format(*game))
            week_parts.append('')
            print '|'.join(week_parts).strip()


if __name__ == '__main__':
    schedule_maker = ScheduleMaker(TEAM_NAMES, SHEET_NAMES)
    schedule = schedule_maker.make_schedule()
