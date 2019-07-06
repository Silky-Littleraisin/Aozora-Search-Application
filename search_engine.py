from whoosh.index import open_dir
from whoosh import qparser
from whoosh import highlight
import time
from pprint import pprint
import re
from flask import current_app
before=re.compile('&lt;proto&gt;')
after=re.compile('&lt;/proto&gt;')
final=re.compile('&lt;/proto|proto&gt;|&lt;proto')
pattern1=re.compile('<proto>.*?</proto>')
pattern2=re.compile('<proto> <b class="match term0">.*?</b> </proto>')
pattern3=re.compile('<proto>|</proto>')
zhushi=re.compile('［＃.*?］')

def full_textsearch(key,top,surround):
    ix = open_dir("/Users/silky/Documents/GitHub/full_text_search","engine2") #作成したインデックスファイルのディレクトリを指定
    with ix.searcher() as searcher:
        parser = qparser.QueryParser("content", ix.schema)

        op = qparser.OperatorsPlugin(And="&", Or="\\|", Not="~")
        parser.replace_plugin(op) #opをセット
        words = key
        start = time.time()
        words = words.split()
        words = "".join(words)
        query = parser.parse(words)
        results = searcher.search(query, limit=50)
        # for result in results:asae_iku来る
        #     print(result.highlights('content'))
        results.fragmenter.maxchars=150
        results.fragmenter.surround=surround
        results.order = highlight.SCORE
        pprint(results)
        search_result=[]
        for fragment in results:
            dict={}
            # print(fragment.highlights('content',top=top))

            tem=final.sub('',after.sub('</proto>',before.sub('<proto>',fragment.highlights('content',top=top)),))
            while pattern2.search(tem)!=None:
                position=pattern2.search(tem).start()
                lenth=len(pattern2.search(tem).group())
                tem=tem[0:position] + \
                '<b class="match term0">'+tem[position+lenth:position+lenth*2-len('<proto> <b class="match term0"></b> </proto>')] +\
                '</b>' + tem[position+lenth*2-len('<proto> <b class="match term0"></b> </proto>'):]
            # tem[position:position+lenth*2-len('<proto> <b class="match term0"></b> </proto>')] =\
            tem=pattern1.sub('',tem)
            tem=pattern3.sub('',tem)
            tem=tem.replace(' ','')
            tem=tem.replace('<bclass="matchterm0">','<b class="matchterm0">')
            tem=zhushi.sub('',tem)

            dict['context'] = tem

            print(dict['context'])
            dict['title']=fragment['title']
            dict['writer']=fragment['writer']
            search_result.append(dict)

            print('#'*30,'\n')
        print("計%d記事" %len(results))
        print(str((time.time() - start)*10000//10)+"ms") #時間計測用
        return search_result

