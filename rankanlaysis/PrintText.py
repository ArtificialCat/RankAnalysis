import pandas as pd
import numpy as np


def season_import(season_path):
    result_ts = pd.read_csv(season_path)
    season = result_ts.loc[result_ts['year'] == 2016]
    season.drop(labels='Unnamed: 0', axis=1, inplace=True)
    print(season)

    return season


def score_import(score_path):
    score = pd.read_csv(score_path)

    return score


def extract_information(season, game_idx, team):

    sorted_rank = np.sort(np.unique(season.loc[season['game_idx'] == game_idx, 'rank_base'].values))
    recent_rank = season.loc[season['team_base'] == team].loc[season['game_idx'] == game_idx, 'rank_base'].values[0]
    recent_rank_idx = np.where(sorted_rank == recent_rank)
    wdf_higher = season.loc[season['team_base'] == team].loc[season['game_idx']
                                                             == game_idx].loc[season['rank_relative']
                                                                              == sorted_rank[recent_rank_idx[0][0]-1],
                                                                              'win_diff'].values[0]

    wdf_lower = season.loc[season['team_base'] == team].loc[season['game_idx']
                                                             == game_idx].loc[season['rank_relative']
                                                                              == sorted_rank[recent_rank_idx[0][0]+1],
                                                                              'win_diff'].values[0]

    return recent_rank, wdf_higher, wdf_lower


def calc_prob(score, game_idx, rank, wdf_higher, wdf_lower):

    if -1.0 * wdf_higher >= 7.0:
        catch_higher = score.loc[score['game_idx'] == game_idx].loc[score['rank']
                                                                    == int(rank)].loc[score['win_diff'] == 7.0,
                                                                                      'probability'].values[0]

    else:
        catch_higher = score.loc[score['game_idx'] == game_idx].loc[score['rank']
                                                                    == int(rank)].loc[score['win_diff']
                                                                                      == int(-1.0 * wdf_higher),
                                                                                      'probability'].values[0]

    if -1.0 * wdf_lower <= -7.0:
        catch_lower = (1.0 - score.loc[score['game_idx'] == game_idx].loc[score['rank']
                                                                          == int(rank)].loc[score['win_diff']
                                                                                            == -7.0,
                                                                                            'probability'].values[0])

    else:
        catch_lower = (1.0 - (score.loc[score['game_idx'] == game_idx].loc[score['rank']
                                                                           == int(rank)].loc[score['win_diff']
                                                                                             == int(-1.0 * wdf_lower),
                                                                                             'probability'].values[0]))

    return catch_higher, catch_lower


def print_text(game_idx, higher_prob, lower_prob):
    if game_idx <= 10:
        print('아직 144경기의 긴 여정의 출발에 불과합니다. 현재 순위는 큰 의미 없습니다. 힘내서 2016 시즌 화이팅!')

    elif game_idx < 90:
        print('10경기 이내에 아래 팀과 승차가 줄어들 확률은 %.2f (%%)입니다' % lower_prob)
        print('10경기 이내에 윗 팀과 승차를 줄일 확률은 %.2f (%%)입니다' % higher_prob)

    elif game_idx <= 133:
        if higher_prob >= lower_prob:
            print('10경기 이내에 윗 팀과 승차를 줄일 확률은 %.2f (%%)입니다, 아래 팀과의 순위 유지보다 높은 곳을 바라보세요!' % higher_prob)

        else:
            print('10경기 이내에 아래 팀과 승차가 줄어들 확률은 %.2f (%%)입니다, 아래 팀과의 승차를 벌리는데 주력해주세요!' % lower_prob)

    else:
        print('시즌이 이미 막바지입니다. 치열한 경기 전망은 한 경기 한경기에 따라 결정될 가능성이 높습니다. 경기 신호등을 참조해주세요!')


def main():
    season_path = './data/flatten/result.csv'
    score_path = './data/result/calc_prob.csv'
    season_data = season_import(season_path)
    score_data = score_import(score_path)
    game_idx = 122
    team = 'LG'

    rank, wdf_higher, wdf_lower = extract_information(season_data, game_idx, team)
    higher_prob, lower_prob = calc_prob(score_data, game_idx, rank, wdf_higher, wdf_lower)
    higher_prob *= 100
    lower_prob *= 100

    print('현재 %s의 %d 경기 시점에서의 순위는 %d(위)이며, 아래 팀과의 승차는 %.2f, 위 팀과의 승차는 %.2f 입니다.'
          % (team, game_idx, rank, wdf_lower, wdf_higher))
    print_text(game_idx, higher_prob, lower_prob)

if __name__ == '__main__':
    main()
