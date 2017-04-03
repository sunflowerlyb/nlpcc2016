nlpcc2016－Chinese Word Segmentation for Weibo Text
=========
## 说明
* 本程序是我们参加[nlpcc2016](http://tcci.ccf.org.cn/conference/2016/pages/page05_evadata.html)的微博中文切分任务所使用的系统。

## 系统流程介绍
* 本系统采用条件随机场训练模型，包括三个步骤
 * 特征提取，生成特征训练数据
 * 根据训练数据训练得到分词模型
 * 使用模型对文本进行切词
  
## 代码实现
* 特征提取，生成训练数据
* 根据训练数据训练模型
* 使用模型切词
