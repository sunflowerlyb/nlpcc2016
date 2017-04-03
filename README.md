nlpcc2016－Chinese Word Segmentation for Weibo Text
=========

## 说明
本程序是我们参加nlpcc2016的中文切分任务的系统。


## 简介
   中文信息处理一般以词为单位,但其书写方式并不像西方语言那样以空格隔开, 因此中文分词就成了其他中文信息处理的基础,并且在很多领域都有广泛的 应用,包括搜索引擎、机器翻译(MT)、语音合成、自动分类、自动摘要、自动校对等等。经过多年的研究,汉语自动分词技术在处理传统文本语料上取得了不错的成绩。然而,这些分词方法在处理网络文本上却达不到要求,其主要原因是 传统的文本主要来自于比较规范的新闻报道和文学作品,缺乏大量的网络词汇。
中文的分词的方法,从基于字典的方法如最大匹配 (BDMM)到基于统 计的方法如隐含马尔科夫模型(HMM)、条件随机场,取得了一系列的进展。实验表明,序列标注的方法在中文分词任务中取得了很好的效果。其中条件 随机场(CRF)模型没有隐马尔可夫模型的独立性假设条件,因而可以容纳任 意的上下文信息。同时,由于 CRF 计算全局最优输出节点的条件概率,克服了最大熵模型的标记偏置问题,可以更好的拟合真实世界的数据,因此被广泛的 应用到汉语自动分词中,并取得了不错的效果。因此本次评测我们选择在基于字的条件随机场模型的基础上,进行微博数据的分词研究。

## 方法
本问采用
