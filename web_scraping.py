import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
base_link = "https://www.themoviedb.org/tv"

def get_page_content(url):
    get_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    response_page = requests.get(url, headers = get_headers )
    if not response_page.ok:
        raise Exception ("Failed to request the data. Status Code:- {}".format(response_page.status_code))
    else:
        page_content = response_page.text
        doc_page = BeautifulSoup(page_content, "html.parser")
        return doc_page
    
    
def empty_dict():
    scraped_dict = {  
                    'Title': [],
                    'User_rating': [], 
                    'Release_date':[], 
                    'Current_season': [],
                    # 'Total_episodes': [], 
                    'Tagline': [],
                    'Genre': [],
                    'Cast': [],
                    'Description': []   
                    }
    return scraped_dict

def user_score_info(tag_user_score, i, scraped_dict):
    if tag_user_score[i]['data-percent'] == '0':
        scraped_dict['User_rating'].append('Not rated yet')
    else:
        scraped_dict['User_rating'].append(tag_user_score[i]['data-percent'])
        
def get_show_info(doc_page):
    base_link_1 = "https://www.themoviedb.org"
    tag_title = tag_shows_page = doc_page.find_all('div', {'class': 'card style_1'})
    tag_user_score = doc_page.find_all('div', {"user_score_chart"}) 
    
    doc_2_list = []
    for link in tag_shows_page:
        doc_2_list.append(get_page_content(base_link_1 + link.h2.a['href']))
    return tag_title, tag_user_score, doc_2_list
        
def get_genres(doc2_page, i):
    genres_tags = doc2_page[i].find('span', {"class": "genres"}).find_all('a')
    check_genre =[]
    
    for tag in genres_tags:
        check_genre.append(tag.text)
    return check_genre
def tagline_info(doc_2_list, i, scraped_dict):
    if doc_2_list[i].find('h3',{"class": 'tagline'}):
        scraped_dict['Tagline'].append(doc_2_list[i].find('h3',{"class": 'tagline'}).text)
    else:
        scraped_dict['Tagline'].append("No Tagline")
        
def get_show_cast(doc2_page, i):
    cast_tags = doc2_page[i].find_all('li', {'class': 'card'})
    cast_lis = []
    
    for t in cast_tags:
         cast_lis.append(t.p.text)
    
    return cast_lis

    

def get_show_details(t_title, t_user_score, docs_2_list):
    scraped_dict =  empty_dict()
    for i in range (0, len(t_title)):
        scraped_dict['Title'].append(t_title[i].h2.text)
        user_score_info(t_user_score, i, scraped_dict)    
        scraped_dict['Release_date'].append(t_title[i].p.text)
        scraped_dict['Current_season'].append(docs_2_list[i].find_all('div' , {'class': 'flex'})[1].h2.text)
        # scraped_dict['Total_episodes'].append(docs_2_list[i].find_all('div' , {'class': 'flex'})[1].h4.text[7:])
        tagline_info(docs_2_list, i, scraped_dict)  
        scraped_dict['Genre'].append(get_genres(docs_2_list, i))        
        scraped_dict['Cast'].append(get_show_cast(docs_2_list, i))
        scraped_dict['Description'].append(docs_2_list[i].find('p').text)
        
    return pd.DataFrame(scraped_dict)

def create_page_df( i, dataframe_list):
    os.makedirs('shows-data', exist_ok = True)
    next_url = base_link + '?page={}'.format(i)
    doc_top = get_page_content(next_url)
    name_tag, viewer_score_tag, doc_2_lis = get_show_info(doc_top)
    print('scraping page {} :- {}'.format(i, next_url))
    dataframe_data = get_show_details(name_tag, viewer_score_tag, doc_2_lis)
    dataframe_data.to_csv("shows-data/shows-page-{}.csv".format(i) , index = None)
    print(" ---> a CSV file with name shows-page-{}.csv has been created".format(i))
    dataframe_list.append(dataframe_data)
    
def scrape_top_200_shows(base_link):
    dataframe_list = []
    for i in range(341,501):
        create_page_df(i, dataframe_list)
    total_dataframe = pd.concat(dataframe_list, ignore_index = True)
    
    csv_complete =  total_dataframe.to_csv('shows-data/Total-dataframe.csv', index= None)
    print(" \n a CSV file named Total-dataframe.csv with all the scraped shows has been created")


scrape_top_200_shows(base_link) 