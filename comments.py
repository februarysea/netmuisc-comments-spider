import requests
import json
from pyquery import PyQuery as pq
import pymongo
import time

def count_time(func):
    def wrapper(*arg, **kwargs):
        start_time = time.time()
        func(*arg, **kwargs)
        print(f"start time:{time.asctime(time.localtime(start_time))}")
        print(f"stop time:{time.localtime(time.time())}")
    return wrapper



client = pymongo.MongoClient(host="localhost", port=27017)
db = client["netmusic"]

collection = db["comments"]

@ count_time
def get_comments(uid:str):
    # log in
    login_url = "http://localhost:3000/login?email=??&password=??"
    requests.get(url=login_url)

    # get songmenu
    song_menu_list = []
    song_menu_url = f"http://localhost:3000/user/playlist?uid={uid}"
    song_menu_response = requests.get(url=song_menu_url)
    song_menus = json.loads(song_menu_response.text)
    for item in song_menus["playlist"]:
        if str(item["creator"]["userId"]) == uid:
            song_menu_list.append(str(item["id"]))
            print("addmenu:" + str(item["id"]))
        else:
            continue
    
    # get song
    songs = []
    for menu_id in song_menu_list:
        song_url = f"http://localhost:3000/playlist/detail?id={menu_id}"
        song_response = json.loads(requests.get(url=song_url).text)
        for item in song_response["privileges"]:
            songs.append(str(item["id"]))
            print("addsong:" + str(item["id"]))
    
    songs = set(songs)
    songs = list(songs)

    # get comment
    for song_id in songs:
        pageNO = 1
        comment_url = f"http://localhost:3000/comment/new?type=0&pageSize=20&id={song_id}&sortType=3"
        cursor = ""
        while 1:
            if pageNO!=1:
                comment_url = f"http://localhost:3000/comment/new?type=0&pageSize=20&id={song_id}&sortType=3&pageNo={pageNO}&cursor={cursor}"
            response = requests.get(url=comment_url).text
            response = json.loads(response)
            comments = response["data"]["comments"]
            cursor = response["data"]["cursor"]
            if comments:
                for item in comments:
                    if item["user"]["userId"]== uid:
                        dic = {}
                        timeArray = time.localtime(item["time"])
                        temp_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                        dic["time"] = temp_time
                        dic["content"] = item["content"]
                        collection.insert_one(dic)
                        print(f"time:{temp_time}, content:{item['content']}")
            else:
                break
            pageNO = pageNO + 1

if __name__ == "__main__":
    # uid
    uid = "???"
    get_comments(uid=uid) 
