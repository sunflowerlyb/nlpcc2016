#-*- coding:utf-8 -*-
import sys
import os
import re
from collections import defaultdict
import math
import json
import random
import time
import nltk
import multiprocessing

av_save = {}
sa = []
content = ''

def format_data(dir_path, tag):#根据需要是否需要给数据加标签
    if tag == 0:
        deal_data(dir_path + '/train.txt', 'train.data')#将数据处理成正确的格式
        deal_data(dir_path + '/test.txt', 'tests.data')#
    else:
        deal_data_av(dir_path + '/train_av.txt', 'train.data')#将数据处理成正确的格式
        deal_data_av(dir_path + '/test_av.txt', 'tests.data')#

def trans_unicode(pwd):
    print '\n'
    for dirs in os.walk(pwd):
        for filename in dirs[2]:
            if filename.endswith('.txt'):
                path = pwd + '/' + filename
                print 'trans unicode to utf-8:',filename
                file_o = open(path)
                file_r = file_o.read()
                file_o.close()
                
                try:
                    text = file_r.decode('utf-8')
                except:
                    text = file_r.decode('gbk','ignore')
                text = text.replace(u'　', ' ')
                text = text.replace(u' ', ' ')
                text = text.replace(u'　', ' ')
                text = text.replace(u' ', ' ')
                text = re.sub(r"( )+", " ", text)
                file_w = open(path, 'w')
                file_w.write(text.encode('utf-8'))
                file_w.close()

def deal_data_av(path, files):
    global av_save
    global sa
    global content
    
    dictt = {0:'B',1:'C',2:'D',3:'M',-1:'E'}
    dir_path = path[0:path.rfind('/')]

    print '\nadd av tag .',
    file_o = open(path)
    file_r = file_o.read()
    file_o.close()
    file_r = re.sub(r"(　)+"," ", file_r)
    file_r = re.sub(r"( )+"," ", file_r)#全文空格替换成一致的
    lines = file_r.decode('utf-8').split('\n')
    
    file_w = open(dir_path + '/' + files,'w')

    count = 0
    for line in lines:
        line = line.strip()
        
        if(line != ""):#教[7,2,4,2,0,]科[8,0,0,0,0,]书[8,6,0,0,0,] 
            line = line.replace(' ', '')
            
            words = line.split(",]")
            if '' in words:
                words.remove('')

            lenword = len(words)
            if lenword == 1:#单字词
                av = '\t'.join(words[0][words[0].find('[') + 1:].split(','))
                file_w.write((words[0][0] + '\t' + av + '\t' + 'S').encode('utf-8') + '\n')
                
            else:#duo字词
                for i in range(lenword):
                    av = '\t'.join(words[i][words[i].find('[') + 1:].split(',')) 
                    if i < 4 and i < lenword -1:
                        k = i;
                    elif i != lenword - 1:
                        k = 3
                    else:
                        k = -1
                    file_w.write((words[i][0] + '\t' + av + '\t' + dictt[k]).encode('utf-8') + '\n')
                    
        else:
            file_w.write('\n')
    file_w.close()

def ngram_feature(words, n):
    features = []

    for i in range(0, len(words) - n + 1):
        word_end = i + n
        word = words[i:word_end]
        av = log2(av_score(word))
        if av < 0:
            av = 0
        features.append(str(av))

    while len(features) < len(words):
        features.append('0')

    return features

def sort_bucket(str, bucket, order):
    d = defaultdict(list)
    result = []

    for i in bucket:
        key = str[i:i+order]
        d[key].append(i)
    
    for k,v in sorted(d.iteritems()):
        if len(v) > 1:#如果多次出现key 那么增加key的长度
            result += sort_bucket(str, v, order*2)
        else:
            result.append(v[0])#

    return result

def generate_sa(str):
    print '\ngenerate sa .',
    return sort_bucket(str, (i for i in range(len(str))), 1)

def cmp_word(words, start):
    global content
    cmp_len = len(content) - start
    n = min(len(words), cmp_len)
    i = 0
    while i < n:
        if words[i] < content[start + i]:
            return -1
        if words[i] > content[start + i]:
            return 1
        i += 1
    return len(words) - cmp_len

def rank(words): #查找words的位置
    global sa
    global content
    low = 0
    high = len(sa) - 2
    while low <= high:
        mid = low + (high - low) / 2
        res = cmp_word(words, sa[mid])
        if res < 0:
            high = mid - 1
        elif res > 0:
            low = mid + 1
        else:
            return mid
    return low

def av_score(words):
    global av_save
    global sa
    global content

    if av_save.has_key(words):
        return av_save[words]

    if content.find(words):
        left_val = 0
        left_set = set()

        right_val = 0
        right_set = set()

        words_len = len(words)
        
        r = rank(words)
        i = r
        lenc = len(content)
        count = 0
        while i < lenc:
            index = sa[i]
            substring = content[index:min(index + words_len, len(content))]
            count += 1
            if substring == words:
                j = index - 1
                if j > 0:
                    ch = content[j]
                    if ch == 'S':
                        left_val += 1
                    else:
                        left_set.add(ch)

                j = index + words_len
                if j < len(content):
                    ch = content[j]
                    if ch == 'E':
                        right_val += 1
                    else:
                        right_set.add(ch)
            else:
                if count > 1:
                    break
            i += 1

        left_val += len(left_set)
        right_val += len(right_set)

        val = min(left_val, right_val)
        av_save[words] = val

        #print val
        return val
    else:
        av_save[words] = 0
        return 0

def log2(x):
    if x < 1:
        return 0
    return (int)(math.log(x) / math.log(2))


def generate_text(path):
    if not os.path.exists(path + '/text.txt'):
        print '\ngenerate text.txt'
        file_o = open(path + '/train.txt')
        text = file_o.read().strip()
        file_o.close()
        file_o = open(path + '/test.txt')
        text = text + '\n'+file_o.read().strip() + '\n'
        file_o.close()
        file_o = open(path + '/ext.txt')
        text = text + '\n'+file_o.read().strip() + '\n'
        file_o.close()


        text = text.replace(' ','')
        text = text.replace('　','')
        text = re.sub(r'：|，|。|！|？|；|,|\?|!|“|”','\n',text)
        text = re.sub(r'(\n)+','\n', text)#去除多余的换行符
        lines = text.split('\n')
        lines = list(set(lines))#去除重复的句子

        text = ''
        for line in lines:
            line = line.strip()
            if line != '':
                text += 'S' + line + 'E'

        file_w = open(path + '/text.txt', 'w')
        file_w.write(text)
        file_w.close()
        print '\ngenerate text.txt sucessfully!'


def deal_data(path, files):#path为需要处理的数据全路径，files是保存处理后的数据的文件名
    #print 'deal_data'
    print '.',
    dictt = {0:'B',1:'C',2:'D',3:'M',-1:'E'}

    file_o = open(path)
    file_r = file_o.read()
    file_o.close()

    file_r = file_r.replace(" ","　")
    file_r = re.sub(r"(　)+","　", file_r)
    file_w = open(path[0:path.rfind('/') + 1] + files,'w')
    lines = file_r.decode('utf-8').split('\n')

    for line in lines:
        line = line.strip()
        if(line != ""):
            temp = line.split(u"　")
            for words in temp:
                words =  words.strip()
                lenword = len(words)
                if lenword == 1:#单字词
                    file_w.write(words.encode('utf-8') + '\t' + 'S' + '\n')
                elif lenword > 1:#单字词
                    for i in range(lenword - 1):
                        if i < 4:
                            file_w.write(words[i].encode('utf-8') + '\t' + dictt[i] + '\n')
                        else:
                            file_w.write(words[i].encode('utf-8') + '\t' + dictt[3] + '\n')
                    file_w.write(words[-1].encode('utf-8') + '\t' + dictt[-1] + '\n')
        file_w.write('\n')
    file_w.close()
    

def generate_dict_prob(path):#利用dicts
#未登录词0 其他10
#1表示单独成词的概率大于95% 2表示单独成词的概率85%－95% 3表示单独成词的概率小于5%
#4表示作为词头的概率大于95% 5表示作为词头的概率85%－95% 6表示作为词头的概率小于5%
#7表示作为词尾的概率大于95% 8表示作为词尾的概率85%－95% 9表示作为词尾的概率小于5%

    words = {} # bbegin s:single sum:sum e:end
    prob = {}
    if os.path.exists(path + '/dicts.txt'):
        file_o = open(path + '/dicts.txt')
        file_r = file_o.read().decode('utf-8')
        file_o.close()

        file_r = re.sub(r'(\n)+', '\n', file_r)
        lines = file_r.split('\n')

    else:
        #根据训练数据生成词频
        file_o = open(path + '/freq.txt')
        file_r = file_o.read().decode('utf-8')
        file_o.close()

        file_r = re.sub(r'(\n)+', ' ', file_r)
        file_r = re.sub(r'( )+', ' ', file_r)
        file_r = file_r
        wordss = file_r.split(' ')
        if '' in wordss:
            wordss.remove('')
        if ' ' in wordss:
            wordss.remove(' ')

        fredist = nltk.FreqDist(wordss)
        if os.path.exists(path + '/fredist.json'):
            os.remove(dir_path + '/fredist.json')
        json.dump(fredist.items(), open(path + '/fredist.json', 'w'))

        lines = [ item[0] + ' ' + str(item[1]) for item in fredist.items()]

    for line in lines:
        line = line.strip() 
        if line != "":
            temp = line.split(' ')
            if len(temp) > 1:
                w = temp[0]
                num = int(temp[1])

                for ww in list(w):
                    if not words.has_key(ww):
                        words[ww] = {'b':0}
                        words[ww]['sum'] = 0
                        words[ww]['e'] = 0
                        words[ww]['s'] = 0

                if len(w) == 1:
                        words[w]['s'] += num
                        words[w]['sum'] += num
                    
                elif len(w) > 1:
                    for loc in range(len(w) - 1):
                        if loc == 0:
                            words[w[loc]]['b'] += num
                            words[w[loc]]['sum'] += num
                        else:
                            words[w[loc]]['sum'] += num
                            
                    words[w[-1]]['e'] += num
                    words[w[-1]]['sum'] += num
            else:
                print line,

    for key in words.keys():
        probs = (float)(words[key]['s']) / (float)(words[key]['sum'])
        if probs > 0.95:
            prob[key] = 1
        elif probs > 0.85:
            prob[key] = 2
        elif probs < 0.05:
            prob[key] = 3
        else:
            probs = (float)(words[key]['b']) / (float)(words[key]['sum'])
            if probs > 0.95:
                prob[key] = 4
            elif probs > 0.85:
                prob[key] = 5
            elif probs < 0.05:
                prob[key] = 6
            else:
                probs = (float)(words[key]['e']) / (float)(words[key]['sum'])
                if probs > 0.95:
                    prob[key] = 7
                elif probs > 0.85:
                    prob[key] = 8
                elif probs < 0.05:
                    prob[key] = 9
                else:
                    prob[key] = 10
    json.dump(prob, open(path + '/dict_prob_feat.json', 'w'))

def generate_dict_feat(path):#生成字典特征json文件
    #print 'generate_dict_feat'
    print '.',
    file_o = open(path + '/dictionary.txt')
    file_r = file_o.read()
    file_o.close()
    li = file_r.strip().decode('utf-8').split('\n')

    file_o = open(path + '/train.txt')
    file_t = file_o.read()
    file_t = file_t.replace('\n', '　')
    file_t = re.sub(r" ","　",file_t)
    file_t = re.sub(r"(　)+","　",file_t)
    file_t = file_t.strip().decode('utf-8')
    li.extend(file_t.split(u'　'))

    li = list(set(li))
    li.sort(key = len, reverse = 1)

    dict_f = {}
    for i in li:
        i = i.strip()
        leni = len(i)
        if leni > 1:
            if not dict_f.has_key(i[0] + '1'):#以i[0]为首的
                if leni > 5:
                    dict_f[i[0] + '1'] = '6'
                else:
                    dict_f[i[0] + '1'] = str(leni)
                
            if not dict_f.has_key(i[-1] + '0'):#以i[0]为尾的
                if leni > 5:
                    dict_f[i[-1] + '0'] = '6'
                else:
                    dict_f[i[-1] + '0'] = str(leni)
        else:
            break

    file_w = open(path + '/dict.txt', 'w')
    file_w.write('\n'.join(li).encode('utf-8'))
    file_w.close()

    json.dump(dict_f, open(path + '/dict_feat.json', 'w'))


def generate_ef_feat(path):#生成bigram ，调用get_ef生成条件墒
    #print 'generate_ef_feat'
    print '.',
    file_o = open(path + '/train.txt')
    text = file_o.read()
    file_o.close()
    file_o = open(path + '/test.txt')
    text = text + file_o.read()
    file_o.close()
    file_o = open(path + '/ext.txt')
    text = text + file_o.read()
    file_o.close()

    text = text.replace(' ','')
    text = re.sub(r'(\n)+','\n', text)
    text = text.replace('　','')
    text = text.strip().decode('utf-8')
    lines = text.split('\n')
    lines = list(set(lines))

    freq = {1:{},0:{}}#1正向0反向
    ef = {}
    for line in lines:
        line = line.strip()
        if line != '':
            words = list(line)
            words.insert(0, '--')
            words.append('--')

            for i in range(len(words) - 1):
                if i != 0:
                    if freq[1].has_key(words[i]):
                        if freq[1][words[i]].has_key(words[i + 1]):
                            freq[1][words[i]][words[i + 1]] += 1
                        else:
                            freq[1][words[i]][words[i + 1]] = 1
                        freq[1][words[i]]['sum'] += 1
                    else:
                        freq[1][words[i]] = {words[i + 1] : 1}
                        freq[1][words[i]]['sum'] = 1
                    
                if i != len(words) - 2:
                    if freq[0].has_key(words[i + 1]):
                        if freq[0][words[i + 1]].has_key(words[i]):
                            freq[0][words[i + 1]][words[i]] += 1
                        else:
                            freq[0][words[i + 1]][words[i]] = 1
                        freq[0][words[i + 1]]['sum'] += 1
                    else:
                        freq[0][words[i + 1]] = {words[i] : 1}
                        freq[0][words[i + 1]]['sum'] = 1
    #print json.dumps(freq,ensure_ascii=False) + '\n'
    for i in freq.keys():
        for item in freq[i].keys():
            ef[item + str(i)] = get_ef(freq[i][item])
    
    #print json.dumps(ef,ensure_ascii=False) + '\n'
    json.dump(ef, open(path + '/ef_feat.json', 'w'))

def get_ef(condition):#计算条件墒
    H = 0.0
    sum1 = condition.pop('sum')
    for value in condition.keys():
        p = (float)(condition[value]) / (float)(sum1)
        H += p * math.log(p) / math.log(2)  #以2为底的对数，math。log默认以10为底
    H = abs(H)
    if H < 1:  #此处也可以作为可调整的参数
        return 0
    elif H < 2:
        return 1
    elif H < 3.5:
        return 2
    elif H < 5:
        return 4
    elif H < 7:
        return 5
    else:
        return 6

def generate_w2v_feat(path):
    print '.',
    file_num = [10, 20, 25, 50, 100, 200, 500]
    w_c = defaultdict(int)

    for num in file_num:
        file_o = open(path + '/cluster/' + str(num) + '.dat')
        lines = file_o.readlines()
        file_o.close()

        count = 0
        for line in lines:
            line = line.strip().decode('utf-8')
            count += 1
            if line != '':
                for word in list(line.split(' ')):
                    w_c[word + str(num)] = count

    json.dump(w_c, open(path + '/w2v_feat.json', 'w'))

class add_tag(object):
    """docstring for add_tag"""
    def __init__(self, file_n, flag, tag):

        self.tag_biaodian = {'，','。','；','“','”','！','？','【','】','（','）','［','］','｛','｝','：','、','《','》'}
        self.tag_danwei = {'吨','余','斤','点','年','月','日','个','只','头','页','天','千','万','百','时','分','秒','成','折','亿','余','旬','米','号'}
        #self.tag_fuhao = {'＃','&',',','.', '-', '*','_','>','<',':','/','(',')', '^', '@','％','.','·','•','#','~','`','\\'}
        self.file_n = file_n
        pwd = os.path.abspath('..')
        self.dir_path = pwd[:pwd.rfind('/')] + '/data/test_weighed/' + self.file_n 
        
        trans_unicode(self.dir_path)
        if flag == 1:
            print '\nformat data .',
            format_data(self.dir_path, tag)

        #print self.dir_path
        self.webdict = {}#字典特征
        self.av = {}#av特征
        self.ef = {}#条件墒特征
        self.prob = {}
        self.word_class = defaultdict(int)
        #word_class['我10'] ＝ 2表示我这个词在类别10种为2
        #若不存在责统一标记为0

        print '\nload dict prob feature info .',
        self.load_prob_feat()
        print '\nload dict feature info .',
        self.load_dict_feat()
        print '\nload ef feature info .',
        self.load_ef_feat()
        print '\nload zi lei bie info .',
        self.load_leibie_feat()
        
    def load_leibie_feat(self): 
        print '.',
        path = self.dir_path + '/w2v_feat.json'#获取当前路径
        if not os.path.exists(path):
            generate_w2v_feat(self.dir_path)
            self.word_class = json.load(open(path,'r'))
        else:
            self.word_class = json.load(open(path,'r'))


    def load_prob_feat(self): 
        print '.',
        path = self.dir_path + '/dict_prob_feat.json'#获取当前路径
        if not os.path.exists(path):
            generate_dict_prob(self.dir_path)
            self.prob = json.load(open(path,'r'))
        else:
            self.prob = json.load(open(path,'r'))
        
    def load_dict_feat(self):
        #print 'load_dict_feat'
        print '.',
        path = self.dir_path + '/dict_feat.json'#获取当前路径
        if not os.path.exists(path):
            generate_dict_feat(self.dir_path)
            self.webdict = json.load(open(path,'r'))
        else:
            self.webdict = json.load(open(path,'r'))

    def load_ef_feat(self):
        #print 'load_ef_feat'
        print '.',
        path = self.dir_path + '/ef_feat.json'#获取当前路径
        if not os.path.exists(path):
            generate_ef_feat(self.dir_path)
            self.ef = json.load(open(path,'r'))
        else:
            self.ef = json.load(open(path,'r'))
    
    #tag  根据字符的 Unicode 
    #编码将字符分为8类:
    #普通汉字为1,
    #字母a-zA-Z为2,
    #0-9数字为3,
    #标点为4（，。；“”！？【】：） 4
    #计量单位如“点年月日个只头天千万百时分秒成折亿余旬米号时”为5,
    #“＃@&％.·•”字符为6,
    #中文数字7
    #其他字符为8,
    def add_all_tag(self, names):
        print '.',
        #print 'add_all_tag'
        file_o = open(self.dir_path + '/' + names)
        file_r = file_o.read().decode('utf-8')
        file_o.close()
        file_w = open(self.dir_path + '/' + names, 'w')

        #file_r = re.sub(r'(\n)+','\n', file_r)
        file_r = file_r.replace(u' ', ' ')
        file_r = re.sub(r'( )+',' ', file_r)

        lines = file_r.split('\n')
        tag = 0
        count = 0
        word_2 = ''
        word_1 = ''
        for line in lines:#这么写为了计算av特征时方便
            count += 1
            if count == 10000:#进度条
                print '.',
                count = 0

            line = line.strip()
            if line != "":
                #添加字类型，一列：6
                if re.search(r'[0-9]', line[0]):#line[0].isdigit:#3
                    tag = 1
                    #print line
                    flag = '3'
                elif tag == 1 and line[0].encode('utf-8') in self.tag_danwei:
                    tag = 0
                    flag = '5'
                elif line[0].encode('utf-8') in self.tag_biaodian:
                    tag = 0
                    flag = '4'
                elif re.search(r'[a-zA-Z]', line[0]):
                    tag = 0
                    flag = '2'
                elif re.search(r'[一二三四五六七八九十零]', line[0]):
                    tag = 0
                    flag = '7'
                elif not re.compile(u'[^\u4E00-\u9FA5]').findall(line[0]):#若无非中文字符
                    tag = 0
                    flag = '1'
                elif len(line[0].encode('utf-8')) == 1:#如果以上都不是，且编码之后只占用一个字节那么有可能是表情符号
                    tag = 0
                    flag = '6'
                else:
                    tag = 0
                    flag = '8'

                ls = line[:-1] + flag + '\t'#第一列为字类型标签

                #添加字典概率特征，一列：7
                if self.prob.has_key(line[0]):
                    fir = str(self.prob[line[0]])
                else:
                    fir = '0'
                ls = ls + fir + '\t'

                # 当前字和前面的字是否为叠字8 9=0
                if line[0] == word_1 and line[0] == word_2:
                    fir = '3'
                elif line[0] == word_1:
                    fir = '1'
                elif line[0] == word_2:
                    fir = '2'
                else:
                    fir = '0'

                ls = ls + fir + '\t' + '0' + '\t'


                #添加墒特征 两列：10 11
                if self.ef.has_key(line[0] + '1'):
                    fir = str(self.ef[line[0] + '1'])
                else:
                    fir = '0'

                if self.ef.has_key(line[0] + '0'):
                    las = str(self.ef[line[0] + '0'])
                else:
                    las = '0'
                ls = ls + fir + '\t' + las + '\t' #第四列为前向最大墒特征 第五列为后向最大墒特征

                #添加字类别信息 12-10类
                if self.word_class.has_key(line[0] + '10'):
                    param = str(self.word_class[line[0] + '10'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 13-20类
                if self.word_class.has_key(line[0] + '20'):
                    param = str(self.word_class[line[0] + '20'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 14-25类
                if self.word_class.has_key(line[0] + '25'):
                    param = str(self.word_class[line[0] + '25'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 15-50类
                if self.word_class.has_key(line[0] + '50'):
                    param = str(self.word_class[line[0] + '50'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 16-100类
                if self.word_class.has_key(line[0] + '100'):
                    param = str(self.word_class[line[0] + '100'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 17-200类
                if self.word_class.has_key(line[0] + '200'):
                    param = str(self.word_class[line[0] + '200'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                #添加字类别信息 18-500类
                if self.word_class.has_key(line[0] + '500'):
                    param = str(self.word_class[line[0] + '500'])
                else:
                    param = '0'
                ls = ls + param + '\t'
                
                #追加标签信息
                ls = ls + line[-1] + '\n'
                word_2 = word_1
                word_1 = line[0]
            else:
                word_2 = ''
                word_1 = ''
                ls = '\n'
            file_w.write(ls.encode('utf-8'))
            
        file_w.close()


if __name__ == '__main__':

    '''
    若文件夹中有json文件，那么是中间生成数据，如果删掉，程序会自动重新生成。
    
    #标记数据在原来字上加tag，字典dict，前后条件墒，av特征信息
    #运行 python -u get_feature.py就不会出现print延迟问题了

    若已经有初步标记好的数据，可以把flag设为0，但是不建议用，因为每个人准备的数据可能有什么小差错
    '''
    start_time1 = time.time()
    print 'start...'
    flag = 1
    tag = 1#tag为0时不用av特征，为1时用
    tt = add_tag('open2', flag, tag)
    end_time = time.time()
    print("\nThe Pre process is %g seconds" % (end_time - start_time1))

    print '\n\ntag train data .',
    tt.add_all_tag('train.data')#为训练数据加特征标签
    print '\ntag tests data .',
    tt.add_all_tag('tests.data')#为测试数据加特征标签

    print '\nsuccessfull!!'

    end_time = time.time()
    print("\nThe whole process is %g seconds" % (end_time - start_time1))
