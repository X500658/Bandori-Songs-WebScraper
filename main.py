import requests
from bs4 import BeautifulSoup
import re
import getch
import csv
from datetime import datetime

start=datetime.now()
# https://oxylabs.io/blog/python-web-scraping
# url = 'https://oxylabs.io/blog'

url='https://bandori.fandom.com/wiki/Track_List'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
song_list = soup.find('div', {"class":'mw-parser-output'})

orig_or_cover=''
song_type=''
song_name=''
band=''
source_artist=''
source_media=''
total=0
count=0
lenset=set()
vocaloids=['Hatsune Miku', 'GUMI', 'IA', 'flower', 'LIP×LIP', 'Kagamine Rin', 'Megurine Luka', 'Kagamine Rin & Len', 'Hatsune Miku and GUMI']
# add these to artist instead of media

with open('dori scrape.csv', 'w', newline='',  encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=['Originality', 'Song Type', 'Name', 'Band', 'Source Artist', 'Source Media'])
    writer.writeheader()
    # writer = csv.writer(csvfile, delimiter=';')
    # writer.writerow(['Originality', 'Song Type', 'Name', 'Band', 'Source Artist', 'Source Media'])

    for child in song_list.children:
        if(str(type(child)) not in ["<class 'bs4.element.NavigableString'>", "<class 'bs4.element.Comment'>"]\
            and child.name not in ['p', 'div'] and not (child.name=='h2' and child.span.contents[0]=='Navigation')\
            and not (child.name=='table' and str(child.attrs)=="{'class': ['navbox'], 'cellspacing': '0', 'style': ';'}")):
            if(re.search('h2', child.name)):
                orig_or_cover=((child.span.contents[0]).rstrip())[:-6]
                song_type=''
            if(re.search('h3', child.name)):
                if(len(child.contents)==1):
                    song_type=child.span.contents[0][:-6]
                else:
                    song_type=child.contents[1].contents[0][:-6]
            if(re.search('table', child.name)):
                rows = child.find_all('tr')
                for index, row in enumerate(rows):
                    song_name=''
                    band=''
                    source_artist=''
                    source_media=''
                    if(index>0 and row.contents[3].contents[0] not in ['TBA\n', '二重の虹 (Full)']\
                        and row.contents[3].a is not None and not re.search("Upcoming", song_type)):
                        if(len(row.contents[1].b.contents)==1):
                            band=row.contents[1].b.contents[0]
                        else:
                            for i in row.contents[1].b.contents:
                                if(str(type(i))=="<class 'bs4.element.Tag'>"):
                                    band+=i.contents[0]
                                else:
                                    band+=i
                        if(re.search("＊", band)):
                            band=re.sub("＊", "*", band)
                        # lenset.add(len(row.contents[3].contents)) #3 TDs per TR
                        song_name=(row.contents[3].a.contents[0])
                        # song_name=(row.contents[3].a.contents[0]).encode('unicode-escape').decode().rstrip()
                        if re.search("Tie-Up", song_type):
                            source_artist=re.sub("\n", '', row.contents[5].contents[0])
                        elif re.search("Cover", orig_or_cover):
                            # lenset.add(len(row.contents[5].contents))
                            if len(row.contents[5].contents)==1:
                                if(re.search("\s\(", row.contents[5].contents[0])):
                                    x=row.contents[5].contents[0]
                                    x=x.split('(')
                                    for i in range(len(x)):
                                        x[i]=re.sub("\)\n", '',x[i])
                                        x[i]=x[i].rstrip()
                                    source_artist=x[0]
                                    if x[1] not in vocaloids:
                                        source_media=x[1]
                                    else:
                                        source_artist+=", "+x[1]
                                else:
                                    source_artist=row.contents[5].contents[0].rstrip()
                                # print(f'{str(source_artist):<40} | {source_media}')
                            if len(row.contents[5].contents)==2:
                                source_artist=row.contents[5].a.contents[0]
                                if(row.contents[5].contents[1]!='\n'):
                                    x=row.contents[5].contents[1]
                                    x=x.rstrip()
                                    x=x.lstrip()
                                    if(x[0]=='(' and x[-1]==')'):
                                        x=x[1:-1]
                                        # print(x)
                                        if x not in vocaloids:
                                            source_media=x
                                        else:
                                            source_artist+=", "+x
                                # print(f'{str(source_artist):<40} | {source_media}')
                            if len(row.contents[5].contents)==3:
                                x=row.contents[5]
                                source_artist=(re.sub("\(", "",x.contents[0])).rstrip()
                                x=(x.a.contents[0]).rstrip()
                                if x not in vocaloids:
                                    source_media=x
                                else:
                                    source_artist+=", "+x
                                # print(f'{str(source_artist):<60} | {source_media}')
                            if len(row.contents[5].contents)==4:
                                source_artist=(row.contents[5].contents[0].contents[0]).rstrip()
                                x=row.contents[5].contents[2].contents[0].rstrip()
                                # print(f'{str(source_artist):<60} | {source_media}')
                            if len(row.contents[5].contents)==5:
                                x=row.contents[5]
                                source_artist=(re.sub(" \(", "", x.contents[0]).rstrip())
                                var=x.contents[1].contents
                                if len(var)>0:
                                    if var[0] not in vocaloids:
                                        if source_media=='':
                                            source_media=var[0]
                                        else:
                                            source_media+=", "+var[0]
                                    else:
                                        source_artist+=", "+var[0]
                                var=x.contents[3].contents[0]
                                # print(var)
                                if len(var)>0:
                                    if var not in vocaloids:
                                        if source_media=='':
                                            source_media=var
                                        else:
                                            source_media+=", "+var
                                    else:
                                        source_artist+=", "+var
                                # print(f'{str(source_artist):<60} | {source_media}')
                            # if len(row.contents[5].contents)==6:
                                # print(row.contents[5].contents)
                            if len(row.contents[5].contents)==7:
                                x=row.contents[5]
                                source_artist=(re.sub(" \(", "", x.contents[0]).rstrip())
                                for i in [1, 3, 5]:
                                    y=x.contents[i].contents[0]
                                    # print(x.contents[i].contents[0])
                                    if y not in vocaloids:
                                        if source_media=='':
                                            source_media=y
                                        else:
                                            source_media+=", "+y
                                    else:
                                        source_artist+=", "+y
                        else:
                            source_artist=''
                            source_media=''
                    if all(v!="" for v in [song_name, band]):
                        count=count+1
                        # print(f'{orig_or_cover:<8} | {song_type[:16]:<16} | {song_name[:30]:<30} | {band[:30]:<30} | {source_artist[:50]:<50} | {source_media[:55]:<55} |')
                        writer.writerow({'Originality':orig_or_cover,'Song Type':song_type, 'Name':song_name, 'Band':band, 'Source Artist':source_artist, 'Source Media':source_media})
                        # 'Originality', 'Song Type', 'Name', 'Band', 'Source Artist', 'Source Media'
                total=total+len(rows)
print(f'Bandori has {total} songs in total but this only has {count} songs')
print (f'Program execution: {datetime.now()-start}')
# print(lenset)
