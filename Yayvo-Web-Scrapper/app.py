from bs4 import BeautifulSoup as soup
import urllib
import requests
import pandas as pd
import time
import os
from flask import Flask, render_template,  session, redirect, request
from flask_cors import CORS,cross_origin
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# define global paths for Image and csv folders
IMG_FOLDER = os.path.join('static', 'images')
CSV_FOLDER = os.path.join('static', 'CSVs')

app = Flask(__name__)
app.config['IMG_FOLDER'] = IMG_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

class DataCollection:
    def __init__(self):
        self.data = { 
		"Name": list(),
		"Old Price (PKR)": list(),
        "Regular Price (PKR)": list(),
        "Special Price (PKR)": list(),
        "Discount %": list(),
        "Brand Name": list()}
    
    def get_final_data(self, commentbox=None,i=None):
        
        try:
            Row = commentbox.find_all("li", {"class":"item"})
            self.data["Name"].append(Row[i].a.img["alt"])
        except:
            self.data["Name"].append("No name")
        try:
            #page_soup.find_all("p",{"class":"old-price"})
            self.data["Old Price (PKR)"].append(commentbox.find_all("p",{"class":"old-price"})[i].get_text().strip())
            #self.data["Old Price (PKR)"].append("Amin")
        except:
            self.data["Old Price (PKR)"].append('0')
        try:
            
            self.data["Regular Price (PKR)"].append(commentbox.find_all("span",{"class":"price"})[i].get_text().strip())
            #self.data["Regular Price (PKR)"].append("Fatima")
        except:
            self.data["Regular Price (PKR)"].append('0')
        try:
            
            self.data["Special Price (PKR)"].append(commentbox.find_all("p",{"class":"special-price"})[i].get_text().strip())
            #self.data["Special Price (PKR)"].append("Mahira")
        except:
            self.data["Special Price (PKR)"].append('0')
            
        try:
            
            self.data["Discount %"].append(commentbox.find_all("span",{"class":"discount_Span"})[i].get_text().strip())
            #self.data["Discount %"].append("Anas")
        except:
            self.data["Discount %"].append('0')    
        try:
            self.data["Brand Name"].append(commentbox.find_all("div",{"class":"cstm_brnd"})[i].get_text().strip())
            #self.data["Brand Name"].append("Siddiq")
        except:
            self.data["Brand Name"].append('none')
    
    def get_main_HTML(self, base_URL=None, search_string=None):
		# construct the search url with base URL and search string
        #http://yayvo.com/search/result/?q=samsung+mobiles
        search_url = f"{base_URL}/search/result/?q={search_string}"
		# usung urllib read the page
        with urllib.request.urlopen(search_url) as url:
            page = url.read()
		# return the html page after parsing with bs4
        return soup(page, "html.parser")
    
    def get_prod_HTML(self, productLink=None):
        prod_page = requests.get(productLink)
        return soup(prod_page.text, "html.parser")
    
    def get_data_dict(self):
        return self.data
    
    def save_as_dataframe(self, dataframe, fileName=None):
        csv_path = os.path.join(app.config['CSV_FOLDER'], fileName)
        fileExtension = '.csv'
        final_path = f"{csv_path}{fileExtension}"
		# clean previous files -
        CleanCache(directory=app.config['CSV_FOLDER'])
        # save new csv to the csv folder
        dataframe.to_csv(final_path, index=None)
        print("File saved successfully!!")
        return final_path
    
class CleanCache:
	'''
	this class is responsible to clear any residual csv and image files
	present due to the past searches made.
	'''
	def __init__(self, directory=None):
		self.clean_path = directory
		# only proceed if directory is not empty
		if os.listdir(self.clean_path) != list():
			# iterate over the files and remove each file
			files = os.listdir(self.clean_path)
			for fileName in files:
				print(fileName)
				os.remove(os.path.join(self.clean_path,fileName))
		print("cleaned!")

# route to display the home page
@app.route('/',methods=['GET'])  
@cross_origin()
def homePage():
	return render_template("index.html")

@app.route('/review', methods=("POST", "GET"))
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            base_URL = 'https://www.yayvo.com'
            #search_string = 'samsung mobiles'
            search_string = request.form['content']
        
            search_string = search_string.replace(" ", "+")
            print('processing, Please wait')
            start = time.perf_counter()
            get_data = DataCollection()
            
            yayvo_HTML = get_data.get_main_HTML(base_URL, search_string)
            print(len(yayvo_HTML))
            
            
            
            #get_data.get_final_data(yayvo_HTML)
            i=0
            #prod_title = []
            while (i <= len(yayvo_HTML)-1):
                #prod_title.append(yayvo_HTML[i].a.img["alt"])
                get_data.get_final_data(yayvo_HTML,i)
                i=i+1
            
            yayvo_Scrapped = pd.DataFrame(get_data.get_data_dict())
            yayvo_Scrapped = yayvo_Scrapped.head(51)
            print("---------chkinggg -------------")
            print(yayvo_Scrapped.head())
            
            download_path = get_data.save_as_dataframe(yayvo_Scrapped, fileName=search_string.replace("+", "_"))
            finish = time.perf_counter()
            print(f"program finished with and timelapsed: {finish - start} second(s)")
            
            return render_template('review.html', 
			tables=[yayvo_Scrapped.to_html(classes='data')], # pass the df as html 
			titles=yayvo_Scrapped.columns.values, # pass headers of each cols
			search_string = search_string, # pass the search string
			download_csv=download_path # pass the download path for csv
			)
            
        except Exception as e:
            print(e)
            return render_template("404.html")
    else:
        return render_template("index.html")

if __name__ == '__main__':
	app.run() 
            
            
            
            






















