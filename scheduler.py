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

    def make_schedule(self):
        schedule = None
        iterations = invalid = unbalanced = 0
        while schedule is None:
            iterations += 1
            print 'Attempt {}'.format(iterations)
            try:
                schedule = self.try_random_schedule()
            except InvalidSchedule:
                invalid += 1
            except UnbalancedSchedule:
                unbalanced += 1
        print 'Tried {} schedules ({} invalid, {} unbalanced) before finding a valid one.'.format(
            iterations, invalid, unbalanced)
        return schedule

    def create_pairings(self):
        return [game for game in itertools.combinations(self.team_names, 2)]

    def try_random_schedule(self):
        pairings = self.create_pairings()
        week_count = len(pairings) / len(self.sheet_names)

        team_sheet_counts = self.initialize_team_sheet_counts()

        schedule = []
        for i in range(week_count):
            week_pairings = []
            used_teams = []
            for sheet in self.sheet_names:
                available_pairings = [p for p in pairings if p[0] not in used_teams and p[1] not in used_teams]
                try:
                    game = random.choice(available_pairings)
                except IndexError:
                    raise InvalidSchedule()
                pairings.remove(game)
                used_teams.extend(game)
                week_pairings.append(game)
                sheet_number = i + 1
                # Count how many times each team has played on this sheet
                team_sheet_counts[game[0]][sheet] += 1
                team_sheet_counts[game[1]][sheet] += 1
            schedule.append(week_pairings)

        print 'Checking for sheet balance'
        if not self.schedule_is_balanced(team_sheet_counts, week_count):
            raise UnbalancedSchedule()
        for team, counts in team_sheet_counts.items():
            print team, counts

        return schedule

    def initialize_team_sheet_counts(self):
        """Returns sheet counting dict with all values at zero."""
        team_sheet_counts = {}
        sheet_count_model = {}
        for sheet in self.sheet_names:
            sheet_count_model[sheet] = 0
        for team in self.team_names:
            team_sheet_counts[team] = sheet_count_model.copy()
        return team_sheet_counts

    def schedule_is_balanced(self, team_sheet_counts, week_count):
        """Checks if a schedule is perfectly balanced across sheets.

        A perfectly balanced schedule has each team playing a balanced number
        of games on each sheet. Example: In a 10 team, 9 week league over
        5 sheets, each team plays 2 games on 4 sheets, and 1 game on the fifth.
        """
        average_per_sheet = float(week_count) / float(len(self.sheet_names))
        max_per_sheet = int(math.ceil(average_per_sheet))
        min_per_sheet = int(math.floor(average_per_sheet))
        for team, counts in team_sheet_counts.items():
            for sheet, count in counts.items():
                if count > max_per_sheet or count < min_per_sheet:
                    return False
        return True

    def print_schedule_header(self):
        """Prints ASCII schedule header with sheet names."""
        header = '| Sheet 1 | Sheet 2 |'
        header_parts = ['']
        for sheet in self.sheet_names:
            header_parts.append(' Sheet {} '.format(sheet))
        header_parts.append('')
        print '|'.join(header_parts)

    def print_schedule(self, schedule):
        """Prints an ASCII schedule."""
        self.print_schedule_header()
        for week in schedule:
            week_parts = ['']
            for game in week:
                week_parts.append('  {} - {}  '.format(*game))
            week_parts.append('')
            print '|'.join(week_parts).strip()


if __name__ == '__main__':
    schedule_maker = ScheduleMaker(TEAM_NAMES, SHEET_NAMES)
    schedule = schedule_maker.make_schedule()
    schedule_maker.print_schedule(schedule)
