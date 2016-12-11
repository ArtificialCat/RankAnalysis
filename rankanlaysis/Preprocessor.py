import pandas as pd

# data import, remove unnecessary rows, columns
raw_data = pd.read_csv('./data/preprocess/raw_data.csv', sep=',')
raw_data.drop(labels=raw_data.loc[raw_data['Season'] == '시즌'].index, axis=0, inplace=True)
raw_data.drop(labels=raw_data.loc[raw_data['Result'] == '우천'].index, axis=0, inplace=True)
raw_data.drop(labels='Unnamed: 0', axis=1, inplace=True)

print(raw_data.head())
print(raw_data['Season'].unique())
print(raw_data['Team1'].unique())

# Regular-Season Filtering (전/후기리그가 있는 1982~1988년도 데이터는 제외)
regular = raw_data.loc[raw_data['Season'] == '정규']
print(regular.head())
print(regular.info())

# Add useful columns
tempResult = []
seasonYear = []
seasonMonth = []
seasonDay = []

for result in regular['Result']:
    tempResult.append(result.split(' ')[0].strip())

for year in regular['Date']:
    split = year.split('-')
    seasonYear.append(split[0].strip())
    seasonMonth.append(split[1].strip())
    seasonDay.append(split[2].strip())

regular['GameResult'] = tempResult
regular['Year'] = seasonYear
regular['Month'] = seasonMonth
regular['Day'] = seasonDay
print(regular.head())

# Exception handling processing
# 2014 - NC vs LG, 2014 - 넥센 vs LG, 2014 - 넥센 vs 삼성, 2016 - LG vs 넥센 : Playoff 경기 섞임
# 2001 - 해태가 기아로 변경(2001시즌부터 기아로 일괄변경)
removal_idx1 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == 'NC'].loc[regular['Team2'] == 'LG'].index[-4:]
removal_idx2 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == 'LG'].loc[regular['Team2'] == 'NC'].index[-4:]
removal_idx3 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == '넥센'].loc[regular['Team2'] == 'LG'].index[-4:]
removal_idx4 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == 'LG'].loc[regular['Team2'] == '넥센'].index[-4:]
removal_idx5 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == '넥센'].loc[regular['Team2'] == '삼성'].index[-6:]
removal_idx6 = regular.loc[regular['Year'] == '2014'].loc[regular['Team1'] == '삼성'].loc[regular['Team2'] == '넥센'].index[-6:]
removal_idx7 = regular.loc[regular['Year'] == '2016'].loc[regular['Team1'] == 'NC'].loc[regular['Team2'] == 'LG'].index[-1:]
removal_idx8 = regular.loc[regular['Year'] == '2016'].loc[regular['Team1'] == 'LG'].loc[regular['Team2'] == 'NC'].index[-1:]
removal_union = list(set().union(removal_idx1, removal_idx2, removal_idx3, removal_idx4, removal_idx5,
                                 removal_idx6, removal_idx7, removal_idx8))
regular.drop(labels=removal_union, axis=0, inplace=True)

idx_home = regular.loc[regular['Year'] == '2001'].loc[regular['Team1'] == '해태', 'Team1'].index
idx_away = regular.loc[regular['Year'] == '2001'].loc[regular['Team2'] == '해태', 'Team2'].index
regular['Team1'][idx_home] = 'KIA'
regular['Team2'][idx_away] = 'KIA'

piv = regular.groupby(by=['Year', 'Team1', 'Team2'], as_index=False).agg({'GameResult': pd.Series.count})
piv.to_csv('./data/preprocess/pivotYear.csv')

# Exception handling process 2
# Date, Team1, Team2, Result 까지 같은 경기가 총 5경기 있음 (더블헤더 & 경기결과 스코어까지 동일)
piv2 = regular.groupby(by=['Year', 'Date', 'Team1', 'Team2', 'Result'], as_index=False).agg({'GameResult': pd.Series.count})
piv2.to_csv('./data/preprocess/pivotYear2.csv')

# Add column: game index
regular = regular.sort_values(['Team1', 'Date'], axis=0)
regular = regular.reset_index()

game_idx = []
for idx, team in enumerate(regular['Team1']):
    if idx == 0:
        game_idx.append(1)
    else:
        if regular['Team1'][idx-1] != regular['Team1'][idx]:
            game_idx.append(1)
        else:
            if regular['Year'][idx-1] != regular['Year'][idx]:
                game_idx.append(1)
            else:
                game_idx.append(game_idx[-1] + 1)

regular['Game_idx'] = game_idx

# Add column: Dummy variable of Win, Draw, Lose
dummy_win = []
dummy_draw = []
dummy_lose = []

for dummy in regular['GameResult']:
    if dummy == 'W':
        dummy_win.append(1)
        dummy_draw.append(0)
        dummy_lose.append(0)

    elif dummy == 'L':
        dummy_win.append(0)
        dummy_draw.append(0)
        dummy_lose.append(1)

    else:
        dummy_win.append(0)
        dummy_draw.append(1)
        dummy_lose.append(0)

regular['dummy_win'] = dummy_win
regular['dummy_lose'] = dummy_lose
regular['dummy_draw'] = dummy_draw

# Pivoting
result_ts = regular.pivot_table(index=['Year', 'Team1', 'Game_idx'], values=['dummy_win', 'dummy_draw', 'dummy_lose'])
result_ts.to_csv('./data/preprocess/result_ts.csv')
result_ts = pd.read_csv('./data/preprocess/result_ts.csv', header=0)

# Calculate cumulative win,lose,draw & Win-Percentage
calc_win = 0
calc_draw = 0
calc_lose = 0
ix_prev = 0
cum_win = []
cum_draw = []
cum_lose = []

for gm_ix, win, draw, lose in zip(result_ts['Game_idx'], result_ts['dummy_win'], result_ts['dummy_draw'],
                                  result_ts['dummy_lose']):
    if int(gm_ix) == 1:
        calc_win = win
        calc_draw = draw
        calc_lose = lose

        cum_win.append(calc_win)
        cum_draw.append(calc_draw)
        cum_lose.append(calc_lose)

        ix_prev = gm_ix

    else:
        if ix_prev > int(gm_ix):
            cum_win.append(calc_win)
            cum_draw.append(calc_draw)
            cum_lose.append(calc_lose)

            calc_win = win
            calc_draw = draw
            calc_lose = lose

            ix_prev += 1

        else:
            calc_win += win
            calc_draw += draw
            calc_lose += lose

            cum_win.append(calc_win)
            cum_draw.append(calc_draw)
            cum_lose.append(calc_lose)

result_ts['cum_win'] = cum_win
result_ts['cum_draw'] = cum_draw
result_ts['cum_lose'] = cum_lose
result_ts['Wpct'] = result_ts['cum_win'] / (result_ts['cum_win'] + result_ts['cum_lose'])

# Export regular season data, Game-Log Time Series
regular.to_csv('./data/preprocess/data.csv')
result_ts.to_csv('./data/preprocess/result_ts.csv')