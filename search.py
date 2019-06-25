import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import MeCab
from .db import get_db
from .search_engine import full_textsearch
import itertools

import re

katakana=re.compile('^[ァ-ヶ]+?')

bp=Blueprint('search',__name__,url_prefix='/search')

@bp.route('/key=<keyword>',methods=('GET','POST'))
def result(keyword):
    db=get_db()

    List_writer=[]
    List_work=[]
    List_free=[]
    keyword=keyword.rstrip()

    m = MeCab.Tagger("-Ochasen")

    ###########%%%%%%%%%%%%%%%%%%%%%%%

    writers = db.execute(
        'SELECT 人物ID,著者名 FROM works WHERE 著者名 like ?', ('%' + keyword + '%',)
    ).fetchall()
    works = db.execute(
        'SELECT 人物ID,著者名,作品ID,作品名 FROM works WHERE 作品名 like ?', ('%' + keyword + '%',)
    ).fetchall()

    for writer in writers:
        tem = list(writer)
        print(List_writer)
        if not len(List_writer) or tem[1] != List_writer[-1][1]:
            tem.append('https://www.aozora.gr.jp/index_pages/person' + str(int(writer[0])) + '.html')
            writer = tuple(tem)
            List_writer.append(writer)

    eng_flag = 0
    for work in works:
        if katakana.match(work[1]):
            eng_flag = 1

    if eng_flag:
        for work in works:
            if katakana.match(work[1]):
                tem = list(work)
                tem.append('https://www.aozora.gr.jp/cards/' + work[0] + '/card' + str(int(work[2])) + '.html')
                work = tuple(tem)
                if not work[3] in (work[3] for work in List_work):
                    List_work.append(work)
    else:
        for work in works:
            tem = list(work)
            tem.append('https://www.aozora.gr.jp/cards/' + work[0] + '/card' + str(int(work[2])) + '.html')
            work = tuple(tem)
            if not work[3] in (work[3] for work in List_work):
                List_work.append(work)

    print(List_work)
    Orign_free = full_textsearch(keyword, 10, 50)
    for free in Orign_free:
        print(free)
        writer = free['writer'].rstrip()
        work = free['title'].rstrip('\n')
        print('-1', writer, writer[-1], work)
        cards = db.execute(
            'SELECT 人物ID,作品ID FROM works WHERE 著者名 like ? AND 作品名 like ?', ('%' + writer[-1], '%' + work + '%',)
        ).fetchone()
        if not cards:
            cards = db.execute(
                'SELECT 人物ID,作品ID FROM works WHERE 作品名 like ?', ('%' + work + '%',)
            ).fetchone()
        if not cards:
            word_r = []
            word_k = []
            for chunk in m.parse(writer).splitlines()[:-1]:
                word = chunk.rstrip().split('\t')[0]  # 分かち書きされた語
                proto = chunk.rstrip().split('\t')[2]
                word_r.append(word)
                break
            for chunk in m.parse(work).splitlines()[:-1]:
                word = chunk.rstrip().split('\t')[0]  # 分かち書きされた語
                proto = chunk.rstrip().split('\t')[2]
                word_k.append(word)
            print('strip', word_r, word_k)
            for r, k in itertools.product(word_r, word_k):
                if cards == None:
                    cards = db.execute(
                        'SELECT 人物ID,作品ID FROM works WHERE 著者名 like ? AND 作品名 like ?',
                        ('%' + r + '%', '%' + k + '%',)
                    ).fetchone()
            if cards == None:
                for k in word_k:
                    cards = db.execute(
                        'SELECT 人物ID,作品ID FROM works WHERE 作品名 like ?',
                        ('%' + k + '%',)
                    ).fetchone()
                    if cards != None:
                        break
            if cards:
                card_t = cards[1]

                cards_t = cards[0]
                free['url'] = 'https://www.aozora.gr.jp/cards/' + cards_t + '/card' + str(int(card_t)) + '.html'
                if free['context']:
                    List_free.append(free)

    #####%%%%%%%%%%%%%%%%%%%%%%%

    for chunk in m.parse(keyword).splitlines()[:-1]:
        word = chunk.rstrip().split('\t')[0]  # 分かち書きされた語
        proto = chunk.rstrip().split('\t')[2]  # 上の語の品詞
        word = word.rstrip()
        # a='%'+word+'%'
        # print('a',a)

        writers = db.execute(
            'SELECT 人物ID,著者名 FROM works WHERE 著者名 like ?', ('%' + word + '%',)
        ).fetchall()
        works = db.execute(
            'SELECT 人物ID,著者名,作品ID,作品名 FROM works WHERE 作品名 like ?', ('%' + word + '%',)
        ).fetchall()
        for writer in writers:
            tem = list(writer)
            print(List_writer)
            if not len(List_writer) or tem[1] != List_writer[-1][1]:
                tem.append('https://www.aozora.gr.jp/index_pages/person' + str(int(writer[0])) + '.html')
                writer = tuple(tem)
                List_writer.append(writer)
        eng_flag = 0
        for work in works:
            if katakana.match(work[1]):
                eng_flag = 1

        if eng_flag:
            for work in works:
                if katakana.match(work[1]):
                    tem = list(work)
                    tem.append('https://www.aozora.gr.jp/cards/' + work[0] + '/card' + str(int(work[2])) + '.html')
                    work = tuple(tem)
                    if not work[3] in (work[3] for work in List_work):
                        List_work.append(work)
                else:
                    continue
        else:
            for work in works:
                tem = list(work)
                tem.append('https://www.aozora.gr.jp/cards/' + work[0] + '/card' + str(int(work[2])) + '.html')
                work = tuple(tem)
                if not work[3] in (work[3] for work in List_work):
                    List_work.append(work)
        print(List_work)
        Orign_free = full_textsearch(proto, 10, 50)
        for free in Orign_free:
            print(free)
            writer = free['writer'].rstrip()
            work = free['title'].rstrip('\n')
            try:
                print('-1', writer, writer[-1], work)
                cards = db.execute(
                    'SELECT 人物ID,作品ID FROM works WHERE 著者名 like ? AND 作品名 like ?', ('%' + writer[-1], '%' + work + '%',)
                ).fetchone()
            except:
                pass
            if not cards:
                cards = db.execute(
                    'SELECT 人物ID,作品ID FROM works WHERE 作品名 like ?', ('%' + work + '%',)
                ).fetchone()
            if not cards:
                word_r = []
                word_k = []
                for chunk in m.parse(writer).splitlines()[:-1]:
                    word = chunk.rstrip().split('\t')[0]  # 分かち書きされた語
                    proto = chunk.rstrip().split('\t')[2]
                    word_r.append(word)
                    break
                for chunk in m.parse(work).splitlines()[:-1]:
                    word = chunk.rstrip().split('\t')[0]  # 分かち書きされた語
                    proto = chunk.rstrip().split('\t')[2]
                    word_k.append(word)
                print('strip', word_r, word_k)
                for r, k in itertools.product(word_r, word_k):
                    if cards == None:
                        cards = db.execute(
                            'SELECT 人物ID,作品ID FROM works WHERE 著者名 like ? AND 作品名 like ?',
                            ('%' + r + '%', '%' + k + '%',)
                        ).fetchone()
                if cards == None:
                    for k in word_k:
                        cards = db.execute(
                            'SELECT 人物ID,作品ID FROM works WHERE 作品名 like ?',
                            ('%' + k + '%',)
                        ).fetchone()
                        if cards != None:
                            break

            # print(writer[-1],'cards',cards)
            # card=cur.execute('SELECT 作品ID FROM works WHERE 作品名 like ?',('%'+work+'%',)
            # ).fetchone()
            # print('card',card[0])

            card_t=cards[1]

            cards_t=cards[0]
            free['url']='https://www.aozora.gr.jp/cards/'+cards_t+'/card'+str(int(card_t))+'.html'
            if free['context']:
                List_free.append(free)
        # len_wr = 0
        # len_work = 0
        # len_free = 0
        len_wr=len(List_writer)
        len_work=len(List_work)
        len_free=len(List_free)
        print('len_free',len_free)

    return render_template('search/Search_result.html',list_writer=List_writer,list_work=List_work,list_free=List_free,
                           len_writer=len_wr,len_free=len_free,len_work=len_work,keyword=keyword)
