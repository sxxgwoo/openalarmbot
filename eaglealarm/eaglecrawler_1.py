#step1.라이브러리 불러오기
from logging import NOTSET
import requests
from bs4 import BeautifulSoup as bs
import schedule
import time
import re

import os
import json

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
class news:
    def __init__(self,query,id):
        self.query=query
        self.id=id       
          
    def preprocessing(self): #괄호 솎아내기
        string1 =''
        string2 =''
        starstring3=[]
        par=[]
        par_nostar=[]
        par_star=[]
        k=0
        global note
        note=[]

        for i in range(len(self.query)):
            if '(' == self.query[i]:
                while True:
                    if k <i:
                        k+=1
                    else:
                        string1 += self.query[k]
                        k +=1
                        if self.query[k] ==')' and k+1 != len(self.query):
                            k+=1
                            if self.query[k] == '*':
                                string1 +=self.query[k-1]+self.query[k]+self.query[k+1]+' '
                                k+=1
                                starstring3.append(1)
                                break
                            else:
                                string1 += self.query[k-1]+' '
                                starstring3.append(0)
                                break
                        elif self.query[k]==')' and k+1==len(self.query):
                            string1 += self.query[k]
                            starstring3.append(0)
                            break
                        else:
                            pass
            elif i <= k and i!=0:
                pass
            else:
                string2 += self.query[i]
        par = re.findall('\(([^)]+)', string1)
        note.append(string2.split())       #문자열 공백기준으로 리스트에 넣기 
        countstar = [i for i in range(len(starstring3)) if 1 == starstring3[i]]
        count = [i for i in range(len(starstring3)) if 0 == starstring3[i]]
        
        for s in countstar:
            par_star.append(par[s])
        for s in count:
            par_nostar.append(par[s])

        return par_star,par_nostar, note

    def star_detection(self):
        nostar=[]
        star_extract=[]
        star_except=[]
        ne=news(self.query,self.id)
        par_star, par_nostar, note = ne.preprocessing()
        if len(note[0]) == ' '.join(note[0]).count('**'):                     #키워드에 **만 있는 경우
            for t in range(len(note[0])):
                nostar.append(note[0][t].replace('**',''))
                star_extract.append(note[0][t].replace('**',''))
        else:                                                                 #키워드에 여러가지 섞여있는 경우                                                      
            if ' '.join(note[0]).count('**') ==0:                                 #키워드에 **이 없는경우
                nostar=note[0]
            else:                                                                 #키워드에 **이 하나이상있는 경우
                for t in range(len(note[0])):
                    if '**' in note[0][t]:
                        if '-' in note[0][t]:
                            star_except.append(note[0][t].replace('**','').replace('-',''))
                        elif '+' in note[0][t]:
                            star_extract.append(note[0][t].replace('**','').replace('+',''))
                        else:
                            star_extract.append(note[0][t].replace('**',''))
                    else:
                        nostar.append(note[0][t])
                if len(nostar)== ' '.join(nostar).count('-')+' '.join(nostar).count('+'):       #nostar에 - 또는 +만 있는 경우 
                    nostar = star_extract + nostar
                else:
                    pass

        return nostar, star_extract, star_except

    def news_list(self):
        try:
            ne=news(self.query,self.id)
            nostar,star_extract ,star_except  = ne.star_detection()
            key=''
            for k in range(len(nostar)):
                if "+" in nostar[k]:                                     # %20%2B{self.query} 포함
                    t = nostar[k].replace('+','').replace(' ','%20')
                    key += f'%20%2B{t}'
                elif "-" in nostar[k]:                                   # %20-{self.query} 제외
                    t = nostar[k].replace(' ','%20')
                    key += f'%20{t}'
                elif "|" in nostar[k]:                                   # %20%7C%20{self.query} 하나이상
                    t = nostar[k].replace('|','').replace(' ','%20')
                    key += f'%20%7C%20{t}'
                elif '"' in nostar[k]:                                   # %20"{self.query}" 정확한 단어검색
                    t = nostar[k].replace(' ','%20')
                    key += f'%20{t}'
                else:                                                       # 나머지 공백은 %20으로 치환
                    t = nostar[k].replace(' ','%20')
                    key += f'%20{t}'
            # (주의) 네이버에서 키워드 검색 - 뉴스 탭 클릭 - 최신순 클릭 상태의 url
            headers ={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
            
            url = f'https://search.naver.com/search.naver?where=news&query={key}&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0'
            
            # html 문서 받아서 파싱(parsing)
            response = requests.get(url,headers=headers)
            soup = bs(response.text , 'html.parser')

            # 해당 페이지의 뉴스기사 링크가 포함된 html 요소 추출
            titles = soup.select('a.news_tit')

            # 요소에서 링크만 추출해서 리스트로 저장
            news_links = [i.attrs['href'] for i in titles]

            # 요소에서 제목만 추출해서 리스트로 저장
            news_titles =  [i.get_text() for i in titles]

            #딕셔너리 형태로 제목+링크 저장
            news_titles_links={}
            for i in range(len(titles)):
                news_titles_links[i]=[news_titles[i],news_links[i]]
            
            if os.path.exists('./data/newsdata_'+str(self.id)+'.json'):
                with open('./data/newsdata_'+str(self.id)+'.json','r',encoding="UTF-8") as json_file:
                    json_data = json.load(json_file)
            else:
                json_data={'0':[[],[],[]]}

            #모든 기사 합치기
            newsdata=[]
            for i in range(len(json_data)):
                newsdata.extend(json_data[list(json_data.keys())[i]][0])
                newsdata.extend(json_data[list(json_data.keys())[i]][2])
                
            # 기존의 링크와 신규 링크를 비교해서 새로운 링크만 저장
            t=0
            new_links={}
            for i in range(len(news_titles_links)):
                if news_titles_links[i][0] not in newsdata:
                    new_links[t]=news_titles_links[i]
                    t+=1
                else:
                    pass
        except:
            new_links={}
            new_links[0]=['blocking','blocking']

        return new_links

    # 특정키워드 "제목"에 모두 포함된것
    def title_extract(self,*args):
        ne = news(self.query,self.id)
        news_titles_links = ne.news_list()
        extract_titles={}
        k=0
        if len(args) !=0:
            for i in range(len(news_titles_links)):
                found_count = len([x for x in args if x in news_titles_links[i][0]])
                if len(args)== found_count:
                    extract_titles[k]=news_titles_links[i]
                    k+=1
                else:
                    pass
        else:
            pass
        return extract_titles

    # 특정키워드 "제목"에서 제외된것
    def title_word_except(self,*args):
        ne = news(self.query,self.id)
        news_titles_links = ne.news_list()
        except_titles ={}
        q=0
        for i in range(len(news_titles_links)): 
            for k in args:
                if k not in news_titles_links[i][0]:    
                    except_titles[q]=news_titles_links[i]
                    q+=1
                else:
                    pass
        x = [] # 처음 등장한 값인지 판별하는 리스트
        new_a = {} # 중복된 원소만 넣는 리스트
        t=0
        if len(args)>1:
            for i in range(len(except_titles)):
                if except_titles[i][0] not in x: # 처음 등장한 원소
                    x.append(i)
                else:
                    if except_titles[i][0] not in new_a: # 이미 중복 원소로 판정된 경우는 제외
                        new_a[t]=except_titles[i]
                        t+=1
                    else:
                        pass
        else:
            new_a = except_titles #.copy() 확인
        return new_a

    def title_word_or(self,*args): #키워드 제목 or
        ne = news(self.query,self.id)
        news_titles_links = ne.news_list()
        or_titles={}
        q=0
        for i in range(len(news_titles_links)):
            for k in args:
                global s
                s=[]
                s.extend(k.replace('|','').split())
                for n in s:
                    if n in news_titles_links[i][0]:    
                        or_titles[q]=news_titles_links[i]
                        q+=1
                    else:
                        pass

        x = {} # 처음 등장한 값인지 판별하는 리스트
        t=0
        if len(args)>=1:
            for i in range(len(or_titles)):
                if or_titles[i][0] not in x: # 처음 등장한 원소
                    x[t]=or_titles[i]
                    t+=1
                else:
                    pass
        else:
            x = or_titles

        return x


def classify(query,id):
    newalarm=[]
    alarm = news(query,id)
    par_star,par_nostar, note = alarm.preprocessing()
    nostar, star_extract, star_except = alarm.star_detection()
    newslink1 = alarm.news_list()
    newslink2 = alarm.title_extract(*star_extract)
    newslink3 = alarm.title_word_except(*star_except)
    newslink4 = alarm.title_word_or(*par_star)

    if len(star_extract)>0:
        if len(star_except)==0:
            if len(par_star)==0:
                newalarm = [newslink2[i] for i in range(len(newslink2))]
            else:
                newalarm = [newslink4[i] for i in range(len(newslink4)) if newslink4[i][0] in newslink2[i][0]]
        else:
            if len(par_star)==0:
                newalarm = [newslink2[i] for i in range(len(newslink2)) if newslink2[i][0] in newslink3[i][0]]
            else:
                newalarm = [newslink2[i] for i in range(len(newslink2)) if newslink2[i][0] in newslink3[i][0] if newslink2[i][0] in newslink4[i][0]]
    else:
        if len(star_except)==0:
            if len(par_star)==0:
                newalarm = [newslink1[i] for i in range(len(newslink1))]
            else:
                newalarm = [newslink4[i] for i in range(len(newslink4))]
        else:
            if len(par_star)==0:
                newalarm = [newslink3[i] for i in range(len(newslink3))]
            else:
                newalarm = [newslink3[i] for i in range(len(newslink3)) if newslink3[i][0] in newslink4[i][0]]
    
    return newalarm


def name():
    ids=[]
    file_list_json=[]
    path = "./data/"
    file_list = os.listdir(path)
    for file in file_list:
        if file.endswith('.json'):
            if 'news' not in file:
                if 'data_' in file:
                    file_list_json.append(file)
                else:
                    pass
            else:
                pass
        else:
            pass
    for i in range(len(file_list_json)):
        ids.append(int(file_list_json[i].replace('data_','').replace('.json','')))
 
    return ids

 
#계속 감지
def main():
    ids= name()
    if len(ids)>0:
        for id in ids:
            if os.path.exists('./data/data_'+str(id)+'.json'):
                with open('./data/data_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
                    json_data = json.load(json_file)
                    if len(json_data)>0:                        # 키워드 10개 이상일경우
                        for q in range(0,len(json_data)//2):
                            query=json_data[str(q+1)][0]
                            alarm = news(query,id)
                            new_links = alarm.news_list()
                            newalarm = classify(query,id) #최종 기사
                            if len(new_links)>0:   #기본 검색의 새로운 기사가 있으면 실행
                                for i in range(len(newalarm)):
                                    #oldlinks 저장
                                    if os.path.exists('./data/newsdata_'+str(id)+'.json'):
                                        with open('./data/newsdata_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
                                            json_newsdata = json.load(json_file)
                                        lists=[]
                                        for s in range(len(json_newsdata)):
                                            lists.append(list(json_newsdata.keys())[s])
                                        if query not in lists:
                                            json_newsdata[query]=[[newalarm[len(newalarm)-1-i][0]],[newalarm[len(newalarm)-1-i][1]],[]]
                                        else:
                                            json_newsdata[query][0].append(newalarm[len(newalarm)-1-i][0])
                                            json_newsdata[query][1].append(newalarm[len(newalarm)-1-i][1])

                                        with open('./data/newsdata_'+str(id)+'.json','w',encoding="UTF-8") as f:
                                            json.dump(json_newsdata,f,ensure_ascii=False,indent=4)
                                    else:
                                        test={}
                                        test[query]=[[newalarm[len(newalarm)-1-i][0]],[newalarm[len(newalarm)-1-i][1]],[]]
                                        with open('./data/newsdata_'+str(id)+'.json','w',encoding="UTF-8") as f:
                                            json.dump(test,f,ensure_ascii=False,indent=4)
                            else:
                                pass
                    else:                                       #키워드가 없는경우
                        pass
            else:
                pass
    else:
        pass        


#  실제 프로그램 구동
if __name__ == '__main__':
    
    schedule.every(1).seconds.do(main)
    
    while  True:
        schedule.run_pending()
        time.sleep(1)

    
    # t=0
    # while True:
    #     if t<5:
    #         start = time.time()
    #         main()
    #         end = time.time()
    #         print(f'time taken: {end-start}')
    #         t+=1
    #     else:
    #         break   
    

 

    