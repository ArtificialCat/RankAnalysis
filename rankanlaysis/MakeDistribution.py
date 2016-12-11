import pandas as pd
import itertools
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt


def season_index():
    data = pd.read_csv('./data/preprocess/result_ts.csv', header=0)
    print(data.columns.unique())

    for idx, season in zip(data['Game_idx'], data['Year']):
        temp_idx = data.loc[data['Game_idx'] == idx]
        temp_season = data.loc[data['Year'] == season]
        join_table = pd.merge(left=temp_idx[['Year', 'Game_idx', 'Team1', 'cum_win', 'cum_lose', 'cum_draw', 'Wpct']],
                              right=temp_season[['Year', 'Game_idx', 'Team1', 'cum_win', 'cum_lose', 'cum_draw', 'Wpct']],
                              how='inner', on=['Year', 'Game_idx', 'Team1'])
        join_table.drop(labels=['Wpct_y', 'cum_win_y', 'cum_lose_y', 'cum_draw_y'], axis=1, inplace=True)
        join_table.columns = ['Year', 'Game_idx', 'Team1', 'cum_win', 'cum_lose', 'cum_draw', 'Wpct']
        join_table['rank'] = join_table['Wpct'].rank(ascending=False)
        join_table.to_csv('./data/dictionary/' + '_'.join(['dictionary', str(idx), str(season)]) + '.csv')


def calc_win_diff(season, game_idx):
    data = pd.read_csv('./data/dictionary/' + '_'.join(['dictionary', str(game_idx), str(season)]) + '.csv')
    temp = pd.merge(left=data, right=data, how='outer', on='Game_idx')
    temp['win_diff'] = ((temp['cum_win_x'] - temp['cum_win_y']) - (temp['cum_lose_x'] - temp['cum_lose_y'])) / 2.0
    win_diff = temp.pivot_table(index='Team1_x', columns='Team1_y', values='win_diff')

    return win_diff


def save_win_diff(win_diff_mat, season, game_idx):
    win_diff_mat.to_csv('./data/win_diff_matrix/WinDiffMat_' + '_'.join([str(season), str(game_idx)]) + '.csv')


def run_win_diff():
    for season in range(1989, 2017):
        for game_idx in range(1, 145):
            try:
                result = calc_win_diff(season, game_idx)
                save_win_diff(result, season, game_idx)

            except OSError:
                print(season, game_idx)


def flatten_win_diff():
    season_range = range(1989, 2017)
    idx_range = range(1, 145)
    season_idx_pair = list(itertools.product(season_range, idx_range))
    """
    두 팀간의 승차는 상대적 상위의 팀이 양수의 값을 갖도록 한다.
    """
    result = pd.DataFrame(data=[['Null', 'Null', 0.0, 0, 0, 0, 0]],
                          columns=['team_base', 'team_relative', 'win_diff', 'game_idx',
                                   'year', 'rank_base', 'rank_relative'])
    for idx, pair in enumerate(season_idx_pair):
        try:
            rank_data = pd.read_csv('./data/dictionary/' +
                                    '_'.join(['dictionary', str(pair[1]), str(pair[0])])+'.csv')
            win_diff = pd.read_csv('./data/win_diff_matrix/' +
                                   '_'.join(['WinDiffMat', str(pair[0]), str(pair[1])])+'.csv')

            team_list = list(win_diff.columns)[1:]
            win_diff_unpivot = pd.melt(win_diff, id_vars=['Team1_x'], value_vars=team_list)
            win_diff_unpivot.columns = ['team_base', 'team_relative', 'win_diff']
            win_diff_unpivot['game_idx'] = [pair[1]] * win_diff_unpivot.shape[0]
            win_diff_unpivot['year'] = [pair[0]] * win_diff_unpivot.shape[0]

            team_pair = list(zip(win_diff_unpivot['team_base'], win_diff_unpivot['team_relative']))
            rank_base = []
            rank_relative = []
            for teams in team_pair:
                rank_base += list(rank_data.loc[rank_data['Team1'] == str(teams[0]), 'rank'].values)
                rank_relative += list(rank_data.loc[rank_data['Team1'] == str(teams[1]), 'rank'].values)

            win_diff_unpivot['rank_base'] = rank_base
            win_diff_unpivot['rank_relative'] = rank_relative

            result = result.append(win_diff_unpivot, ignore_index=True)

        except OSError:
            print(pair)

    result.drop(labels=0, axis=0, inplace=True)
    result.to_csv('./data/result.csv')


def add_time_lag_info():
    data = pd.read_csv('./data/flatten/result.csv')
    season_range = range(1989, 2017)
    time_lag = 10
    result = pd.DataFrame(data=[['Null', 'Null', 0.0, 0, 0, 0, 0, 99]],
                          columns=['team_base', 'team_relative', 'win_diff', 'game_idx',
                                   'year', 'rank_base', 'rank_relative','win_diff_at_lag'])
    for year in season_range:
        year_data = data.loc[data['year'] == year]
        difference = []
        for idx, t1, t2, current_diff in zip(year_data['game_idx'], year_data['team_base'], year_data['team_relative'],
                                             year_data['win_diff']):

            try:
                future_diff = year_data.loc[year_data['team_base'] == t1].loc[year_data['team_relative']
                                                                              == t2].loc[year_data['game_idx']
                                                                                         == idx+time_lag, 'win_diff'].values[0]
                difference.append(float(future_diff - current_diff))
                print(year_data.shape[0] - len(difference))

            except IndexError:
                print(year, idx)
                difference.append(-99)

            except ValueError:
                print(year, idx)
                difference.append(-99)

        year_data['win_diff_at_lag'] = difference
        result = result.append(year_data, ignore_index=True)

    # result.drop(label=0, axis=0, inplace=True)
    result.to_csv('./data/result/result' + '_'.join(['time', 'lag', str(time_lag)]) + '.csv')


def extract_apply_data():
    result = pd.read_csv('./data/flatten/result.csv')
    print(result.columns.unique())
    result.drop(labels='Unnamed: 0', axis=1, inplace=True)
    team_list = result.loc[result['year'] == 2016, 'team_base'].unique()
    print(team_list)

    # 2016시즌은 각 팀당 144경기씩을 치룸
    idx_range = range(1, 145)
    year = 2016
    season_data = []

    for pair in list(itertools.product(team_list, idx_range)):
        row = result.loc[result['year'] == year].loc[result['team_base'] == pair[0]].loc[result['game_idx'] ==
                                                                                         pair[1]].values
        print(row)
        season_data.append(row)

    extract_season = pd.DataFrame(data=season_data, columns=['team_base', 'team_relative', 'win_diff', 'game_idx',
                                                             'year', 'rank_base', 'rank_relative'])
    extract_season.to_csv('./data/result/season_data.csv')


def main():
    """
    season_index()
    run_win_diff()
    flatten_win_diff()
    add_time_lag_info()
    extract_apply_data()
    """


if __name__ == '__main__':
    main()
