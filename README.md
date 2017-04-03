NLPCC2016－Chinese Word Segmentation for Weibo Text
=========
## 说明
* 本程序是我们参加[nlpcc2016](http://tcci.ccf.org.cn/conference/2016/pages/page05_evadata.html)的微博中文切分任务所使用的系统。
* 语言环境：python2.7.10
* CRF模型工具包：[CRF](https://taku910.github.io/crfpp/)

## 系统流程介绍
### 本系统采用条件随机场训练模型，包括三个步骤
* 特征提取，生成特征训练数据
* 根据训练数据训练得到分词模型
* 使用模型对文本进行切词
  
## 代码实现
### 特征提取，生成训练数据
* 由coding/generate_feature.py提取特征并生成训练数据
    * 数据准备及说明(各特征的意义參考论文：A Feature-Rich CRF Segmenter for Chinese Micro-Blog.pdf)
        * data文件夹
            ----
            * 官方发布数据，文件格式如官方给出文件，不需要做预先做任何处理
                * 训练数据文件名是固定的：train.dat
                * 发展集数据文件名：dev.dat
                * 测试集文件名：test.dat
            ----
            * 生成特征所需要的其他文件（均为open任务设置的额外数据，在semi及closed任务上，这些特征都是自动提取train.dat中的数据，对应的文件置空即可）
                * dictionary.txt : 用于open任务上的字典特征（评测未用该特征，改用了字典位置特征），如果额外的数据生成此特征，则将对应的词加入该文件，每行一个词。如果不需要将此文件夹置空即可
                * ext.txt :  同样用于open任务上的数据，用于生成条件熵的语料，数据为切好词的数据（格式同train.dat），如果不需要将此文件夹置空即可
                * freq.txt : 用于生成词频的文件，计算字典位置特征，内容为train.dat如果需要更多的语料，则直接追加到该文件中即可
                * text.txt : av特征为非监督特征，如果不存在该文件，系统直接使用train.dat生成av相关的数据（closed任务），在open任务上，如果需要增加额外的数据，则将数据直接拷贝到该文件中即可，系统会自动预处理空格。                    
                * freq.txt : 用于生成词频的文件，计算字典位置特征，内容为train.dat如果需要更多的语料，则直接追加到该文件中
            ----
            * 生成的训练数据
                * train.data: 提取过特征的训练数据
                * dev.data：提取过特征的发展集数据
                * test.data：提取过特征的测试集数据
            ----
            * 生成的中间数据，是为了下次生成数据方便，系统会自动检测是否存在对应的中间文件，如果不存在会自动生成，否则不予重复生成。因此如果需要重新生成，只需要手工删除即可，存储中间数据的目的是为了更快的生成训练数据，比如av特征程序执行较慢，若没次都执行会严重影响开发效率，只有当对应的生成该特征的数据改变时才重新执行（直接删除即可）
                * av_save.json：av特征对应的av值中间数据文件，为了下次生成数据方便，会在第一次执行的时候自动生成。如果需要重新生成，只需要手工删除即可。
                * dict_feat.json: 生成的字典特征中间数据文件，为了下次生成数据方便，会在第一次执行的时候自动生成。如果需要重新生成，只需要手工删除即可。
                * dict_prob_feat.json：生成的字典位置特征中间数据文件，为了下次生成数据方便，会在第一次执行的时候自动生成。如果需要重新生成，只需要手工删除即可。
                * ef_feature.json: 条件熵特征中间数据文件，为了下次生成数据方便，会在第一次执行的时候自动生成。如果需要重新生成，只需要手工删除即可。
                * fredist.json: 根据freq.txt生成的词频文件
                * sa.json: 根据前缀字符串算法的到的整个文件的排序结果。
            ----
    * 生成训练数据：data文件夹和generate_feature.py必须在同级文件夹
         * 直接执行python generate_feature.py
         * ![generate feature](https://github.com/sunflowerlyb/nlpcc2016/raw/master/others/generate_feature.png)
### 根据训练数据训练模型
* 训练数据说明
    * 由上一步得到的训练数据格式如下
    * ![train data](https://github.com/sunflowerlyb/nlpcc2016/raw/master/others/train_data.png) 
    * 文件格式描述
        * 每行对应13位特征值
        * 从左到右，具体特征含义及计算方法见论文 
            * 第1位字特征
            * 第23456共五位对应五个av特征
            * 第7位字类型特征
            * 第8位表概率特征
            * 第9表当前字和前一个字是否为叠字
            * 10、未用
            * 第11、12位表前后熵特征
            * 第13位表字类型特征（字向量训练好之后open会使用该特征）

* 使用训练数据训练模型
    * 训练模型的命令：crf_learn -m 2000 -p 6 template train.data result/template_model > result/log/log_template.txt&
        * -m表示最大迭代次数，本系统设置为2000
        * -p表示开启的进程数可以根据服务器使用情况改变
        * template表示模版
        * 训练的模型存在result问价下，并将训练日志存入log文件
### 使用模型切词
* 同样使用用coding/generate_feature.py提取测试数据特征并生成和训练数据相同格式的文件tests.data
* 使用模型进行标注的命令crf_test -m result/template_model tests.data>result/template_model_tests.txt&
    * -m表示使用的模型文件
    * tests.data表示已经提取完特征需要预测的文本文件名，将预测结果存入result/template_model_tests.txt
# 以上为整个系统流程，谢谢～
