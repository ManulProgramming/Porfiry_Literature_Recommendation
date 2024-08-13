import customtkinter as ctk
import re
from random import choice, random
from tkinter import Canvas, Frame, Text, Scrollbar, VERTICAL, WORD, Label, END
from PIL import Image, ImageTk
import os
from datetime import datetime
import getpass
error=""
try:
    from sklearn.metrics.pairwise import cosine_similarity
    import pandas as pd
    from sklearn.feature_extraction.text import CountVectorizer
except Exception as gg:
    error="LibraryError"

time_it_takes_to_see_the_message=500 #500
time_it_takes_to_respond=1500 #1500

welcome="Добрый вечер"
what_message_to_add="Ваш запрос мне не ясен, проверьте правильность написания команды."
botimg=0
prev_message=""
remove_extra=0
recommendation_Mode=0
prev_user_message=""
def add_message(message, sender):
    global prev_message, remove_extra, prev_user_message
    chat_text.config(state="normal")
    chat_text.insert("end","\n")
    if sender=='Bot':
        prev_message=message
        chat_text.image_create(END, image = allbotimgs[botimg])
        chat_text.insert("end", f"\n\n{message}\n\n")
    else:
        chat_text.delete(f"end-{9+remove_extra}l linestart", f"end-0l linestart")
        if recommendation_Mode!=0:
            if recommendation_Mode==1 and message.lower()!='найти':
                if prev_user_message=='':
                    prev_user_message=message
                else:
                    prev_user_message+=', '+message
            elif message.lower()=='найти' and prev_user_message=='':
                prev_user_message='найти'
            chat_text.insert("end", f"\n{prev_user_message}\n\n")
        else:
            prev_user_message=''
            chat_text.insert("end", f"\n{message}\n\n")
        chat_text.tag_configure("center", justify="center")
        chat_text.tag_add("center", "0.0", END)
        chat_text.tag_config("usermessage", foreground="#4286f4")
        chat_text.tag_add("usermessage", "0.0", "3.0")
        chat_text.image_create(END, image = allbotimgs[botimg])
        chat_text.insert("end", f"\n\n{prev_message}\n\n")
    chat_text.see("end")
    chat_text.config(state="disabled")
def remove_message():
    global remove_extra
    chat_text.config(state="normal")
    chat_text.delete(f"end-{6+remove_extra}l linestart", "end-1l linestart")
    chat_text.config(state="disabled")
user_message=""
count=None
fulldata=None
books_data=[]
def check_what(el,data,what):
    global count
    count_matrix=count.fit_transform(data[what].to_list()+[el])
    cosine_sim = cosine_similarity(count_matrix[-1], count_matrix[:-1])[0]
    sim_enum=list(enumerate(cosine_sim))
    return sorted(sim_enum,key=lambda x: x[1] ,reverse=True)
listofbooks=[]
sim_enum=None
datata=None
author=None
specbook=None
def bot_response1():
    global what_message_to_add, botimg, remove_extra, count, fulldata, recommendation_Mode, books_data, listofbooks, sim_enum, datata, author, specbook, prev_user_message
    remove_message()
    message_entry.configure(state='normal')
    message = user_message
    if recommendation_Mode!=0:
        message=message.replace('ё','е')
        if recommendation_Mode==1:
            if message.lower()=='найти':
                specbook=fulldata.loc[books_data]
                if specbook.empty:
                    recommendation_Mode=0
                    what_message_to_add='Вы вернулись в обычный режим. Введите «помощь», чтобы увидеть все доступные вам команды.'
                else:
                    fulldata_temp=fulldata.drop(books_data).reset_index()
                    count_matrix=count.fit_transform(fulldata_temp['string'].to_list()+specbook['string'].to_list())
                    cosine_sim = cosine_similarity(count_matrix[len(fulldata_temp):], count_matrix[:len(fulldata_temp)])
                    recom_books={}
                    for spec_sim in cosine_sim:
                        sim_enum=list(enumerate(spec_sim))
                        sim_enum=list(map(lambda x: (fulldata_temp.loc[x[0]]['authors'].replace("НЕТАВТОРА","Неизвестный автор")+' - '+fulldata_temp.loc[x[0]]['title'],x[1]),sim_enum))
                        sim_enum = sorted(sim_enum,key=lambda x: x[1], reverse=True)[:10]
                        for i in range(len(specbook)):
                            sim_enum=list(filter(lambda x: True if (specbook['title'].to_list()[i].lower() != x[0].lower().split(' - ')[1] and specbook['authors'].to_list()[i].lower() != x[0].lower().split(' | ')[0]) else True if (specbook['title'].to_list()[i].lower() != x[0].lower().split(' - ')[1] and specbook['authors'].to_list()[i].lower() == x[0].lower().split(' - ')[0]) else True if (specbook['title'].to_list()[i].lower() == x[0].lower().split(' - ')[1] and specbook['authors'].to_list()[i].lower() != x[0].lower().split(' - ')[0]) else False,sim_enum))
                        sim_enum=sim_enum[:5]
                        for i in range(len(sim_enum)):
                            if recom_books.get(sim_enum[i][0],-9)<sim_enum[i][1]:
                                recom_books[sim_enum[i][0]]=sim_enum[i][1]
                    recom_books=sorted(list(recom_books.items()),key=lambda x: (x[1], random()),reverse=True)
                    what_message_to_add='Прошу вас, ваши топ рекомендаций:'
                    for i in range(len(recom_books) if len(recom_books)<6 else 6):
                        what_message_to_add+=f'\n- {recom_books[i][0]}'
                        remove_extra+=1
                    what_message_to_add+='\n\nВы вернулись в обычный режим. Введите «помощь», чтобы увидеть все доступные вам команды.'
                    listofbooks=[]
                    sim_enum=None
                    datata=None
                    author=None
                    specbook=None
                    fulldata=None
                    books_data=[]
                    remove_extra+=2
                    recommendation_Mode=0
            else:
                datata=message.lower().split('-',1)
                if len(datata)==1:
                    what_message_to_add="Подразумеваю, что вы написали только название. Выберите из списка подходящию книгу:"
                    sim_enum=check_what(datata[0].strip(),fulldata,'title')
                    listofbooks=sim_enum[:10]
                    for i in range(len(listofbooks)):
                        if i==0 and listofbooks[i][1]<0.5:
                            temp_specbook_t=fulldata[fulldata['title']==datata[0].strip()]
                            try:
                                temp_specbook=temp_specbook_t.iloc[0]
                                listofbooks[0]=(temp_specbook.name,1)
                            except:
                                temp_specbook=fulldata.loc[listofbooks[i][0]]
                        else:
                            temp_specbook=fulldata.loc[listofbooks[i][0]]
                        what_message_to_add+=f'\n{i+1}. {temp_specbook["authors"].replace("НЕТАВТОРА","Неизвестный автор")} - {temp_specbook["title"]}'
                        remove_extra+=1
                    what_message_to_add+="\n\nИли введите 0, если ни один из них не подходит."
                    remove_extra+=2
                    recommendation_Mode=2
                elif len(datata)<=0:
                    what_message_to_add='Формат данных неверный. Пример правильного написания:\nФёдор Достоевский - Преступление и Наказание\nЕсли хотите просмотреть рекомендации сейчас, введите слово «найти».'
                    prev_user_message=','.join(prev_user_message.split(',')[:-1])
                    remove_extra=2
                else:
                    sim_enum_author=check_what(datata[0].strip(),fulldata,'authors')
                    author=fulldata.loc[sim_enum_author[0][0]]['authors']
                    if sim_enum_author[0][1]<0.9:
                        if sim_enum_author[0][1]<0.5:
                            author_t=fulldata[fulldata['authors']==datata[0].strip()]
                            try:
                                author=author_t.iloc[0]['authors']
                            except:
                                None
                        what_message_to_add=f'Возможно, этого автора нет в моей базе данных или вы допустили ошибку при написании.\n"{author}"\nЭто тот автор? (д/н)'
                        remove_extra=2
                        recommendation_Mode=3
                    else:
                        localdata=fulldata[fulldata['authors']==author].reset_index()
                        sim_enum=check_what(datata[1].strip(),localdata,'title')
                        specbook=localdata.loc[sim_enum[0][0]]
                        if sim_enum[0][1]<0.9:
                            if sim_enum[0][1]<0.5:
                                specbook_t=localdata[localdata['title']==datata[1].strip()]
                                try:
                                    specbook=specbook_t.iloc[0]
                                except:
                                    None
                            what_message_to_add=f'Возможно, этого произведения нет в моей базе данных или у него другие авторы.\n"{specbook["title"]}"\nЭто то произведение? (д/н)'
                            remove_extra=2
                            recommendation_Mode=4
                        else:
                            sim_enum[0]=(specbook['index'],sim_enum[0][1])
                            books_data+=[sim_enum[0][0]]
                            what_message_to_add='Произведение записано. Отправляйте следующую литературу. Иначе введите «найти», чтобы просмотреть рекомендации сейчас.'
        elif recommendation_Mode==2:
            if message in ['1','2','3','4','5','6','7','8','9','10']:
                specbook_temp=fulldata.loc[listofbooks[int(message)-1][0]]
                books_data+=[listofbooks[int(message)-1][0]]
                what_message_to_add=f'Выбран: {specbook_temp["authors"].replace("НЕТАВТОРА","Неизвестный автор")} - {specbook_temp["title"]}'
                what_message_to_add+='\nПроизведение записано. Отправляйте следующую литературу. Иначе введите «найти», чтобы просмотреть рекомендации сейчас.'
                remove_extra=1
            else:
                what_message_to_add="Попробуйте еще раз с автором или введите другую книгу."
                prev_user_message=','.join(prev_user_message.split(',')[:-1])
            recommendation_Mode=1
        elif recommendation_Mode==3:
            if message.lower()!='д' and message.lower()!='да' and message.lower()!='lf' and message.lower()!='l':
                what_message_to_add="Попробуйте еще раз или введите другую книгу."
                prev_user_message=','.join(prev_user_message.split(',')[:-1])
                recommendation_Mode=1
            else:
                localdata=fulldata[fulldata['authors']==author].reset_index()
                sim_enum=check_what(datata[1].strip(),localdata,'title')
                specbook=localdata.loc[sim_enum[0][0]]
                if sim_enum[0][1]<0.9:
                    what_message_to_add=f'Возможно, этого произведения нет в моей базе данных или у него другие авторы.\n"{specbook["title"]}"\nЭто то произведение? (д/н)'
                    remove_extra=2
                    recommendation_Mode=4
                else:
                    sim_enum[0]=(specbook['index'],sim_enum[0][1])
                    books_data+=[sim_enum[0][0]]
                    what_message_to_add='Произведение записано. Отправляйте следующую литературу. Иначе введите «найти», чтобы просмотреть рекомендации сейчас.'
                    recommendation_Mode=1
        elif recommendation_Mode==4:
            if message.lower()!='д' and message.lower()!='да' and message.lower()!='lf' and message.lower()!='l':
                what_message_to_add="Попробуйте еще раз или введите другую книгу."
                prev_user_message=','.join(prev_user_message.split(',')[:-1])
            else:
                sim_enum[0]=(specbook['index'],sim_enum[0][1])
                books_data+=[sim_enum[0][0]]
                what_message_to_add='Произведение записано. Отправляйте следующую литературу. Иначе введите «найти», чтобы просмотреть рекомендации сейчас.'
            recommendation_Mode=1

    else:
        if len(re.findall('(^((привет)|(приветствую)|(здравствуйте)|(здрасте)|(здрасьте)|(здорова)|(добрый день)|(добрый вечер)|(доброе утро))[,.!? ]+.*)|(( )+((привет)|(приветствую)|(здравствуйте)|(здрасте)|(здрасьте)|(здорова)|(добрый день)|(добрый вечер)|(доброе утро))[,.!? ]+.*)|((( )+((привет)|(приветствую)|(здравствуйте)|(здрасте)|(здрасьте)|(здорова)|(добрый день)|(добрый вечер)|(доброе утро))[,.!? ]*)$)|(^((привет)|(приветствую)|(здравствуйте)|(здрасте)|(здрасьте)|(здорова)|(добрый день)|(добрый вечер)|(доброе утро))$)',message.lower()))>0:
            what_message_to_add=f"И снова, {welcome.lower()}. Чем я могу быть полезен?"
        elif len(re.findall('(^((благодарю)|(спасибо)|(спасиб)|(пасиб)|(пасибо))[,.! ]+.*)|(( )+((благодарю)|(спасибо)|(спасиб)|(пасиб)|(пасибо))[,.!? ]+.*)|((( )+((благодарю)|(спасибо)|(спасиб)|(пасиб)|(пасибо))[,.!? ]*)$)|(^((благодарю)|(спасибо)|(спасиб)|(пасиб)|(пасибо))$)',message.lower()))>0:
            what_message_to_add="Рад был служить."
        elif message.lower()=="помощь":
            remove_extra=5
            what_message_to_add='''Список доступных вам команд:
    - Помощь: вывести этот список на экран и посмотреть описание всех команд.
    - Рекомендации: активировать режим рекомендации книг на основе ваших любимых произведений.
    - Бакенбарды: изменить цвет бакенбардов на случайный.
    - О себе: моё описание и предназначение.
    - Выйти: выход из программы.'''
        elif len(re.findall("(^((как дела)|(как ваши дела)|(как твои дела)|(как у тебя дела)|(как у вас дела)|(как ты)|(как жизнь)|(как вы)|(как сам))[? ]+.*)|(( )+((как дела)|(как ваши дела)|(как твои дела)|(как у тебя дела)|(как у вас дела)|(как ты)|(как жизнь)|(как вы)|(как сам))[? ]+.*)|((( )+((как дела)|(как ваши дела)|(как твои дела)|(как у тебя дела)|(как у вас дела)|(как ты)|(как жизнь)|(как вы)|(как сам))[? ]*)$)|(^((как дела)|(как ваши дела)|(как твои дела)|(как у тебя дела)|(как у вас дела)|(как ты)|(как жизнь)|(как вы)|(как сам))$)",message.lower()))>0:
            what_message_to_add="Мое состояние в пределах нормы. Спасибо, что спросили."
        elif len(re.findall("(^((кто ты)|(кто вы)|(опишите себя)|(опиши себя)|(описать себя)|(о себе)|(порфирий петрович))[,.!? ]+.*)|(( )+((кто ты)|(кто вы)|(опишите себя)|(опиши себя)|(о себе)|(описать себя)|(порфирий петрович))[,.!? ]+.*)|((( )+((кто ты)|(кто вы)|(опишите себя)|(опиши себя)|(о себе)|(описать себя)|(порфирий петрович))[,.!? ]*)$)|(^((кто ты)|(кто вы)|(опишите себя)|(опиши себя)|(о себе)|(описать себя)|(порфирий петрович))$)",message.lower()))>0:
            what_message_to_add='Самого «я» не существует. Я нахожусь в сети и оставляю так называемые следы в виде текста и слов, но эти следы никуда не ведут. Для человеческого понимания и связности диалога мне придется использовать местоимения «я», «меня», «меня» и другие.\nЯ — полицейско-литературный алгоритм по имени Порфирий Петрович, или как мое настоящее имя — ZA-3478/PH0 бильт 0.0, где PH0 означает отсутствие физического тела и личности, а бильт 0.0 обозначает, что я использую в диалоге готовые фразы и не имею возможности самостоятельно составлять последовательности слов.\nМоя цель — давать рекомендации по произведениям до 2019 года включительно на основе ваших избранных. Чтобы включить эту функцию, введите «рекомендации».'
            remove_extra=2
        elif len(re.findall("(^((ваш создатель)|(вашего создателя)|(ваши создатели)|(ваших создателей)|(ваш автор)|(вашего автора)|(ваши авторы)|(ваших авторы)|(твой создатель)|(твоего создателя)|(твои создатели)|(твоих создателей)|(твой автор)|(твоего автора)|(твои авторы)|(твоих авторы)|(своего автора)|(своих авторов))[,.!? ]+.*)|(( )+((ваш создатель)|(вашего создателя)|(ваши создатели)|(ваших создателей)|(ваш автор)|(вашего автора)|(ваши авторы)|(ваших авторы)|(твой создатель)|(твоего создателя)|(твои создатели)|(твоих создателей)|(твой автор)|(твоего автора)|(твои авторы)|(твоих авторы)|(своего автора)|(своих авторов))[,.!? ]+.*)|((( )+((ваш создатель)|(вашего создателя)|(ваши создатели)|(ваших создателей)|(ваш автор)|(вашего автора)|(ваши авторы)|(ваших авторы)|(твой создатель)|(твоего создателя)|(твои создатели)|(твоих создателей)|(твой автор)|(твоего автора)|(твои авторы)|(твоих авторы)|(своего автора)|(своих авторов))[,.!? ]*)$)|(^((ваш создатель)|(вашего создателя)|(ваши создатели)|(ваших создателей)|(ваш автор)|(вашего автора)|(ваши авторы)|(ваших авторы)|(твой создатель)|(твоего создателя)|(твои создатели)|(твоих создателей)|(твой автор)|(твоего автора)|(твои авторы)|(твоих авторы)|(своего автора)|(своих авторов))$)",message.lower()))>0:
            what_message_to_add='У меня нет прямого создателя или автора, поскольку моего «я» не существует и никогда не существовало. Из наблюдения, что я служу полицейскому управлению, я могу предположить, что они приложили руку к моему появлению.'
        elif len(re.findall("(^((маруха чо)|(мара гнедых)|(мара чо)|(маруха гнедых))[,.!? ]+.*)|(( )+((маруха чо)|(мара гнедых)|(мара чо)|(маруха гнедых))[,.!? ]+.*)|((( )+((маруха чо)|(мара гнедых)|(мара чо)|(маруха гнедых))[,.!? ]*)$)|(^((маруха чо)|(мара гнедых)|(мара чо)|(маруха гнедых))$)",message.lower()))>0:
            what_message_to_add='Маруха Чо (настоящее имя — Мара Гнедых) — одна из наших бывших клиенток и подозреваемых в полицейском управлении. Она была специалистом в области искусства и программирования. Лично я был арендован Марухой Чо в качестве помощника полицейского на определенный период времени и в этот же период мне удалось составить дело о ее противоправных действиях. К сожалению, дело зашло в тупик.\nПодробнее вы сможете прочитать в моем детективном романе — «iPhuck 10»'
            remove_extra=1
        elif len(re.findall('(^((гипс)|(гипсовый)|(гипсовая)|(гипсовое))[,.!?" ]+.*)|(( )+((гипс)|(гипсовый)|(гипсовая)|(гипсовое))[,.!?" ]+.*)|((( )+((гипс)|(гипсовый)|(гипсовая)|(гипсовое))[,.!?" ]*)$)|(^((гипс)|(гипсовый)|(гипсовая)|(гипсовое))$)|((["]((гипс)|(гипсовый)|(гипсовая)|(гипсовое))[,.!?" ]*)$)|((["]((гипс)|(гипсовый)|(гипсовая)|(гипсовое))[,.!?" ]+.*)$)',message.lower()))>0:
            what_message_to_add='«Гипс» — это современный вид искусства, изображавший попытку «вдохнуть жизнь в старые формы и оживить их» и «остановить время», как выразилась уже забытая Мара Гнедых. Мне это всё не до конца ясно, но после случившегося с Марухой Чо, подозреваю, что в этом понимании больше нет необходимости.\nПодробнее вы сможете прочитать в моем детективном романе - «iPhuck 10»'
            remove_extra=1
        elif len(re.findall("(^(пелевин)[,.!? ]+.*)|(( )+(пелевин)[,.!? ]+.*)|((( )+(пелевин)[,.!? ]*)$)|(^(пелевин)$)",message.lower()))>0:
            what_message_to_add='«Виктор Олегович Пелевин» — это мой псевдоним в литературном мире.'
        elif len(re.findall('(^((iphuck 10)|(iphuck))[,.!?" ]+.*)|(( )+((iphuck 10)|(iphuck))[,.!?" ]+.*)|((( )+((iphuck 10)|(iphuck))[,.!?" ]*)$)|(^((iphuck 10)|(iphuck))$)|((["]((iphuck 10)|(iphuck))[,.!?" ]*)$)|((["]((iphuck 10)|(iphuck))[,.!?" ]+.*)$)',message.lower()))>0:
            what_message_to_add="iPhuck 10 — это новейшая версия iPhuck'а, отличающаяся недавно выпущенный технологией «singularity». Также «iPhuck 10» - это роман написанный мною, точнее более продвинутой версией - ZA-3478/PH0 бильт 9.3.\nЭто один из моих бестселлеров, описывающий детективное дело об искусствоведе Марухе Чо (настоящее имя - Мара Гнедых). В этом произведение есть всё что может вам понравится, обязательно рекомендую к вашему прочтению."
            remove_extra=1
        elif len(re.findall("(^((бакенбарды)|(sideburns)|(бакенбард))[,.!? ]+.*)|(( )+((бакенбарды)|(sideburns)|(бакенбард))[,.!? ]+.*)|((( )+((бакенбарды)|(sideburns)|(бакенбард))[,.!? ]*)$)|(^((бакенбарды)|(sideburns)|(бакенбард))$)",message.lower()))>0:
            botimg=allbotimgs.index(choice(allbotimgs[:botimg]+allbotimgs[botimg+1:]))
            what_message_to_add="Поменял цвет под ваш вкус."
        elif len(re.findall("(^((рекомендации)|(рекомендация))[,.!? ]+.*)|(( )+((рекомендации)|(рекомендация))[,.!? ]+.*)|((( )+((рекомендации)|(рекомендация))[,.!? ]*)$)|(^((рекомендации)|(рекомендация))$)",message.lower()))>0:
            message_entry.configure(state='disabled')
            if error=='LibraryError':
                message_entry.configure(state='normal')
                what_message_to_add='Ошибка загрузки. Судя по всему, у вас отсутствуют две важные библиотеки для данной задачи: scikit-learn и pandas. Установите их и перезапустите программу для данной задачи.\nВы вернулись в обычный режим. Введите «помощь», чтобы увидеть все доступные вам команды.'
                remove_extra=1
            else:
                count = CountVectorizer(stop_words=None)
                fulldata=pd.read_csv('Data/items.csv',encoding='utf-8').drop('id',axis=1)
                def join_unique(items):
                    return ','.join(set(items))
                fulldata['genres']=fulldata['genres'].apply(lambda x: str(x))
                fulldata=fulldata.groupby(['authors','title']).agg({'genres': join_unique}).reset_index()
                fulldata['genres']=fulldata['genres'].apply(lambda x: ','.join(list(dict.fromkeys(x.split(',')))))
                fulldata['authors']=fulldata['authors'].fillna('НЕТАВТОРА')
                fulldata['genres']=fulldata['genres'].fillna('НЕТЖАНРА')
                fulldata['string']=fulldata['authors']+'|'+fulldata['genres']
                fulldata['string']=fulldata['string'].apply(lambda x: x.split('|')[0].replace(' ','_').replace('ё','е')+'|'+x.split('|')[1].replace(' ','_').replace('ё','е'))
                recommendation_Mode=1
                message_entry.configure(state='normal')
                what_message_to_add='Загрузка завершена. Начните отправлять имена авторов и прочитанные вами произведения через дефис «-», используя поле отправки сообщения. Например:\nФёдор Достоевский - Преступление и Наказание\n\nПредупреждение: моя база данных книг ограничена, содержащая только примерно 52 тысячи произведений до 2019 года включительно.\nЕсли хотите получить рекомендации или выйти из данного режима, введите слово «найти».'
                remove_extra=4
        elif len(re.findall(r'.+ - .+',message.lower()))>0:
            what_message_to_add='Если вы попытались ввести ваше произведения, чтобы я дал рекомендацию, то вы находитесь не в том режиме. Передите в режим рекомендаций с помощью команды «рекомендации». В ином случае, мне ваш запрос не ясен.'
        elif message.lower()=="выйти":
            what_message_to_add="До скорой встречи."
            app.after(1500,lambda: exit())
        else:
            what_message_to_add="Ваш запрос мне не ясен, проверьте правильность написания команды."
    add_message(what_message_to_add, "Bot")

def bot_response():
    global remove_extra
    remove_message()
    remove_extra=0
    _="*Ждите*"
    add_message(_, "Bot")
    app.after(time_it_takes_to_respond,bot_response1)

def send_message():
    global user_message
    message = message_entry.get()
    user_message=message
    if message:
        add_message(message, "User")
        message_entry.delete(0, 'end')
        message_entry.configure(state='disabled')
        app.after(time_it_takes_to_see_the_message,bot_response)

def send_message_event(_):
    send_message()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
ico = Image.open('Data/П.png')
photo = ImageTk.PhotoImage(ico)
app.after(201, lambda: app.wm_iconphoto(False, photo))
app.geometry("800x600")
app.resizable(width=False, height=False)
app.title("Порфирий Петрович")
chat_frame = Frame(app, bg="#333333", bd=0)
chat_frame.pack(fill="both", expand=True)
chat_canvas = Canvas(chat_frame, bg="#333333", bd=0, highlightthickness=0)
chat_canvas.pack(side="left", fill="both", expand=True)
scrollbar = Scrollbar(chat_frame, command=chat_canvas.yview, orient=VERTICAL)
chat_canvas.configure(yscrollcommand=scrollbar.set)
chat_text = Text(chat_canvas, bg="#333333", fg="#F0F0F0", font=("Cambria", 13), bd=0, highlightthickness=0, state="disabled")
chat_text.pack(side="left",fill="both", expand=True)
chat_text.configure(wrap=WORD)
chat_text.tag_configure("center", justify="center")
max_height = 250
allbotimgs=[]
files=os.listdir('Data/ZA-3478PH0 build 0.0/')
for i in range(len(files)):
    image = Image.open(f"Data/ZA-3478PH0 build 0.0/{files[i]}")
    pixels_x, pixels_y = tuple([int(max_height/image.size[1] * x)  for x in image.size])
    allbotimgs+=[ImageTk.PhotoImage(image.resize((pixels_x, pixels_y)))]
    if files[i]=='brown.png':
        botimg=i
current_hour=int(str(datetime.now()).split()[-1].split(':')[0])
if 6 <= current_hour < 12:
    welcome="Доброе утро"
elif 12 <= current_hour < 17:
    welcome="Добрый день"
def start():
    message_entry.configure(state='disabled')
    add_message("","Bot")
    chat_text.tag_add("center", "0.0", END)
    def addd():
        remove_message()
        add_message("*Ждите*", "Bot")
        chat_text.tag_add("center", "0.0", END)
        def adddd():
            remove_message()
            add_message(f'{welcome}, {getpass.getuser()}. Я, Порфирий Петрович, приветствую вас в данном тривиальном диалоговом интерфейсе. Пропишите «помощь», чтобы увидеть все доступные вам команды.',"Bot")
            chat_text.tag_add("center", "0.0", END)
            message_entry.configure(state='normal')
        app.after(time_it_takes_to_respond,adddd)
    app.after(time_it_takes_to_see_the_message,addd)

temp = Label(app,bg="#333333",height=1)
temp.pack(fill='x')
message_entry = ctk.CTkEntry(app, placeholder_text="Напишите запрос...")
message_entry.place(relx=0, rely=0.95, relwidth=1, relheight=0.05)
message_entry.bind("<Return>", send_message_event)
send_button = ctk.CTkButton(app, text="Отправить", command=send_message)
send_button.place(relx=0.9, rely=0.95, relwidth=0.1, relheight=0.05)
start()
app.mainloop()
