#-*- coding:utf-8 -*-

import sys
import os
import re
from collections import defaultdict
import copy
import json
import random
#比分 空格 成语

# 3、表情符号 全文匹配
def deal_bq(line, path):

	regex = re.compile(u'(.|*|\|?|+|{|}|(|))')
	if re.search(r'(一|∪|．|ㄒ|＞|□|∠|ε|︴|︵|▽|υ|ˇ|ω|ˋ|﹌|※|`|︽|╮|︿|▂|→|↖|口|﹋|﹏|◎|╥|≧|╭|o|╱|‥|☆|↓|〒|└|↗|⊙|┘|Σ|…|\*|△|′|┴|︶|≡|σ|◇|○|●|︸|˙|\^|￣|︺|≦|╬|╰|、|★|﹀|▔|Ψ|-|‵|ㄟ|︹|＿|﹁|ψ|ˊ|∥|]|╯)', line):
		file_o = open(path)
		lines = file_o.read().decode('utf-8').strip().split('\n')
		file_o.close()

		for bq in lines:
			l = list(bq.strip())
			if ' ' in l:
				l.remove(' ')
			if '' in l:
				l.remove('')

			tt = ' '.join(l)

			if '*' in l:
				l.remove('')
			if '.' in l:
				l.remove('')
			if '?' in l:
				l.remove('')

			if '\\' in l:
				l.remove('')
			char = ' ?'.join(l)
			line = re.sub(r' ' + char + ' ', ' ' + bq+ ' ',line)

	return line
	#凸^-^凸

# 1、若字典中存在一个长词，被切分了，则合并该词，遵循前向最长匹配。
def deal_dict(dicts, line):
	print 'dict'
	words = line.split(' ')
	lenl = len(words)
	i = 0
	while i < lenl - 1:#每次判断连续的两个词组成的新词是否在字典中。
		word = words[i] + words[i + 1]
		if word in dicts: #若在则合并
			words = words[:i] + words[i + 1:]
			words[i] = word
			lenl -= 1
		else:
			i += 1

	return ' '.join(words)

# 7、文中连续的词，如哈哈哈哈，应视为一个词，连续三个相同的字出现三次及以上就认为是复字
def deal_continues(line):
	#外面 下雨 了 哈 哈 哈 哈 哈 哈 哈 哈 哈 哈哈 哈 哈 哈 哈 。 。 。 。 。如果用上面的替换这样的会匹配不成功
	s = 'aa ' + line.strip() + ' aa'
	ref = re.compile('( .)\\1{2,}( .*)$')
	result = ref.findall(s)

	while result:
		word = result[0][0]
		loc = len(s) - len(result[0][1])
		while(s[loc - 1] == s[:loc-1].strip()[-1]):
			s = s[:loc - 1].strip() + s[loc - 1:].strip()
			if loc - 2 > -1:
				loc = loc - 2
			else:
				break
		result = ref.findall(s)

	return s[3:-3].strip()

########################################


def deal_comp(text,dir_path):
	file_o = open(dir_path + '/result/result/com.txt')
	file_r = file_o.readlines()
	file_o.close()
	lines = set(file_r)
	for line in lines:
		line = line.strip().decode('utf-8')
		words = line.split(':')
		#print words[0],words[1]
		text = text.replace(' ' + words[0].strip() + ' ', ' ' + words[1].strip() + ' ')
	return text

# 2、小数点处理及外文名 全文匹配	
def deal_bd(line):
	line = line.encode('utf-8')
	print 'biaodian.',
	#连续的数字放在一起，连续的英文字母就不要放在一起了
	regex = re.compile(r'(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７) *( \.|\. |: | :| ) *(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５| ８|３|６|４|７)')
	text0 = ''
	while line != text0:
		text0 = line
		line = regex.sub(lambda m:m.group(0).replace(' ', ''),line)
	#words = ['点', '', '', '']
	
	#iPhoneSE
	regex = re.compile(r'(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７)点')
	line = regex.sub(lambda m:m.group(0).replace('点', ' 点'),line)
	
	#亿 元,5楼
	line = line.replace('亿元', '亿 元')

	regex = re.compile(r'(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７) 楼')
	line = regex.sub(lambda m:m.group(0).replace(' 楼', '楼'),line)
	#,/数字和英文应该分开，汉字与汉字也要
	regex = re.compile(r'(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７)/[a-zA-Z]')
	line = regex.sub(lambda m:m.group(0).replace('/', ' / '),line)
	regex = re.compile(r'[a-zA-Z]/(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７)')
	line = regex.sub(lambda m:m.group(0).replace('/', ' / '),line)
	regex = re.compile(r'[\u4E00-\u9FA5]/[\u4E00-\u9FA5]')
	line = regex.sub(lambda m:m.group(0).replace('/', ' / '),line)
	#数字/数字
	regex = re.compile(r' [0-9]+ / [0-9]+ ')
	line = regex.sub(lambda m:m.group(0).replace(' / ', '/'),line)
	#点时 30分，如果数字fen之前没有点或者时，那么以记分算,中间需要加空格
	regex = re.compile(r'(点|时) ?[0-9]+ ?分')
	line = regex.sub(lambda m:m.group(0).replace(' 分', '分'),line)
	regex = re.compile(r'[^点时] ?[0-9]+分')
	line = regex.sub(lambda m:m.group(0).replace('分', ' 分'),line)
	regex = re.compile(r'分[0-9]')
	line = regex.sub(lambda m:m.group(0).replace('分', '分 '),line)
	

	regex = re.compile(r'[午上晨晚](1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７)+ 点')
	line = regex.sub(lambda m:m.group(0).replace(' 点', '点'),line)
	regex = re.compile(r'(1|2|3|4|5|6|7|8|9|0|２|９|０|１|５|８|３|６|４|７)+ 点半')
	line = regex.sub(lambda m:m.group(0).replace(' 点半', '点半'),line)
	print 'while'
	while line.find('哈 哈') > -1:#把哈哈给合并吧，因为训练集中哈 哈 哈并不多
		line = line.replace('哈 哈', '哈哈')

	print 'end biaodian'
	return line.decode('utf-8')


# 4、网址邮箱 全文匹配
def deal_url(line):
	print 'deal_url',
	regex=re.compile(r' (((h ?t ?t ?p ?s?)|(f ?t ?p ?)) ?: ?/ ?/ ?)?([a-zA-Z])([a-zA-Z0-9_+ -])+\.([a-zA-Z0-9_+ -])+(:[0-9]{1,4})?((/[ a-zA-Z0-9\&%_\./-~-]*)|(?=[^a-zA-Z0-9\.]))? ')
	text0 = line + ' '
	while len(text0) > len(line):
		text0 = line
		line = regex.sub(lambda m: ' ' + m.group(0).replace(' ', '') + ' ',line)
	line = text0
	print '.',
	regex=re.compile(r' [a-zA-Z0-9][a-zA-Z0-9_ -]+@[ a-zA-Z0-9_-]+(\.[ a-zA-Z0-9_-]*)+[a-zA-Z] ')
	text0 = line + ' '
	while len(text0) > len(line):
		text0 = line
		line = regex.sub(lambda m: ' ' + m.group(0).replace(' ', '') + ' ',line)
	line = text0
	print 'end url'
	return line


def post_process(file_n):

	pwd = os.path.abspath('..')	
	dir_path = pwd[:pwd.rfind('/')] + '/data/test_weighed/' + file_n

	file_o = open(dir_path + '/result/result/wordlist.txt')
	file_r = file_o.read().decode('utf-8')
	wordlist = file_r.split('\n')
	if '' in wordlist:
		wordlist.remove('')
	file_o.close()

	file_o = open(dir_path + '/result/result/train.txt')#打开结果数据
	text = file_o.read().decode('utf-8')
	file_o.close()

	for dirs in os.walk(dir_path + '/result/result/'):    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
		for filename in dirs[2]:
			count = 0
			if re.search(r'results',filename):
				print 'dealing with ' + filename
				save = re.sub(r'results', 'resultp', filename)
				if os.path.exists(dirs[0] + '/' + save):
					continue
				file_o = open(dirs[0] + '/' + filename)
				test = file_o.read().decode('utf-8')#每行都全部处理一下
				file_o.close()

				test = deal_bd(test)
				test = deal_url(test)
				#test = deal_comp(test, dir_path)
				print '.',
				for words in wordlist:#先查看结果中是否存在不可分的词错分了
					word = ' ?'.join(list(words)) 
					reg = re.compile('( ' + word + ' )')
					result = reg.findall(test)
					for r in result:
						test = test.replace(r, ' ' + words + ' ')#把匹配到的词替换成合成词
				print '.',
				tests = test.replace('\n',' ')
				tests = re.sub(r'( )+',' ', tests)
				ww = list(set(tests.split(' ')))

				for w in ww:#单字词不做处理，纯数字也不做处理
					if len(w) < 2 or re.compile(u'[^0-9a-zA-Z\u4E00-\u9FA5]').findall(w) or not re.compile(u'[^0-9]').findall(w):#若全为
						ww.remove(w)

				print '.',
				for w in ww:
					if not text.find(' ' + w + ' '):#若训练数据集中未找到该词
					#那么查看训练集中是否存在 ' ?'.join(list(w)) 的情况，若有则分开，否则pass
						w1 = ' ?'.join(list(w))
						reg = re.compile('( ' + w1 + ' )')
						result = reg.findall(text)
						#当然如果存在多个比如 abc-》a bc 或ab c随便取一个
						if len(result) > 0:
							test = test.replace(' ' + w + ' ', result[0])
				print '.',
				test = deal_bd(test)
				test = deal_url(test)
				print 'end'
				file_w = open(dirs[0] + '/' + save, 'w')
				file_w.write(test.encode('utf-8'))
				
				file_w.close()

if __name__ == '__main__':
	
	if len(sys.argv) != 2: 
		sys.exit(2)
	try:
		file_n = sys.argv[1]
	except IOError:
		sys.stderr.write("ERROR: please input dealed dir %s.\n" % arg)
		sys.exit(1)

	print 'start.'
	post_process(file_n);

	print 'successfull!!'