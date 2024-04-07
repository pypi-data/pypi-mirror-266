from requests import get
from bs4 import BeautifulSoup, Tag
import re
from random_user_agent.params import HardwareType, SoftwareType, Popularity
from random_user_agent.user_agent import UserAgent

def __get_user_agent__():
    return {"User-Agent": UserAgent(
        hardware_types=[HardwareType.COMPUTER.value],
        software_type=[SoftwareType.WEB_BROWSER.value],
        popularity=[Popularity.POPULAR.value]
    ).get_random_user_agent()}

class BaekjoonUser:
    """백준 유저의 정보 클래스 (Baekjoon User Information Class)"""
    def __init__(self, user_name):
        """유저의 정보를 가져옵니다 (Get user information)"""
        soup = BeautifulSoup(get(f'https://www.acmicpc.net/user/{user_name}', headers=__get_user_agent__()).text, 'lxml')
        self.user_name = user_name
        self.status = soup.find('blockquote', {'class': 'no-mathjax'}).text.removesuffix('정보언어')
        self.rank = soup.select_one("#statics > tbody > tr:nth-child(1) > td").text
        self.correct_qs = soup.select_one("body > div.wrapper > div.container.content > div.row > div:nth-child(2) > div > div.col-md-9 > div:nth-child(1) > div.panel-body").text
        self.correct_q = soup.select_one("#u-solved").text
        self.unsolved_qs = soup.select_one("body > div.wrapper > div.container.content > div.row > div:nth-child(2) > div > div.col-md-9 > div:nth-child(2) > div.panel-body").text.split(" ")
        del self.unsolved_qs[len(self.unsolved_qs) - 1]
        self.unsolved_qs = list(map(int, self.unsolved_qs))
        self.unsolved_q = soup.select_one("#u-failed").text
        self.submit_time = soup.select_one("#statics > tbody > tr:nth-child(4) > td").text
        self.status = soup.find('blockquote', {'class': 'no-mathjax'}).text
        self.correct_q = soup.select_one('#u-solved').text

class BaekjoonProb:
    """백준 문제의 정보 클래스 (Baekjoon Problem Information Class)"""
    def __init__(self, number, url: str = "https://www.acmicpc.net/problem/"):
        """문제의 정보를 가져옵니다 (Get problem information)"""
        soup = BeautifulSoup(get(f"{url}{number}", headers=__get_user_agent__()).text, "lxml")
        self.number = number
        self.question = soup.select_one("#problem_description > p").text
        if soup.select_one("#problem_input > p") is not None:
            self.input = soup.select_one("#problem_input > p").text
        else:
            self.input = None
        if soup.select_one("#problem_output > p") is not None:
            self.output = soup.select_one("#problem_output > p").text
        else:
            self.output = None
        self.sample_input = [i.text for i in soup.find_all(id=re.compile("^sample-input"))]
        self.sample_output = []
        self.sample_output.extend(i.text for i in soup.find_all(id=re.compile("^sample-output")))
        self.correct_rate = soup.select_one("#problem-info > tbody > tr > td:nth-child(6)").text
        self.time_limit = float(''.join(filter(lambda s: s in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'], soup.select_one("#problem-info > tbody > tr > td:nth-child(1)").text)))
        self.memory_limit = soup.select_one("#problem-info > tbody > tr > td:nth-child(2)").text

class BaekjoonCompetition:
    """백준 대회 클래스 (Baekjoon Competition Class)"""
    def __init__(self, number: int):
        soup = BeautifulSoup(get(f"https://www.acmicpc.net/contest/view/{number}", headers=__get_user_agent__()).text, "lxml")
        _cache = soup.find_all("div", {"class": "page-header"}, recursive=True)[0]
        self.number = number
        self.name = _cache.find("h1").text.removeprefix("\n").split("\n")[0]
        self.username = _cache.find("a").text
        self.start = min(map(int, self.__timestamp__(_cache.find("blockquote").find_all("span", {"class": "update-local-time"}))))
        self.stop = max(map(int, self.__timestamp__(_cache.find("blockquote").find_all("span", {"class": "update-local-time"}))))

    def __timestamp__(self, a: list[Tag]):
        return [i["data-timestamp"] for i in a]

class SolvedACClassDecoration:
    none = "none",
    silver = "silver",
    gold = "gold"

class SolvedACUser:
    """Solved.ac 유저의 정보 클래스 (Solved.ac User Information Class)"""
    def __init__(self, name):
        """유저의 정보를 가져옵니다 (Get user information)"""
        tiers = ["Unranked", "Bronze V", "Bronze IV", "Bronze III", "Bronze II", "Bronze I", "Silver V", "Silver IV", "Silver III", "Silver II", "Silver I", "Gold V", "Gold IV", "Gold III", "Gold II", "Gold I", "Platinum V", "Platinum I",
                 "Diamond IV", "Diamond III", "Diamond II", "Diamond I", "Ruby V", "Ruby IV", "Ruby III", "Ruby II", "Ruby I", "Master"]
        self.name = name
        apire = get("https://solved.ac/api/v3/user/show", params={"handle": name}, headers={"Content-Type": "application/json"}).json()
        self.bio = apire["bio"]
        self.badge = apire.get("badgeId")
        self.background = apire["backgroundId"]
        self.profileimage = apire["profileImageUrl"]
        self.solved = int(apire["solvedCount"])
        self.vote = int(apire["voteCount"])
        self.solvedacclass = int(apire["class"])
        self.classDecoration = apire["classDecoration"]
        self.tier = tiers[apire["tier"]]
        self.rating = int(apire["rating"])
        self.ratingByProblemsSum = int(apire["ratingByProblemsSum"])
        self.ratingByClass = int(apire["ratingByClass"])
        self.ratingByVoteCount = int(apire["ratingByVoteCount"])
        self.rivalCount = int(apire["rivalCount"])
        self.reverseRivalCount = int(apire["reverseRivalCount"])
        self.maxStreak = int(apire["maxStreak"])
        self.coins = int(apire["coins"])
        self.stardusts = int(apire["stardusts"])
        self.joinedAt = apire["joinedAt"]
        self.bannedUntil = apire["bannedUntil"]
        self.proUntil = apire["proUntil"]
        self.rank = int(apire["rank"])