import pandas as pd


def data_import(file_path):
    data = pd.read_csv(file_path)
    data.drop(labels=['Unnamed: 0', 'Unnamed: 0.1'], axis=1, inplace=True)

    return data


def plotting(data, game_idx, rank_base):
    try:
        win_diff_after = data.loc[data['game_idx'] == game_idx].loc[data['rank_base']
                                                                    == rank_base].loc[data['rank_relative']
                                                                                      == rank_base+1, 'win_diff_at_lag']
        win_diff_after = win_diff_after[win_diff_after > -99]

    except:
        win_diff_after = data.loc[data['game_idx'] == game_idx].loc[data['rank_base']
                                                                    == int(rank_base)].loc[data['rank_relative']
                                                                                           == rank_base,
                                                                                           'win_diff_at_lag']

    return win_diff_after


def calc(data, rank_range, idx_range, diff_range):

    calc_prob = []
    for rank in rank_range:
        for idx in idx_range:
            win_diff_after =plotting(data, idx, rank)
            for diff in diff_range:
                try:
                    prob = len(win_diff_after[win_diff_after >= diff]) / len(win_diff_after)
                    calc_prob.append([rank, idx, diff, prob])
                    # print(calc_prob)

                except:
                    pass

    return calc_prob


"""
def calc_smoothing(calc_prob, window_size=5):
"""


def main():
    file_path = './data/result/resulttime_lag_10.csv'
    data = data_import(file_path)
    rank_range = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]
    idx_range = range(1, 145)
    diff_range = range(-7, 8)

    calc_prob = calc(data, rank_range, idx_range, diff_range)
    prob_file = open('./data/result/calc_prob.csv', mode='w')
    for row in calc_prob:
        prob_file.write(str(row[0]) + ',' + str(row[1]) + ',' + str(row[2]) + ',' + str(row[3]) + '\n')

    prob_file.close()


if __name__ == '__main__':
    main()
