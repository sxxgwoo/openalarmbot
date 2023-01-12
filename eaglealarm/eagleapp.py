#step1.라이브러리 불러오기
from logging import NOTSET
import requests
from bs4 import BeautifulSoup as bs
import schedule
import time
import re
from collections import deque

import os
import json

import logging
from telegram import Update
from telegram.ext import JobQueue, filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def contexts(id):
    text_context=''
    if os.path.exists('./data/data_'+str(id)+'.json'):
        with open('./data/data_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
            json_data = json.load(json_file)
            for k in range(len(json_data)):
                text_context += '[ '+str(k+1)+' ]'+json_data[str(k+1)][0]+'\n'
    else:
        pass
    return text_context


#new command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username =update.message.chat.first_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F604 '+str(username) +'님 안녕하세요 뉴스알림봇 독수리\U0001F985입니다.')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='먼저 키워드를 설정 해주세요!')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F9D0 도움이 필요할때는 /help를 입력해주세요!')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text="""[ 도움말 ]
 
 1. 키워드 편집
 현재 목록에 없는 키워드를 입력하면 추가되고,
 키워드를 삭제할 때는 현재 목록에서의 번호를 아래와 같이 /delete 명령어 뒤에 붙이면 됩니다.
 /delete 지우려는 키워드 번호
 
 상세검색을 위한 연산자 활용은 아래 [상세검색 연산자] 항목을 확인하세요.
 
 2. 키워드 초기화
 입력창에 초기화!를 입력하면 저장된 키워드가 모두 삭제됩니다.
 
 3. 뉴스 알림주기 설정
 설정: /set 설정할 알림주기(단위: 초)
 해제: /unset

 [ 상세검색 연산자 ]
 
 1. 정확히 일치하는 단어/문장 (연산자 “ ” )
 입력한 단어/문장이 순서대로 정확하게 일치하는 문서를 검색하도록 조건을 설정합니다.
 [예시] 책 "아동 심리학"
 
 2. 반드시 포함하는 단어 (연산자 + )
 입력한 단어를 모두 포함하는 문서를 검색하도록 조건을 설정합니다.
 [예시] 삼성전자 +카카오 +주가
 
 3. 제외하는 단어 (연산자 - )
 입력한 단어가 포함된 문서는 검색결과에서 제외하도록 조건을 설정합니다.
 [예시] 유럽배낭여행 -런던
 
 4. 단어 중 하나 이상 포함 (연산자 | )
 연산자 앞/뒤로 입력한 단어가 하나 이상 포함된 문서를 검색하도록 조건을 설정합니다.
 [예시] 날씨 오늘 | 내일 | 주말
 
 5. 키워드를 포함하는 제목의 기사만 검색 (연산자 **)
 키워드 입력할 때 마지막에 **를 붙이면, 제목에 키워드를 하나라도 포함하는 기사만 알림을 보내도록 필터를 설정합니다.
 [예시] 삼성전자 +주가**, 카카오**
 
 6. 복수 키워드 중 하나 이상 기사 제목에 포함 (keyword1 | keyword2)**
  [예시] 코로나 (확진자 | 트렌드)**"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id=update.effective_chat.id
    data={}
    if os.path.exists('./data/data_'+str(id)+'.json'):
        with open('./data/data_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
                    json_data = json.load(json_file)
        if os.path.exists('./data/newsdata_'+str(id)+'.json'):
            with open('./data/newsdata_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
                        json_newsdata = json.load(json_file)
        else:
            pass

        if len(json_data) >= len(context.args)>0:
            if os.path.exists('./data/newsdata_'+str(id)+'.json'):
                deletelist=[]
                for k in range(len(json_newsdata)):
                    deletelist.append(list(json_newsdata.keys())[k])
                if json_data[context.args[0]][0] in deletelist:
                    json_newsdata.pop(json_data[context.args[0]][0])
                else:
                    pass
            else:
                pass
            json_data.pop(context.args[0])
            # 중간에 삭제한 목록 번호 밀기
            for s in range(len(json_data)):
                if int(context.args[0])<=s+1:
                        data[s+1]=json_data[str(s+2)]
                else:
                        data[s+1]=json_data[str(s+1)]

            if os.path.exists('./data/newsdata_'+str(id)+'.json'):
                with open('./data/newsdata_'+str(id)+'.json','w',encoding="UTF-8") as f:
                    json.dump(json_newsdata,f,ensure_ascii=False,indent=4)
            else:
                pass    
            with open('./data/data_'+str(id)+'.json','w',encoding="UTF-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=4)
            text_context = contexts(id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args[0]+'번째 키워드 삭제 완료!\n'+'\U0001F4D5 현재 키워드 목록 \U0001F4D5\n'+text_context)
        else:
            text_context = contexts(id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F4D5  삭제할 키워드를 선택해주세요  \U0001F4D5\n'+text_context)
    else:
        text_context = contexts(id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F4D5  삭제할 키워드가 없습니다.  \U0001F4D5\n'+text_context)



async def set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args)>0:
        id=update.effective_chat.id
        if os.path.exists('./data/newsdata_'+str(id)+'.json'):       #새로운 set 들어오면 쌓인 데이터 정리 다시시작
            os.remove('./data/newsdata_'+str(id)+'.json')
        else:
            pass
        to_remove = context.job_queue.get_jobs_by_name(name=str(update.effective_chat.id))
        if len(to_remove)>0:
            for i in to_remove:
                i.schedule_removal()
            await context.bot.send_message(chat_id=update.effective_chat.id, text='뉴스 알림주기 설정완료! \n\U0001F916지금부터 '+context.args[0]+'초마다 알려드릴게요!')
            await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F4A5 기존에 설정된 값은 삭제되었습니다!')
            context.job_queue.run_repeating(newsalarm,interval=int(context.args[0]),name=str(update.effective_chat.id),chat_id=update.effective_chat.id)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='뉴스 알림주기 설정완료! \n\U0001F916지금부터 '+context.args[0]+'초마다 알려드릴게요!')
            context.job_queue.run_repeating(newsalarm,interval=int(context.args[0]),name=str(update.effective_chat.id),chat_id=update.effective_chat.id)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='/set 알림주기 설정해주세요(단위:초)')
    

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    to_remove = context.job_queue.get_jobs_by_name(name=str(update.effective_chat.id))
    for i in to_remove:
        i.schedule_removal()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F47B 뉴스 알람이 해제되었습니다. \U0001F47B')
#텍스트 입력됐을때
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text=='초기화!':
        to_remove = context.job_queue.get_jobs_by_name(name=str(update.effective_chat.id))
        for i in to_remove:
            i.schedule_removal()
        id =update.message.chat_id
        if os.path.exists('./data/data_'+str(id)+'.json'):
            os.remove('./data/data_'+str(id)+'.json')
        else:
            pass
        if os.path.exists('./data/newsdata_'+str(id)+'.json'):
            os.remove('./data/newsdata_'+str(id)+'.json')
        else:
            pass
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F607  계정이 초기화 되었습니다! \U0001F607')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='[전체알림] "'+user_text+'" 추가완료!')

        id =update.message.chat_id
        #json파일로 저장
        if os.path.exists('./data/data_'+str(id)+'.json'):
            with open('./data/data_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
                json_data = json.load(json_file)
            tur = len(json_data)
            json_data[str(tur+1)]=[user_text]
            data=[]
            order_data={}
            for i in range(len(json_data)):
                data.append(json_data[str(i+1)][0])
            sort_data=sorted(data)
            for k in range(len(sort_data)):
                order_data[str(k+1)]=[sort_data[k]]
            with open('./data/data_'+str(id)+'.json','w',encoding="UTF-8") as f:
                json.dump(order_data,f,ensure_ascii=False,indent=4)
        else:
            test={}
            test['1']=[user_text]
            with open('./data/data_'+str(id)+'.json','w',encoding="UTF-8") as f:
                json.dump(test,f,ensure_ascii=False,indent=4)
        
        text_context = contexts(id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='\U0001F4D5 현재 키워드 목록 \U0001F4D5\n'+text_context)

async def newsalarm(context: ContextTypes.DEFAULT_TYPE):
    id=context.job.chat_id
    if os.path.exists('./data/newsdata_'+str(id)+'.json'):
        with open('./data/newsdata_'+str(id)+'.json','r',encoding="UTF-8") as json_file:
            json_newsdata = json.load(json_file)

        for i in range(len(json_newsdata)):
            if len(json_newsdata[list(json_newsdata.keys())[i]][0])>0:
                await context.bot.send_message(chat_id=context.job.chat_id, text='\U0001F4A5 [ '+str(list(json_newsdata.keys())[i])+' ] 새로운 뉴스 '+str(len(json_newsdata[list(json_newsdata.keys())[i]][0]))+'건 \U0001F4A5')
                for k in range(len(json_newsdata[list(json_newsdata.keys())[i]][0])):
                        await context.bot.send_message(chat_id=context.job.chat_id, text='[ '+str(list(json_newsdata.keys())[i])+' ]'+'에 대한 검색\n'+json_newsdata[list(json_newsdata.keys())[i]][0][k]+'\n'+json_newsdata[list(json_newsdata.keys())[i]][1][k])
                if len(json_newsdata[list(json_newsdata.keys())[i]][2])<10:
                    json_newsdata[list(json_newsdata.keys())[i]][2]+=json_newsdata[list(json_newsdata.keys())[i]][0]
                    json_newsdata[list(json_newsdata.keys())[i]][0]=[]
                    json_newsdata[list(json_newsdata.keys())[i]][1]=[]
                else:
                    queue = deque(json_newsdata[list(json_newsdata.keys())[i]][2])
                    for t in range(len(json_newsdata[list(json_newsdata.keys())[i]][0])):
                        queue.append(json_newsdata[list(json_newsdata.keys())[i]][0][t])
                        queue.popleft()
                    json_newsdata[list(json_newsdata.keys())[i]][2]=list(queue)
                    json_newsdata[list(json_newsdata.keys())[i]][0]=[]
                    json_newsdata[list(json_newsdata.keys())[i]][1]=[]
                with open('./data/newsdata_'+str(id)+'.json','w',encoding="UTF-8") as f:
                    json.dump(json_newsdata,f,ensure_ascii=False,indent=4)
            else:
                pass
    else:
        pass
    

def main():

    application = ApplicationBuilder().token('Your bot ID').build() # 독수리 봇
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('del', delete))
    application.add_handler(CommandHandler('set', set))
    application.add_handler(CommandHandler('unset', unset))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    application.run_polling()

#  실제 프로그램 구동
if __name__ == '__main__':
    main()
 
    