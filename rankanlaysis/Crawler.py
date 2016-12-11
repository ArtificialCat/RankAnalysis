import urllib.request
import pandas as pd
from bs4 import BeautifulSoup

# 스탯티즈 스코어 게시판을 대상으로 전 시즌 기간의 경기 스코어 데이터 수집
teamList = ['KIA', 'kt', 'LG', 'NC', 'MBC', 'OB', 'SK', '%EB%84%A5%EC%84%BC', '%EB%91%90%EC%82%B0',
            '%EB%A1%AF%EB%8D%B0', '%EB%B9%99%EA%B7%B8%EB%A0%88', '%EC%82%BC%EB%AF%B8', '%EC%82%BC%EC%84%B1',
            '%EC%8C%8D%EB%B0%A9%EC%9A%B8', '%EC%B2%AD%EB%B3%B4', '%ED%83%9C%ED%8F%89%EC%96%91', '%ED%95%9C%ED%99%94',
            '%ED%95%B4%ED%83%9C', '%ED%98%84%EB%8C%80', '%ED%9E%88%EC%96%B4%EB%A1%9C%EC%A6%88']

tbl_col = 16
tbl = []
row = []
cite = []

for t1 in teamList:
    for t2 in teamList:
        cite.append("http://www.statiz.co.kr/scorestat.php?opt=3&sm=" + t1 + "&sm2=" + t2)

for comb in cite:
    url = comb
    print(url)
    Result = urllib.request.urlopen(url)
    soup = BeautifulSoup(Result)

    if len(soup.find_all('td')) == 0:
        pass

    else:
        for idx, td_tag in enumerate(soup.find_all('td')):
            if idx == 0:
                pass

            elif idx % tbl_col != 0:
                row.append(td_tag.text)

            else:
                print(row)
                tbl.append(row)
                row = []

data = pd.DataFrame(tbl, columns=['Season', 'Date', 'Time', 'Stadium', 'Team1', 'Team1_Pitcher', 'T', 'Result', 'Team2',
                                  'Team2_Pitcher', 'T2', 'Win_Pit', 'Lose_Pit', 'Save', 'Audience'])
data.to_csv('./data/preprocess/raw_data.csv')
