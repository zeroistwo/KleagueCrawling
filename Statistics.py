from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from tqdm import *
import helper.crawlerCommon as crawlerCommon

# URL 변수
URL = "http://www.kleague.com/schedule/get_lists?datatype=html&month="
MATCHCENTERURL = "http://www.kleague.com/match?vw=record&gs_idx="
SELECTLEAGUE = "&select_league="
SELECTLEAGUEYEAR = "&select_league_year=2018"

# CLASS 명
BUTTONCLASS = "btn btn-outline-blue btn_matchcenter"
ACLDIVCLASS = "clearfix team-score"

# 기타 변수
MONTH = 12
TEAMNUMBERS = 2
DATAFRAME = ['Match_ID', 'Team', '점유율', '슈팅', '유효슈팅', '파울', '경고', '퇴장', '코너킥', '프리킥', '오프사이드']
STATCONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "


def getData(match_id, name_home_team, name_away_team, score_statistics):
    statistics_list = []
    for i in range(TEAMNUMBERS):
        try:
            raw_data = []
            raw_data.append(match_id)                           # 1. Match_ID
            if i == 0:
                raw_data.append(name_home_team)                 # 2. Team
            else:
                raw_data.append(name_away_team)                 # 2. Team
            for j in range(i, len(score_statistics), 2):
                each_data = []
                text_score_statistics = score_statistics[j].get_text().split(' ')
                # 특정 통계 지표에 공백이 존재하므로 체크: text_score_statistics[0]의 값이 존재할 경우에 each_data list에 추가
                if text_score_statistics[0]:
                    each_data.append(text_score_statistics[0])  # 3~9. 경기 통계
                else:
                    each_data.append(text_score_statistics[1])  # 3~9. 경기 통계
                raw_data.extend(each_data)
            statistics_list.append(raw_data)

        except Exception as e:
            print(e)

    return statistics_list


def setBasicInfo(league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    for n in range(MONTH):
        url = urlopen(URL + str(n + 1).zfill(2) + SELECTLEAGUE + league_num + SELECTLEAGUEYEAR).read()  # 크롤링하고자 하는 사이트 url명을 입력
        soup = bs(url, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행

        match_list = crawlerCommon.getButtonList(soup, league_str, BUTTONCLASS, ACLDIVCLASS)
        match_number = len(match_list)

        # html source에서 각 경기의 고유 번호인 gs_idx를 모두 읽어와 gs_idxList에 저장
        gs_idxList = []
        for i in range(match_number):
            idxList = []
            idxList.append(match_list[i].get('gs_idx'))
            gs_idxList.append(idxList)

        # 공통
        data_list = []
        for j in tqdm(range(match_number)):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
            try:
                html = urlopen(MATCHCENTERURL + str(gs_idxList[j][0])).read()  # 각 매치센터 페이지 사이 url 입력
                body = bs(html, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
                match_id = gs_idxList[j][0]
                name_home_team = body.findAll('div', class_="team-1")[0].get_text()
                name_away_team = body.findAll('div', class_="team-2")[0].get_text()
                score_statistics = body.find('div', class_="compare-data").findAll('div', class_='score')
                statistics_list = getData(match_id, name_home_team, name_away_team, score_statistics)
                data_list.extend(statistics_list)

            except Exception as e:
                print(e)

        result.extend(data_list)

    return result


def crawlStatistics():
    while True:
        league_num = input(STATCONSOLEGUIDE)
        if league_num in ["1", "2"]:
            league_str = "K" + league_num
        else:
            print(STATCONSOLEGUIDE)
            continue
        result = setBasicInfo(league_num, league_str)
        crawlerCommon.saveAsCSV(result, league_str, DATAFRAME)


if __name__ == "__main__":
    crawlStatistics()