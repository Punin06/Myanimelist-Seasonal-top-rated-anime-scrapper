from flask import Flask, render_template, request
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

import pandas as pd

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def index():

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    titles = []
    if request.method =="POST":
        
        url = "https://myanimelist.net/anime/season"

        #Storing the seasons of the buttons
        x = request.form.get("btn1")
        
        c = request.form.get("btn2")
        
        v = request.form.get("btn3")
        #Visiting the site for those seasons
        if request.form.get("btn1") == x and x!=None:
            url = f"https://myanimelist.net/anime/season/{x.split()[1]}/{x.split()[0]}"

        elif (request.form.get("btn2") == c and c!=None):
            url = f"https://myanimelist.net/anime/season/{c.split()[1]}/{c.split()[0]}"

        elif request.form.get("btn3") == v and v!=None:
            url = f"https://myanimelist.net/anime/season/{v.split()[1]}/{v.split()[0]}"
        #Setting up variable to store respecitve values and the BS
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        date = []
        score = []
        images = []
        links = []
        genre = []
        episode = []
        df = pd.DataFrame()
        animes = soup.find_all("div", attrs = {"class" : "js-anime-category-producer seasonal-anime js-seasonal-anime js-anime-type-all js-anime-type-1"})
        szn = soup.find("a", attrs = {"class": "on"}).text.split()
        #storing the values for the following
        for dates in animes:
            c = []
            day = dates.find("span", attrs = {"class" : "item"}).text
            episode.append(dates.find_all("span", attrs = {"class" : "item"})[1].text)
            scores = dates.find("span", attrs = {"class":"js-score"}).text
            name = dates.find("h2", attrs = {"class": "h2_anime_title"}).text
            for x in (dates.find_all("span", attrs = {"class": "genre"})):
                c.append((x.text).strip("\n"))
            genre.append((c))
            links.append(dates.find("a").get("href"))
            date.append(day)
            score.append(scores)
            titles.append(name)
            txt = str(dates.find("img"))
            temp = re.findall("[a-z]+[!-@]+[a-z]+[!-@]+[a-z]+[!-@]+[a-z]+[!-@]+[a-z]+[!-@]+[a-z]+[!-@]+[0-9]+[!-@]+[0-9]+[!-@]+[a-z]+", txt)

            images.append(temp[0])

        df["name"] = titles
        df["genre"] = genre
        df["date"] = date
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d-%m-%Y")
        df["score"] = score
        df["images"] =images
        df["links"] = links
        df["episode"] = episode

        driver.close()
        df = df.sort_values(by = ["score"], ascending = False)
        #Checking and dropping animes that have started before the current season years
        for index in (df.index):
            temp = int(str(df["date"][index]).split("-")[2])
            if(temp >= int(szn[1])):
                pass
            else:
                df = df.drop(index)
        #stores the unique genre values
        trim = list(df["genre"])
        temp_list = []
        for i in range(len(trim)):
            for num in (trim[i]):
                temp_list.append(num)
        trim = list(dict.fromkeys(temp_list))

        return render_template("anime_result.html" , episode = list(df["episode"]), szn = szn, names = list(df["name"]), date = list(df["date"]), score = list(df["score"]), images = list(df["images"]), links = list(df["links"]), genre = list(df["genre"]), trim = trim)

    return render_template("anime.html")

@app.route("/anime")
def anime ():
    return render_template("anime_sort.html")

if __name__ =="__main__":
    app.run(debug = True)
