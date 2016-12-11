import pandas as pd
import numpy as np
import itertools


def season_import(season_path):
    result_ts = pd.read_csv(season_path)
    season = result_ts.loc[result_ts['year'] == 2016]
    season = season.drop(labels='Unnamed: 0', axis=1)

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


def print_text(rank, game_idx, higher_prob, lower_prob):
    if game_idx <= 10:
        text = ('아직 144경기의 긴 여정의 출발에 불과하며, 현재 순위는 큰 의미 없습니다. 힘내서 2016 시즌 화이팅!')

    elif game_idx < 90:
        if higher_prob >= lower_prob:
            text = ('10경기 이내에 윗 팀과 승차를 줄일 확률은 %.2f (%%)입니다, 아래 팀과의 순위 유지보다 높은 곳을 바라보세요!' % higher_prob)
        else:
            text = ('10경기 이내에 아래 팀과 승차가 줄어들 확률은 %.2f (%%)입니다, 아래 팀과의 승차를 벌리는데 주력해주세요!' % lower_prob)

    elif game_idx <= 133:
        if int(rank) == 4:
            if higher_prob >= lower_prob:
                text = ('향후 10경기에서 3위권과의 승차를 줄일 수 있을 가능성이 %.2f (%%)로 5위권에게 추격당할 확률보다 높습니다.' % higher_prob)
            else:
                text = ('향후 10경기에서 5위권과의 격차가 줄어들 확률이 %.2f (%%)로 3위권 추격 확률보다 높습니다.' % lower_prob)

        elif int(rank) == 5:
            if higher_prob >= lower_prob:
                text = ('향후 10경기 내에 4위와의 격차를 줄일 수 있을 확률이 높습니다: %.2f (%%)' % higher_prob)
            else:
                text = ('4위권 추월 확률보다 플레이오프 마지노선인 5위 수성이 위태로운 상황입니다. 6위와의 격차를 벌려야합니다.: %.2f (%%)' % lower_prob)

        elif int(rank) == 3:
            if higher_prob >= lower_prob:
                text = ('향후 10경기 후에 플레이오프 직행을 위한 2위 자리를 뺏을 수 있을 확률은 %.2f (%%)입니다.' % higher_prob)
            else:
                text = ('향후 10경기 후에 4위권에게 추월당할 확률은 %.2f (%%)입니다. 3위권 수성을 목표로 하세요, 3위와 4위의 차이는 큽니다.' % lower_prob)

        elif int(rank) == 2:
            if higher_prob >= lower_prob:
                text = ('향후 10경기 내에 1위 자리를 탈환할 수 있을 확률은 %.2f (%%)입니다. ' % higher_prob)
            else:
                text = ('향후 10경기 내에는 2위권 수성을 목표로 하세요. 2위를 빼앗길 확률이 %.2f (%%)입니다.' % lower_prob)

        elif rank == 1:
            text = ('2위 권에게 추월당할 확률은 %.2f (%%)입니다.' % lower_prob)

        else:
            if higher_prob >= lower_prob:
                text = ('상위 팀을 추월할 확률은 %.2f (%%)입니다. 플레이오프 진출을 위해 갈길이 멀어요!' % higher_prob)
            else:
                text = ('하위 팀에게 추월당할 확률이 %.2f (%%)로 더 높지만, 매치업에 따라 결과는 충분히 달라질 수 있어요' % lower_prob)

    else:
        text = ('시즌이 이미 막바지므로 치열한 경기 전망은 한 경기 한경기에 따라 결정될 가능성이 높습니다, 경기 신호등을 참조해주세요!')

    return text


def main():
    season_path = './data/flatten/result.csv'
    score_path = './data/result/calc_prob.csv'
    season_data = season_import(season_path)
    score_data = score_import(score_path)
    result_file = open('./data/result/rank_upcoming_db.csv', mode='w')

    for game_idx, team in zip(season_data['game_idx'], season_data['team_base']):
        try:
            rank, wdf_higher, wdf_lower = extract_information(season_data, game_idx, team)
            higher_prob, lower_prob = calc_prob(score_data, game_idx, rank, wdf_higher, wdf_lower)
            higher_prob *= 100
            lower_prob *= 100

            print('현재 %s의 %d 경기 시점에서의 순위는 %d(위)이며, 아래 팀과의 승차는 %.2f, 위 팀과의 승차는 %.2f 입니다.'
                  % (team, game_idx, rank, wdf_lower, wdf_higher))
            print('-----------------------------------------------------------------------------------')
            text = print_text(rank, game_idx, higher_prob, lower_prob)
            result_file.write(str(game_idx) + ',' + team + ',' + text + '\n')

        except IndexError:
            # print(element[0], element[1])
            pass

    result_file.close()


if __name__ == '__main__':
    main()
