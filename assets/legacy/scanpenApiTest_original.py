# -*- coding: utf-8 -*-
__author__ = "bszheng"
__date__ = "2025/7/24"
__version__ = "1.0"
# 获取项目根目录的绝对路径

import argparse
import datetime,random,json,serial
import re,os,sys,time,uuid,logging
import subprocess
import traceback
import threading
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
# from common.Common_Func import *

txtInfo={
  "40": {
    "chinese": [
      "一大堆邻居挤在门口，只听得",
      "因为是成年人，没有人去理会",
      "限寂寞。传说中的正宗巧克力",
      "一定牵肠挂肚。但是方中信…",
      "我留意她的神情，知道危险时",
      "过身来向他求情，看到他的面",
      "格都没有了。我喃喃念着方中",
      "百宝。但无法找到爱梅的父亲",
      "信她也看得出，我是何等失望",
      "设法照应我。我都想起来了，",
      "以及所有爱她的人都会失踪。",
      "比我们进步多少，却开口闭口",
      "见面会的地点是那位先生的家",
      "清脆的笑语声，才能拯救成年",
      "完之后不到一会儿又打回原形",
      "镂空花纸上，刚自机器间出来",
      "祖母是什么病？我搜索枯肠也",
      "没好好的吃，也不肯好好的睡",
      "我怎么敢耍你，我还要命呢",
      "这是什么话，是你自己挑的"
    ],
    "english": [
      "make twenty-eight. I haven‘t time to light it",
      "six months that they need for digestion. I pond",
      "feet dangling. And I heard him say: Then you don",
      "at will please them. But do not waste your time on",
      "cerned with matters of consequence. I have live",
      "site direction. Are they coming back already?",
      "bove the place where I came to the Earth. a year ag",
      "understands everything. even books about chil",
      "ling-can of fresh water. So. he tended the flowe",
      "sketch of a muzzle. And as I gave it to him my heart",
      "know who he is. If this should happen. please com",
      "autiful you are! Am I not? the flower respond",
      "often neglected. said the fox. It means to esta",
      "them.Whenever I met one of them who seemed to me a",
      "the sheep to eat the little baobabs? He answere",
      "selling those? asked the little prince. Beca",
      "he gifts I received. The men where you live. say",
      "was reviving little by little. Dear little man",
      "The orders are that I put out my lamp. Good evenin",
      "money does his father make? Only from these fig"
    ],
    "number": [
      "89021000 g500克0.1 kgJan 15. 20236709922239",
      "15/01/20231000 g2023年1月15日883615/01",
      "31082023年1月15日4212487215/01/202315",
      "0.25分钟2023-01-152023年1月15日2.52",
      "69641 meter15-Jan-20232023年1月15日15/",
      "2023-01-15500 gJan 15. 20232023年1月15日",
      "40990.1 kg2023年1月15日2330.25分钟38",
      "1小时2.5公斤0.25 min500 g-10°CJan15. 2",
      "2023年1月15日891032541.5 m850524725604",
      "2023年1月15日1小时30882023年1月15",
      "1.5小时2023年1月15日15852023年1月",
      "15-Jan-202397715-Jan-20231000克185615-J",
      "2902558115562.5 kg49292119190111624423762",
      "487530 min1 meter2023-01-15500克0.5公里",
      "8583-10°C2023年1月15日2023-01-154390",
      "15/01/202310 cm2023年1月15日329015/01/",
      "0.1千克500克86531.5小时76815/01/202",
      "2023年1月15日4676100毫米1 hour436920",
      "4614979100 mm93762023年1月15日2023年1",
      "3674641130971 hour2461000克2023年1月15"
    ],
    "mixed": [
      "usand miles from any inhab一排矮树开着花",
      "大家好松口气the tippler. Forget what",
      "用手托着头，le prince. it is not very i",
      "带着超时代武ith three petals. a flower",
      "多地球人肯拼ers of consequence. There",
      "ave so much to do! I am conce宝藏并不在这",
      "make a splendid spectacle奇的探头出去",
      "awned. He was regretting 君毅说：将",
      "al is invisible to the eye.无疑问。他",
      "你的外公呢？at I have watered; because",
      "之外还有什么e. Straight ahead of him.",
      "ndemn him to death. Thus hi才可以帮你？",
      "她说话已相当lf. nevertheless: It may",
      "make my portraits as true 跟一切日子一样",
      "要先在你身上have not been altogether h",
      "来越大声。—he has only four thorns to do",
      "生婴儿如一只.If Your Majesty wishes t",
      "now that yours is unique in什么关系？刚",
      "ed the wall just in time to c？”老方问。",
      "可要求做爱梅in more important details"
    ],
    "mixed_with_number": [
      "you have tamed m说：“我0.1 kg1000克691",
      "口，半边ve it to him my he19652023年1月",
      "都是生命by chance that o0.5公里202311",
      "1677500 g8284286来同你住ot forget it. Yo",
      "应该喜悦ished from the r28562023年1月",
      "ittle by little方中信。15-Jan-20239946",
      "的生命还2023-01-1513371proud of being a",
      "1kg77799186-10C说：“老ue in all the wor",
      "1.5小时2023-0ng Number Two lo是母亲的",
      "mber it. And so I1米7288零下1说出这么",
      "15/01/20231.525the stars. It is为国家图",
      "加工生产ur baobabs-- th36372023年1月",
      "赖。我说plained anythi953036992023年",
      "570345秒89222.用未追踪at is why. at the",
      "body at all ever2023-01-1520231前生的事",
      "尽是过去forgetting. to2023年1月151-",
      "罢他回房dea before any o665630629083100",
      "rince responde1.5小时813041我气馁。",
      "带球走路times in one day467558215/01/20",
      "1.5 h25°C202311earned that new一了百了"
    ]
  },
  "120": {
    "chinese": [
      "磨得憔悴。我无限怜惜的看住她，不由得伸手去握住她的手。可能是第六感影响她，她说：",
      "官贵人见得太多，他的身份亦跟着高贵起来，一般普通访客他不放在眼内了。“找谁？”他",
      "富比拍卖买来，平时只舍得取出摸一摸瓶子，你明自吗？”猥琐，我竟落在这种小人手中，",
      "彩的霓虹光管，在嘉年华会中，我们也用来哄孩子们欢心。我颓然倒向座垫，要不是嘴里还",
      "张开嘴，耸动头部，一般热气喷出来，吓得我连退三步。老方大笑。我悻悻地。“没见过亚",
      "不要你。”“我远远跟在你身旁好不好，绝不打扰你。”他对我倒是千依百顺。我出门缓缓",
      "紧搂住我脖子，我挤上救伤车。车上设备之简陋，使我不由得一愣。外婆气若游丝，我却无",
      "令许多人快乐的行业。”“你真的那么想？”他欣悦。我点点头。“谢谢你，陆小姐，”他",
      "在那里，他死心不息要对我好，即使我来到另一个世界，他还设法照应我。我都想起来了，",
      "中信认为我们开头做得很好，已争取到外婆的同情。“以后你出现就不会突兀，”他说：“",
      "我每年都去扫墓。”“我想去。”“同你有什么关系？刚出院，热辣辣的天气，日头一照中",
      "对社会有贡献。即使在五十年后，我们仍然可以成为好朋友，他这种性格的人，越老越可爱",
      "零食给我吃，带我走到动物园附近。间隔倒也宽畅，但对笼中兽来说，又是另外一件事。老",
      "第10章啊，母亲童年时所遇见的神秘女客，她的身份已经明朗，她是我，她是我，她是母亲",
      "只要按一个钮，却任由饥荒地震带走千万人性命，还有什么大自然的定律可言？”纳尔逊与",
      "有的都是得不到的爱。”夫人笑着责怪说：“你看你为老不尊的样子。”他哈哈笑起来，象",
      "是个爱说话的人。原医生并没有与我攀谈，他在阅读笔记。我最无聊，睡又睡不着，又不想",
      "没有注意这段新闻，嘿，还说我笨，他自己才愚不可及，太空垃圾不加以控制，将来吃苦的",
      "买了图片说明书，向小爱梅朗诵出来。不一会儿身边聚集一大堆小朋友，他们都听故事来了",
      "方大大，他们班上的小同学时常这样顽皮，算不得真，不必紧张，那个陆君毅更是顽皮得全"
    ],
    "english": [
      "rembling water. I am thirsty for this water. said the little prince. Give me some of it to drink... And I understood what he had been looking f",
      "And they will think you are crazy. It will be a very shabby trick that I shall have played on you... And he laughed again. It will be as if. in place",
      "... do me that kindness... Order the sun to set...If I ordered a general to fly from one flower to another like a butterfly. or to write a tragic d",
      "Millions of what? The businessman suddenly realized that there was no hope of being left in peace until he answered this question. Millions",
      "more entertaining than the visit to the king. the little prince said to himself. And he began again to clap his hands. one against the other. The",
      "one dare not disobey. Absurd as it might seem to me. a thousand miles from any human habitation and in danger of death. I took out of my pocket a shee",
      "might be extinguished by a little puff of wind... And. as I walked on so. I found the well. at daybreak. [ Chapter 25 ]finding a well. the narrator a",
      "Water may also be good for the heart...I did not understand this answer. but I said nothing. I knew very well that it was impossible to cross-ex",
      "that there was nothing more fragile on all Earth. In the moonlight I looked at his pale forehead. his closed eyes. his locks of hair that trembled",
      "it was impossible to cross-examine him. He was tired. He sat down. I sat down beside him. And. after a little silence. he spoke again: The stars a",
      "He believed that he would never want to return. But on this last morning all these familiar tasks seemed very precious to him. And when he watere",
      "And if the planet is too small. and the baobabs are too many. they split it in pieces... It is a question of discipline. the little prince said to",
      "ill make you a present of a secret. The little prince went away. to look again at the roses. You are not at all like my rose. he said. As yet you ar",
      "king for chickens? No. said the little prince. I am looking for friends. What does that mean-- tame? It is an act too often neglecte",
      "and the secrets of your sad little life... For a long time you had found your only entertainment in the quiet pleasure of looking at the sunset. I l",
      "It is better. like that. My star will just be one of the stars. for you. And so you will love to watch all the stars in the heavens... they will all be",
      "herself against the world. And I have left her on my planet. all alone! That was his first moment of regret. But he took courage once more. What p",
      "eat consequence. On matters of consequence. the little prince had ideas which were very different from those of the grown-ups. I myself own a",
      "back at the same hour. said the fox. If. for example. you come at four o‘clock in the afternoon. then at three o‘clock I shall begin to be hap",
      "more to drink; and I. too. should be very happy if I could walk at my leisure toward a spring of fresh water! My friend the fox-- the little princ"
    ],
    "number": [
      "150248292023年1月15日15-Jan-20231000 g1.5米1091100华氏度60062023年1月15日30491米7649113520492023年1月15日20",
      "48801612100华氏度95841小时1 kg2.5公斤1.5小时15-Jan-202311121.5 h15-Jan-202370470.5公里15/01/2023500 g53160.25分",
      "8491717515-Jan-202310厘米15-Jan-2023225258282023年1月15日Jan 15. 20232023年1月15日2023年1月15日2023年1月15日",
      "15/01/20231282-10°C1小时2023-01-1545 sec92285150238169035540-10°C0.5公里2659Jan 15. 202378927574650599515-Jan-2023392",
      "15-Jan-20230.1 kg423125摄氏度45秒45 sec15/01/202325摄氏度25摄氏度Jan 15. 2023299630 min96381000克30 min100华氏度",
      "2.5 kg8750588329118951.5小时855567921.5 m100华氏度152311.5 m2.5 kg15/01/20232023年1月15日79502023年1月15日9596606",
      "2023-01-1525°C6400927212742251014530568002023年1月15日15-Jan-2023零下10度2023年1月15日0.25分钟4106693611181 k",
      "100毫米2023年1月15日15-Jan-2023Jan 15. 20230.1千克7707934925851.5 h15/01/2023-10°C1小时2023-01-1591100.1千克1.5",
      "2023年1月15日201915-Jan-20232023-01-15500克46272023年1月15日5362023年1月15日59062023年1月15日2023-01-158120",
      "85142023年1月15日2023-01-1515-Jan-202315/01/20232023年1月15日582615-Jan-2023Jan 15. 20238625195930分钟6938Jan15. 20",
      "321398870.25分钟2578100°F2023年1月15日2.5公斤92171小时2023年1月15日98652023年1月15日15/01/20232023年115",
      "19891 kg664627162023-01-15100 mm55234830685225612023年1月15日15/01/202325°C4162704032412023年1月15日100华氏度0.1",
      "979455951795900.1千克100毫米2023-01-1513392023年1月15日2023-01-15660130 min839059304360Jan 15. 202315-Jan-2023Jan 15. ",
      "0.5 km70991 kg1.5 m42172023年1月15日1.5米15/01/20232023年1月15日0.25分钟45秒52零下10度0.1 kg5968100毫米202311",
      "1516924325摄氏度15/01/20232023年1月15日5976Jan 15. 202399692023年1月15日2023年1月15日Jan 15. 2023100华氏度500 ",
      "1 hour1 hour43722023年1月15日1000 g4170Jan 15. 20239285100华氏度1.5米2023年1月15日15-Jan-202330 min2023年1月15日1",
      "330615/01/20230.25 min0.25 min15/01/20232023年1月15日1000 g92682023年1月15日2023年1月15日2023年1月15日2023年11",
      "2023-01-1537462023年1月15日1.5 m368833562023-01-157291小时2023年1月15日Jan 15. 20232023年1月15日346615-Jan-20230",
      "2023年1月15日7097100华氏度1米2023年1月15日2023-01-15-10°C0.25分钟0.5 km96042023年1月15日0.1千克100华45",
      "1米15/01/20232023年1月15日25摄氏度2023-01-15500克零下10度19342023年1月15日54268724100华氏度0.5公里15/"
    ],
    "mixed": [
      "ain more important details I shall make mistakes. also. But that is some底一寒，“我们不谈这个。”“好，我同你到",
      "之外，根本不用搞人事关系，人们可以专注工wn-ups. and asked them whether the drawing frightened them.But they an",
      "k to his idea. My life is very monotonous. the fox said. I hunt chicken工厂一行，临走时千叮万嘱。我躺在床上假寐",
      "are you trying to say? In one of the stars I shall be living. In one of the怕你会寂寞。”那是一定的，虽没有开口，眼",
      "陆宜。”“或许你应当注意心脏，人造心脏并He laughed. touched the rope. and set the pulley to working. And the pull",
      "uch annoyed. he said to himself. if she should see that... she would co怔，不过立刻明白了，她脸上露出颇为同情的",
      "ent career as a painter. I had been disheartened by the failure of my Draw表情。这个时候，我才知道，老方是怕我多心",
      "- you were strolling along like that. all alone. a thousand miles from an“小妹，真看不出你这么大方，我一定补偿你",
      "方中信为我难过，他双手扬在裤袋里，欲言无a little from the truth. I have not been altogether honest in what I have t",
      "上配仪器零件到底不自然，我知道有人引此为that were stretched out before us in the moonlight. The desert is beaut",
      "secret: It is only with the heart that one can see rightly; what is essent全抽不出空来，并不是没有时间，为什么随她",
      "re you trying to say? In one of the stars I shall be living. In one of them帮你。”“联络你的国防部。”“你不明自，",
      "浪费时间金钱。母亲一坐下便问我要饮料。我ould pretend that she was dying. to avoid being laughed at. And I should b",
      "over the whole of the six continents. a veritable army of 462.511 lampli偷将一枚糖果与一枚铜市包在锡纸内，藏到车",
      "It was that of the boa constrictor from the outside. And I was astounded t到这里，我浑身颤抖起来，这么算来，我岂不",
      "。我震惊地呆坐。五十年就这么过去了，物是swer. And the little prince went away. The grown-ups are certainly alt",
      "en he got up. He took one step. I could not move. There was nothing but a fla方轻轻跟音乐吟唱：“渴睡的礁溯，在热带的",
      "ater. If you would have the kindness to think of my needs-- And the litt来探望她。”他今日似乎正经得多。“你可以",
      "said the little prince. so that he would be sure to remember. Men have f心翼翼地侍候，又轻轻放下，这项工作似乎给",
      "接到一座公园内，我们坐在树荫下谈了许久，ink that she has tamed me... It is possible. said the fox. On the Eart"
    ],
    "mixed_with_number": [
      "1千克1000 g2023年1月15日1 meter5221206一个神经兮兮的小伙子没好感Ah! I am scarcely awake. I beg that you will excu",
      "320344174047Jan 15. 202315-Jan-20232023-01-es: is it yes or no? Has the sheep eaten the flower蠢如猪，为什么为什么，一天",
      "眼睛也露消息，他并不担心自is ankle. He remained motionless for an instant92675305Jan 15. 2023Jan 15. 20234415100华氏",
      "“好的。”我渐渐堕人黑暗中perly astonished to see you laughing as you look14992023年1月15日757100°F0.25 min43562",
      "把你送回去。”我摔开他的手5449Jan 15. 20235906Jan 15. 2023387913241000 ged all the affection that lay behind her poor lit",
      "10厘米0.25 min0.1千克Jan 15. 2023零下1不可以共度一辈子的。家人都ed to the story of the merchant as I was drinking t",
      "Jan 15. 20232023年1月15日2023年1月1575e was in Turkish costume. and so nobody would bel意。方中信因为是成年人，没",
      "10 cm10662023年1月15日2023年1月15日7十来夭，他对你怎么样，相信astrophe. I knew a planet that was inhabited by a",
      "25°C1 kg22642023年1月15日98922023年11听腻。”我静默的坐下来，第ay. if you grow too homesick for your own planet.",
      "ing of his flower. [ Chapter 16 ]the narrator dis错，我给你试试。”她把双手15-Jan-20232023年1月15日15/01/20236148",
      "“小妹妹，珍惜你的本钱，好2023年1月15日25583181Jan 15. 202315-Jan-ir steps in the dance. and then they too would be w",
      "5223零下10度44488866100 mm0.25 min640286玩笑好不好，你看你，头发那portant! He could not say anything more. His wo",
      "eatures. This one might bite you just for fun...道你是好人还是坏人？”“即0.5 km967715/01/2023517565112023年1月151 ",
      "olden curls in the breeze. I know a planet where温柔他说：“看，又触动他的15-Jan-20239154100华氏度-10°C100华97",
      "北美洲大陆的天空及太空袭击ge of such a na秭e untruth. she coughed two or th2023年1月15日2023年1月15日Jan15.202",
      "25°C 1米零下10度37902023年1月15日2e. and his colleague who was responsible for the吵，糟蹋能源，造成空气传染",
      "2023-01-152023年1月15日9824100 mm0.5公“妈妈，新闻报告说第四空间ttle prince discuss his return to his planet Me",
      "2023年1月15日0.25分钟15/01/202320231她仿佛想穿了，同我说，她希elf and begin-- timidly at first-- to push a char",
      "可，我并没，也不打算爱他，79821000克-10°C25摄氏度15/01/2023552e figures do they think they have learned anythi",
      "未曾注意的事物，都震荡心扉28352023年1月15日15/01/2023100°F20231ery fragile treasure. It seemed to me. even. tha"
    ]
  }
}


def get_serial(port, baudrate=115200, time_out=0.5):
    """
    实例化串口对象
    :param port: 串口名，如 "COM87"
    :param baudrate: 默认115200
    :param time: 超时时间，默认0.5s
    :return: 串口实例化对象
    """
    serials = ""
    try:
        # serials = serial.Serial(port, baudrate,timeout=0.5,
        #                         parity=serial.PARITY_NONE,
        #                         stopbits=serial.STOPBITS_ONE,
        #                         xonxoff=0,writeTimeout=1,
        #                         rtscts=0)  # /dev/ttyUSB0
        serials = serial.Serial(port, baudrate, timeout=time_out)

    except Exception as e:
        print(f"串口连接出错，出错信息{e}")
    return serials


def saveFile(fileName, info, wType="w+"):
    with open(fileName,wType,encoding='utf-8',errors='ignore') as fp:
        fp.write(info)
# 生成文件夹
def createdirs(path):
    isExists = os.path.exists(path)  # 判断是否已存在目录
    if isExists == True:
        pass
    else:
        os.makedirs(path)
def load_json(file):
    """
    Load json file and switch to python dict type
    :param file: file name
    :return: python dict
    """
    with open(file, "r+", encoding="utf-8") as fp:
        content = json.load(fp)
    return content
class TextGenerator:
    def __init__(self, chinese_file: str = "zw.txt", english_file: str = "yw.txt"):
        self.chinese_file = chinese_file
        self.english_file = english_file
        self._validate_files()
        
        # 加载并清理文件内容（去除换行符）
        self.raw_chinese = self._load_and_clean_file(chinese_file)
        self.raw_english = self._load_and_clean_file(english_file)
        
        # 预处理去除空格后的文本（用于长度计算）
        self.chinese_clean = self.raw_chinese.replace(' ', '')
        self.english_clean = self.raw_english.replace(' ', '')
        
        # 标点符号库（中英文）
        self.punctuations = {
            'chinese': ['，', '。', '；', '：', '？', '！', '「', '」', '『', '』', '、'],
            'english': [',', '.', ';', ':', '?', '!', '"', "'", '(', ')', '-']
        }
        
        # 增强的日期和单位数据（带中英文转换）
        self.date_formats = [
            ("2023-01-15", "2023年1月15日"),
            ("15/01/2023", "2023年1月15日"),
            ("Jan 15, 2023", "2023年1月15日"),
            ("15-Jan-2023", "2023年1月15日")
        ]
        
        self.units = {
            "length": [
                ("1 meter", "1米"), ("10 cm", "10厘米"), ("100 mm", "100毫米"),
                ("1.5 m", "1.5米"), ("0.5 km", "0.5公里")
            ],
            "weight": [
                ("1 kg", "1千克"), ("500 g", "500克"), ("2.5 kg", "2.5公斤"),
                ("0.1 kg", "0.1千克"), ("1000 g", "1000克")
            ],
            "time": [
                ("1 hour", "1小时"), ("30 min", "30分钟"), ("45 sec", "45秒"),
                ("1.5 h", "1.5小时"), ("0.25 min", "0.25分钟")
            ],
            "temperature": [
                ("25°C", "25摄氏度"), ("100°F", "100华氏度"), ("-10°C", "零下10度")
            ]
        }

    def _validate_files(self):
        if not os.path.exists(self.chinese_file):
            raise FileNotFoundError(f"中文文件 {self.chinese_file} 不存在")
        if not os.path.exists(self.english_file):
            raise FileNotFoundError(f"英文文件 {self.english_file} 不存在")

    def _load_and_clean_file(self, file_path: str) -> str:
        """加载文件并移除所有换行符"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().replace('\n', '')

    def _get_byte_length(self, text: str) -> int:
        """计算UTF-8编码下的字节长度"""
        return len(text.encode('utf-8'))

    def _get_effective_byte_length(self, text: str) -> int:
        """计算不含空格的字节长度"""
        return self._get_byte_length(text.replace(' ', ''))

    def _get_random_segment(self, text: str, clean_text: str, target_bytes: int) -> str:
        """
        从文本中获取指定字节长度的片段（空格不计入长度）
        每次调用都从全新的随机位置开始
        """
        if target_bytes <= 0 or len(clean_text) == 0:
            return ""
        
        # 计算clean_text中的字节位置映射
        byte_positions = []
        current_byte_pos = 0
        for i, char in enumerate(text):
            if char != ' ':
                byte_positions.append((i, current_byte_pos))
                current_byte_pos += self._get_byte_length(char)
        
        if not byte_positions:
            return ""
        
        # 随机选择起始字节位置
        max_start_byte = max(0, current_byte_pos - target_bytes)
        if max_start_byte <= 0:
            return text
        
        start_byte = random.randint(0, max_start_byte)
        
        # 找到起始字符位置
        start_idx = 0
        for i, (char_idx, byte_pos) in enumerate(byte_positions):
            if byte_pos >= start_byte:
                start_idx = i
                break
        
        # 收集满足字节长度的字符
        result = []
        remaining_bytes = target_bytes
        collected_bytes = 0
        text_pos = byte_positions[start_idx][0]
        
        while remaining_bytes > 0 and text_pos < len(text):
            char = text[text_pos]
            if char != ' ':
                char_bytes = self._get_byte_length(char)
                if char_bytes <= remaining_bytes:
                    result.append(char)
                    remaining_bytes -= char_bytes
                    collected_bytes += char_bytes
                else:
                    break  # 当前字符超出剩余字节数
            else:
                result.append(char)  # 保留空格但不计入长度
            
            text_pos += 1
        
        return ''.join(result)

    def _get_random_punctuation(self, lang: str = 'mixed') -> str:
        """获取随机标点符号"""
        if lang == 'chinese':
            return random.choice(self.punctuations['chinese'])
        elif lang == 'english':
            return random.choice(self.punctuations['english'])
        else:
            return random.choice(
                self.punctuations['chinese'] + self.punctuations['english']
            )

    def _get_random_date(self, bilingual: bool = False) -> str:
        """获取随机日期（支持中英文双语）"""
        date_pair = random.choice(self.date_formats)
        return random.choice(date_pair) if not bilingual else f"{date_pair[0]}/{date_pair[1]}"

    def _get_random_unit(self, bilingual: bool = False) -> str:
        """获取随机单位（支持中英文双语）"""
        category = random.choice(list(self.units.keys()))
        unit_pair = random.choice(self.units[category])
        return random.choice(unit_pair) if not bilingual else f"{unit_pair[0]}/{unit_pair[1]}"

    def generate_text(self, text_type: str, byte_length: int) -> str:
        """
        生成指定类型的文本（每次调用都从随机位置开始）
        """
        if byte_length <= 0:
            return ""
        
        if text_type == 'chinese':
            return self._get_random_segment(self.raw_chinese, self.chinese_clean, byte_length)
        
        elif text_type == 'english':
            return self._get_random_segment(self.raw_english, self.english_clean, byte_length)
        
        elif text_type == 'number':
            result = []
            remaining_bytes = byte_length
            
            while remaining_bytes > 0:
                item_type = random.choice(['digit', 'date', 'unit'])
                if item_type == 'digit':
                    item = str(random.randint(0, 9999))
                elif item_type == 'date':
                    item = self._get_random_date()
                else:
                    item = self._get_random_unit()
                
                effective_bytes = self._get_effective_byte_length(item)
                if effective_bytes <= remaining_bytes:
                    result.append(item)
                    remaining_bytes -= effective_bytes
                else:
                    temp = []
                    temp_bytes = 0
                    for c in item:
                        c_bytes = self._get_byte_length(c)
                        if c != ' ' or random.random() > 0.5:
                            if temp_bytes + (0 if c == ' ' else c_bytes) <= remaining_bytes or c == ' ':
                                temp.append(c)
                                if c != ' ':
                                    temp_bytes += c_bytes
                    result.append(''.join(temp))
                    remaining_bytes -= temp_bytes
            
            return ''.join(result)
        
        elif text_type == 'mixed':
            chinese_part = self._get_random_segment(self.raw_chinese, self.chinese_clean, byte_length // 2)
            english_part = self._get_random_segment(self.raw_english, self.english_clean, byte_length - len(chinese_part.replace(' ', '').encode('utf-8')))
            
            parts = [chinese_part, english_part]
            random.shuffle(parts)
            return ''.join(parts)
        
        elif text_type == 'mixed_with_number':
            chinese_part = self._get_random_segment(self.raw_chinese, self.chinese_clean, byte_length // 3)
            english_part = self._get_random_segment(self.raw_english, self.english_clean, byte_length // 3)
            number_part = self.generate_text('number', byte_length - len(chinese_part.replace(' ', '').encode('utf-8')) - len(english_part.replace(' ', '').encode('utf-8')))
            
            parts = [chinese_part, english_part, number_part]
            random.shuffle(parts)
            return ''.join(parts)
        
        elif text_type == 'punctuation':
            result = []
            remaining_bytes = byte_length
            
            while remaining_bytes > 0:
                punc = self._get_random_punctuation()
                punc_bytes = self._get_byte_length(punc)
                if punc_bytes <= remaining_bytes:
                    result.append(punc)
                    remaining_bytes -= punc_bytes
                else:
                    break
            
            return ''.join(result)
        
        elif text_type == 'bilingual_number':
            result = []
            remaining_bytes = byte_length
            
            while remaining_bytes > 0:
                item_type = random.choice(['digit', 'date', 'unit'])
                if item_type == 'digit':
                    num = random.randint(0, 9999)
                    item = f"{num}/{num}"
                elif item_type == 'date':
                    item = self._get_random_date(bilingual=True)
                else:
                    item = self._get_random_unit(bilingual=True)
                
                effective_bytes = self._get_effective_byte_length(item)
                if effective_bytes <= remaining_bytes:
                    result.append(item)
                    remaining_bytes -= effective_bytes
                else:
                    temp = []
                    temp_bytes = 0
                    for c in item:
                        c_bytes = self._get_byte_length(c)
                        if c != ' ' or random.random() > 0.5:
                            if temp_bytes + (0 if c == ' ' else c_bytes) <= remaining_bytes or c == ' ':
                                temp.append(c)
                                if c != ' ':
                                    temp_bytes += c_bytes
                    result.append(''.join(temp))
                    remaining_bytes -= temp_bytes
            
            if random.random() > 0.3 and byte_length > 20:
                mixed_part = self.generate_text('mixed', byte_length // 3)
                result.append(mixed_part)
            
            random.shuffle(result)
            return ' '.join(result)
        
        else:
            raise ValueError(f"不支持的文本类型: {text_type}")



class output_log():
    def __init__(self, level, path, sjc):
        self.level = level
        self.path = path
        self.sjc = sjc
        # 创建logger对象
        self.logger = logging.getLogger('test_logger')
        # 追加写入文件a ，设置utf-8编码防止中文写入乱码
        test_logname = os.path.join(self.path, "output_log_" + self.sjc + ".log")
        self.test_log = logging.FileHandler(test_logname, 'a+', encoding='utf-8')
        if self.level == 1:
            # 设置日志等级
            self.logger.setLevel(logging.DEBUG)
            # 向文件输出的日志级别
            self.test_log.setLevel(logging.DEBUG)
        elif self.level == 2:
            # 设置日志等级
            self.logger.setLevel(logging.INFO)
            # 向文件输出的日志级别
            self.test_log.setLevel(logging.INFO)
        elif self.level == 3:
            # 设置日志等级
            self.logger.setLevel(logging.WARNING)
            # 向文件输出的日志级别
            self.test_log.setLevel(logging.WARNING)
        elif self.level == 4:
            # 设置日志等级
            self.logger.setLevel(logging.ERROR)
            # 向文件输出的日志级别
            self.test_log.setLevel(logging.ERROR)
        elif self.level == 5:
            # 设置日志等级
            self.logger.setLevel(logging.CRITICAL)
            # 向文件输出的日志级别
            self.test_log.setLevel(logging.CRITICAL)
        # 向文件输出的日志信息格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        self.test_log.setFormatter(formatter)

        # 加载文件到logger对象中
        self.logger.addHandler(self.test_log)

    def LOG_DEBUG(self, log):
        # 调试级别的log
        self.logger.debug(log)
        if self.level == 1:
            print(log)

    def LOG_INFO(self, log):
        # 一般信息的log
        self.logger.info(log)
        if self.level <= 2:
            print(log)

    def LOG_WARNING(self, log):
        # 警告信息的log
        self.logger.warning(log)
        if self.level <= 3:
            print(f"\a{log}")

    def LOG_ERROR(self, log):
        # 错误信息的log
        self.logger.error(log)
        if self.level <= 4:
            print(f"\a{log}")

    def LOG_CRITICAL(self, log):
        # 严重错误信息的log
        self.logger.critical(log)
        if self.level:
            print(f"\a{log}")

    def close_file(self):
        # 关闭log文件
        print(f"关闭output_log文件")
        self.logger.removeHandler(self.test_log)
        self.test_log.close()
        logging.shutdown()


# 串口日志处理器
class serThread(threading.Thread):
    def __init__(self, projectInfo, deviceName, deviceInfo, output):
        super().__init__()
        self.projectInfo = projectInfo
        self.deviceName = deviceName
        self.portNum = deviceInfo.get("port", "")
        self.baudRate = deviceInfo.get("baudRate", 115200)
        self.regexMap = deviceInfo.get("regex", {})
        self.serial_data_type = deviceInfo.get("serial_data_type", "serial_data_type")
        # tempT = datetime.datetime.now()
        # timeTag = tempT.strftime("%Y-%m-%d_%H_%M_%S")
        # self.logName = os.path.join(output.path, f"{self.projectInfo}_{self.deviceName}_{self.portNum}_{timeTag}.log")
        self.logName = os.path.join(output.path, f"{self.projectInfo}_{self.deviceName}_{self.portNum}.log")
        self.output = output
        # 初始化需要正则结果的信息容器，一般设备重启或者指定场景需要重置所有信息为初始状态
        self.regexResult = {key: False for key in self.regexMap}
        self.serFp = ''
        self.stop_flag = False
        self.tempMsg = []
        self.currentBootReasonList = []
        self.assertNum = 0


    def regexMatch(self, log_info):
        if not self.regexMap:
            return
        for regexTag, regex in self.regexMap.items():
            if not regex:
                continue
            kw = re.match(regex, log_info)
            if kw:
                try:
                    get_kw = kw.group(1).strip("\r\n ")
                    # TODO 正则到的结果二次处理
                    # 讲结果加入消息队列
                    self.regexResult.update({regexTag: get_kw})
                    if regexTag == 'otaDownloadProgress':
                        continue
                    if "Boot Reason" in regex:
                        self.currentBootReasonList.append(get_kw)
                    self.output.LOG_INFO(f"\t{self.deviceName}: {regexTag}正则匹配结果：{get_kw}")
                except Exception as e:
                    self.output.LOG_ERROR(f"{self.deviceName}的正则表达式{regex}匹配出错，出错信息{e}")

    def getRegexResult(self):
        return self.regexResult

    def cleanRegexResultBuff(self):
        self.output.LOG_INFO(f"清除 {self.deviceName}串口 RegexResultBuff 信息")
        self.regexResult = {key: False for key in self.regexMap}

    def clearSingleRegex(self, regexKey):
        self.output.LOG_INFO(f"清除 {self.deviceName}串口 {regexKey} 信息")
        self.regexResult.update({regexKey: False})

    def getBootReasonList(self):
        return self.currentBootReasonList

    def clearBootReasonList(self):
        self.currentBootReasonList = []

    def serActive(self):
        self.serFp = get_serial(self.portNum, self.baudRate)
        if self.serFp:
            return self.serFp.isOpen()
        else:
            self.output.LOG_ERROR(f"串口{self.portNum}无法连接！")
            return False
        # if not self.serFp.isOpen():
        #     raise EOFError("设备初始化失败")
        # return self.serFp.isOpen()

    def getSerMsg(self):
        return self.tempMsg

    def cleanMsgBuff(self):
        self.tempMsg.clear()

    def serWrite(self, cmd):
        if self.serFp:
            if self.serFp.isOpen():
                self.output.LOG_INFO(f"{self.deviceName}串口输入命令{cmd}")
                cmdHd = f"{cmd}\r\n"
                self.serFp.reset_input_buffer()
                self.serFp.reset_output_buffer()
                # self.serFp.write(f"{cmd}\r\n".encode('utf-8'))
                chunk_size = 32  # 一次发送 32 字节
                for i in range(0, len(cmdHd), chunk_size):
                    self.serFp.write(cmdHd[i:i+chunk_size].encode('utf-8'))
                    time.sleep(0.01)  # 给设备一点处理时间



    def __del__(self):
        if self.serFp:
            if self.serFp.isOpen():
                self.serFp.close()

    def run(self):
        str_info = ""
        buffer = ""
        errorBefore = ''
        if self.serial_data_type == "hex":
            logfile = open(self.logName, "a+")
        else:
            logfile = open(self.logName, "ab+")
        if self.serActive():
            if self.serial_data_type == "hex":
                while not self.stop_flag:
                    try:
                        data = self.serFp.readline()
                        if data:
                            self.tempMsg.append(data)
                            now_time = datetime.datetime.now()
                            str_info = ''.join(['{:02x}'.format(b) for b in data]).upper()
                            buffer += str_info
                            self.output.LOG_DEBUG(f"buffer:{buffer}")
                            kw = re.match(self.deviceInfo['regex']["wakeupkw"], buffer)
                            if kw:
                                info = f"[{now_time}]{buffer}\n"
                                logfile.write(info)
                                logfile.flush()
                                self.regexMatch(buffer)
                                buffer = ""
                    except Exception as e:
                        if "拒绝访问" in str(e):

                            errorinfo = f"串口连接出现问题，请检查{self.portNum}串口是否掉线！！！\n"
                            self.stop_flag = True
                        else:
                            errorinfo = "Error info : %s, Current line : %s\n" % (e, str_info)
                        self.output.LOG_ERROR(f"{errorinfo}")
                    finally:
                        continue
            else:
                while not self.stop_flag:
                    try:
                        # num = self.serFp.inWaiting()
                        # str_info = self.serFp.read(num)
                        str_info = self.serFp.readline()
                        # if self.deviceName == "asrLog":
                        #     print(str_info)
                        #     print("==>:", str_info.decode('iso-8859-1'))
                        if str_info:
                            now_time = datetime.datetime.now()
                            b_info = bytes(f"[{now_time}]", encoding='utf-8') + str_info
                            logfile.write(b_info)
                            logfile.flush()
                            log_info = str_info.decode("utf-8", "ignore")  # 日志内存在不兼容的字符编码，加上ignore忽略异常
                            log_info = ILLEGAL_CHARACTERS_RE.sub('', log_info)  # 去掉非法字符
                            # asr 获取csk数据时，大量的写操作，此处避免将这些数据进入正则
                            if "lega_ota_write" in log_info:
                                continue
                            if "ASSERT" in log_info:
                                self.assertNum += 1
                                self.output.LOG_ERROR(f"当前检测 ASSERT : {self.assertNum}次")
                            self.tempMsg.append(b_info)
                            self.regexMatch(log_info)
                    except Exception as e:
                        if errorBefore != str(e):
                            errorBefore = str(e)
                            if "拒绝访问" in str(e):
                                errorInfo = f"串口连接出现问题，请检查{self.portNum}串口是否掉线！！！\n"
                                self.stop_flag = True
                            else:
                                # traceback.print_exc()
                                errorInfo = "Error info : %s, Current line : %s\n" % (e, str_info)
                            self.output.LOG_ERROR(f"{errorInfo}")
                    finally:
                        continue
            logfile.close()
        else:
            logfile.close()
            self.output.LOG_ERROR(f"{self.portNum}串口连接出错，请重试！！")
            self.stop_flag = True

class apiTest():
    def __init__(self, config, testArgs):
        super().__init__()

        self.config = config
        self.testArgs = testArgs
        # 初始化设备参数
        self.projectInfo = self.config.get("projectInfo", "")
        self.deviceListInfo = self.config.get("deviceListInfo", {})
        self.pinMask = self.config.get("pinMask", '')
        self.usb2xxxNum = self.config.get("usb2xxNum", '')
        self.serFpPools = {}

        # args 外部传参的测试信息
        self.testType = self.testArgs.testType
        self.testNum = self.testArgs.testNum
        self.testLabel = self.testArgs.testLabel
        self.testByte = self.testArgs.testByte
        # 初始化本地结果数据保存目录
        tempT = datetime.datetime.now()
        timeTag = tempT.strftime("%Y-%m-%d_%H_%M_%S")
        self.resultFolder = os.path.join(os.getcwd(), "result", timeTag + "-" + self.testLabel)
        createdirs(self.resultFolder)
        self.resFile = os.path.join(self.resultFolder, "result.txt")
        self.output = output_log(1, self.resultFolder, timeTag)
        self.runTimes = 0
        self.pcmFolder = os.path.join(self.resultFolder, "pcmRes")
        createdirs(self.pcmFolder)

        self.ttsPlayStart = "xtts_play 1"
        self.ttsPlayEnd = "xtts_play 0"
        self.ttsStop = "xtts_stop"
        self.transStop = "trans_stop"


        # if self.testType == 4 and self.usb2xxNum:
        #     showCurrentDev()
        #     self.gpioHandle = usb2xxGpioHandle(self.usb2xxNum, self.output)

        zh_text = "zhxs.txt"
        en_text = "xwz.txt"
        self.generator = TextGenerator(chinese_file=zh_text,english_file=en_text)
    def initSerDevice(self):
        # isDeviceInitDone = True
        if not self.deviceListInfo:
            self.output.LOG_ERROR(f"配置文件中设备信息异常，请检查")
            return
        for deviceName, deviceInfo in self.deviceListInfo.items():
            try:
                if "csk" in deviceName:
                    # 后续烧录完成后会重新初始化句柄，当句柄存在则不用重复初始化
                    if deviceName in self.serFpPools:
                        continue
                    self.output.LOG_INFO(f"开始初始化{deviceName}串口信息")
                    serFpThread = serThread(self.projectInfo, deviceName, deviceInfo, self.output)
                    self.serFpPools.update({deviceName: serFpThread})
                    serFpThread.start()
                    while True:
                        if serFpThread.serFp:
                            if serFpThread.serFp.isOpen():
                                self.output.LOG_INFO(f"{deviceName}串口正常打开！")
                                break
                            else:
                                self.output.LOG_INFO(f"{deviceName}串口打开失败！,清除已打开的设备后关闭退出测试")
                                self.clearSerThread()
                                sys.exit()
                        time.sleep(0.5)
            except Exception as e:
                self.output.LOG_ERROR(f"设备初始化失败{str(e)}")
                # traceback.print_exc()
                self.clearSerThread()
                return
        return True
    # 清除指定串口句柄

    def closeAsrSer(self, serName):
        asrSerFp = self.serFpPools.get(serName, "")
        self.serFpPools = {key: value for key, value in self.serFpPools.items() if key != serName}

        clearStep = 0
        self.output.LOG_INFO(f"清除{serName} 串口信息")
        if asrSerFp.serFp:
            clearStep += 1
            asrSerFp.stop_flag = True
            if asrSerFp.serFp.isOpen():
                asrSerFp.serFp.close()
                self.output.LOG_INFO(f"{serName} 串口信息清除成功")
            if not asrSerFp.serFp.isOpen():
                # asrSerFp.stop_flag = True
                return True
            else:
                time.sleep(0.5)
                self.closeAsrSer(serName)
        else:
            time.sleep(0.5)
            self.closeAsrSer(serName)

    def clearSerThread(self):
        # 清除所有串口句柄
        self.output.LOG_INFO("销毁串口线程和对应串口句柄")
        for serFpName, tempSerFp in self.serFpPools.items():
            tempSerFp.stop_flag = True
            self.output.LOG_INFO(f"清除{serFpName}信息")
            if tempSerFp.serFp:
                if tempSerFp.serFp.isOpen():
                    tempSerFp.serFp.close()
            # tempSerFp.stop_flag = True
        self.serFpPools = {}

    def cmdShell(self, cmdSer, cmd):
        # 串口命令输入
        if cmdSer.serFp:
            if cmdSer.serFp.isOpen():
                cmdSer.cleanMsgBuff()
                cmdSer.serWrite(cmd)
                self.output.LOG_INFO(f"发送命令：{cmd}")
                time.sleep(0.5)

    def shell(self, cmd, purpose="Pull PCM", tag="1 file pulled", timeOut=10):
        # 使用subprocess.Popen执行exe文件并获取输出
        self.output.LOG_INFO(f"当前执行命令：{cmd}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=timeOut)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

        # 将输出从字节转换为字符串
        stdout_str = stdout.decode("utf-8", "ignore")
        stderr_str = stderr.decode("utf-8", "ignore")
        self.output.LOG_INFO(f"\t\t**********{tag} 待验证**********")
        if "error" in stdout_str:
            self.output.LOG_INFO(f"\t\t**********{purpose} 失败， 详细内容:{stdout_str}**********")
            return False
        elif tag in stdout_str:
            self.output.LOG_INFO(f"\t\t**********{purpose} 成功**********")
            return True
        else:
            self.output.LOG_ERROR(f"\t\t**********{purpose} 失败**********")
            self.output.LOG_INFO(f"shell 命令执行输出： {str(stdout_str)}")
            self.output.LOG_INFO(f"shell 命令执行异常： {str(stderr_str)}")
            return False
        
    def checkSerAlive(self, cskFp, cskCpFp):
        # 由于压测的时候串口总是会随机断开，避免压测数据丢失，监测串口连接逻辑，
        # 当串口断开后重新连接串口
        try:
            if cskFp.serFp.isOpen() and cskCpFp.serFp.isOpen():
                return True
        except Exception as e:
            self.output.LOG_INFO(f"串口异常需要重新连接,{str(e)}")
            return False
        return False

    def getTTSCmd(self,role=1,vol=50,speed=50,txt="test",isRandom=0):
        if isRandom:
            role = random.choice([1, 1])          # 从[1, 2]中随机选择
            vol = random.randint(1, 1)        # 从0-100随机整数
            speed = random.randint(50, 50)    # 从0-100随机整数
        return f"xtts_start {role} {vol} {speed} \"{txt}\""
    
    def getTransCmd(self,language=1,txt="test",isRandom=0):
        if isRandom:
            language = random.choice([1, 1])   
        return f"trans_start {language} \"{txt}\""
    
    def checkRes(self,serFp,checkInfo,timeout=80):
        start_time = time.time()
        # timeout = 10  # 10秒超时
        while True:
            # 执行你的检测逻辑
            res = serFp.getRegexResult().get(checkInfo, False)
            if res:  # 如果条件满足
                return res
            # 检查是否超时
            if time.time() - start_time > timeout:
                print(f"操作超时（{timeout}秒）")
                break
            time.sleep(0.2)  # 避免CPU占用过高
        return False
        # self.ttsPlayStart = "xtts_play 1"
        # self.ttsPlayEnd = "xtts_play 0"
        # self.ttsStop = "xtts_stop"
        # self.transStop = "trans_stop"
    def ttsApi(self,infoType,cmd,txt,serFp,serFpCp):
        serFp.cleanRegexResultBuff()
        serFpCp.cleanRegexResultBuff()   
        # self.cmdShell(serFp, self.ttsPlayEnd)
        # time.sleep(0.1)
        self.cmdShell(serFp, self.ttsStop)
        time.sleep(0.5)
        # self.cmdShell(serFp, self.ttsPlayStart)
        # time.sleep(0.1)
        self.cmdShell(serFp, cmd)
        res = self.checkRes(serFp,"ttsEnd")
        ttsInit = serFpCp.getRegexResult().get("ttsInit", False)
        ttsCost = serFpCp.getRegexResult().get("ttsCost", False)
        ttsTotal = serFpCp.getRegexResult().get("ttsSpeed", False)
        resStrlistInfo = f"{infoType},{self.removeCom(txt)},{ttsInit},{ttsCost},{ttsTotal}"
        self.output.LOG_INFO(f"TTS::{resStrlistInfo}")
        saveFile(self.resFile, resStrlistInfo + "\n", "a+")
        # if res:
        #     tempFileName = uuid.uuid4().hex
        #     self.output.LOG_INFO(f"{cmd} 合成文件保存为：{tempFileName}.pcm")
        #     pcmFile = os.path.join(self.pcmFolder, f"{tempFileName}.pcm")
        #     self.shell(f"adb -s FFBBCCDDEE001122 pull /SD:/factory/xtts.pcm {pcmFile}", purpose="Pull PCM", tag="1 file pulled", timeOut=10)
        return res
    
    def getVersionInfo(self, serFp, reTryTimes=10):
        serFp.clearSingleRegex("version")
        while reTryTimes > 0:
            self.cmdShell(serFp, "version\r\n")
            time.sleep(0.5)
            ver = serFp.getRegexResult().get("version", False)
            if ver:
                return ver
            time.sleep(0.5)
            reTryTimes -= 1
        return False

    def transApi(self,infoType,cmd,txt,serFpAp,serFpCp):
        serFpAp.cleanRegexResultBuff()
        serFpCp.cleanRegexResultBuff()
        # self.cmdShell(serFp, self.ttsStop)
        self.cmdShell(serFpAp, " ")
        self.cmdShell(serFpAp, " ")
        time.sleep(0.5)
        self.cmdShell(serFpAp, cmd)

        # self.shell(f"adb -s FFBBCCDDEE001122 shell {cmd}", purpose="Pull PCM", tag="1 file pulled", timeOut=10)

        res = self.checkRes(serFpAp,"transRes")
        transRes = serFpAp.getRegexResult().get("transRes", False)
        transInit = serFpCp.getRegexResult().get("transInit", False)
        transCost = serFpCp.getRegexResult().get("transCost", False)
        transTotal = serFpCp.getRegexResult().get("transTotal", False)
        resStrlistInfo = f"{infoType},{self.removeCom(txt)},{self.removeCom(transRes)},{transInit},{transCost},{transTotal}"
        self.output.LOG_INFO(f"Trans::{resStrlistInfo}")
        saveFile(self.resFile, resStrlistInfo + "\n", "a+")
        if res and transRes:
            return True
        self.output.LOG_ERROR(f"{txt} 翻译异常请查看相关日志")
        return False

    def heartCheck(self,serFp):
        times = 0
        res = False
        while True:
            serFp.cleanRegexResultBuff()
            self.cmdShell(serFp, "version")
            if self.checkRes(serFp,"hearCmdRes",2):
                res = True
                break
            times += 1
            if times == 5:
                break
        return res
    
    def removeCom(self,info):
        try:
            res = info.replace(",","，")
            return res
        except:
            return info
    
    def removeYH(self,info):
        try:
            res = info.replace("\"","'")
            return res
        except:
            return info
    def is_sorted(self,lst):
        return all(int(lst[i]) <= int(lst[i + 1]) for i in range(len(lst) - 1))

   def transHubTest(self,apSerFp,cpSerFp):
        # print("纯中文(30字节)", generator.generate_text('chinese', 40))
        # print("纯英文(30字节)", generator.generate_text('english', 40))
        # print("数字类型(30字节)", generator.generate_text('number', 30))
        # print("中英文混合(30字节)", generator.generate_text('mixed', 30))
        # print("中英数混合(30字节)", generator.generate_text('mixed_with_number', 30))
        # print("纯标点符号(20字节)", generator.generate_text('punctuation', 20))
        # print("双语数字(30字节)", generator.generate_text('bilingual_number', 30))
        # print("混合类型(40字节)", generator.generate_text('mixed_with_number', 40))
        # tempInfo = generator.generate_text('chinese', 40)
        typeList = ['chinese','english','number','mixed','mixed_with_number']
        # typeList = ['english']
        self.resFile = os.path.join(self.resultFolder, "result_trans.txt")
        saveFile(self.resFile, "InfoType,txt,transRes,initTime,costTime,totalTime\n", "a+")

        for size in ["40","120"]:
            tempTimes=0
            allInfo = txtInfo.get(size,{})
            for infoType in typeList:
                tempInfoList = allInfo.get(infoType,[])
                for tempInfo in tempInfoList:
                    if not tempInfo:
                        continue
                    try:
                        self.output.LOG_INFO(f"\t\t^^^^^^^^^^CURRENT TRANS {infoType} {size}BYTE NO.{tempTimes} START^^^^^^^^^^")
                        if infoType == "chinese":
                            tempTRANSCmd = self.getTransCmd(language=1,txt=tempInfo)
                        elif infoType == "english":
                            tempTRANSCmd = self.getTransCmd(language=2,txt=tempInfo)
                        else:
                            tempTRANSCmd = self.getTransCmd(language=1,txt=tempInfo)
                        # print("------------------",tempTRANSCmd)
                        transRes = self.transApi(infoType,tempTRANSCmd,tempInfo,apSerFp,cpSerFp)
                        if not transRes:
                            self.output.LOG_INFO(f"\n********** NO {self.runTimes} TransTest Result Fail **********\n")
                        else:
                            self.output.LOG_INFO(f"\n********** NO {self.runTimes} TransTest Result Pass **********\n")
                        self.runTimes+=1
                        time.sleep(1)
                        if not self.heartCheck(apSerFp):
                            self.output.LOG_ERROR(f"\n********** 串口通信中断，退出脚本 **********\n")
                            break
                        self.cmdShell(apSerFp, " ")
                        self.cmdShell(apSerFp, " ")
                        tempTimes+=1
                    except Exception as e:
                        traceback.print_exc()
                        print(e)
                        time.sleep(1)
                    except KeyboardInterrupt as e:
                        print("Test Break")
                        self.clearSerThread()
                        break

    def ttsHubTest(self,apSerFp,cpSerFp):
        typeList = ['chinese','english','number','mixed','mixed_with_number']
        self.resFile = os.path.join(self.resultFolder, "result_tts.txt")
        saveFile(self.resFile, "\n", "a+")
        saveFile(self.resFile, "InfoType,txt,initTime,costTime,speedTime\n", "a+")
        end = False
        
        for size in ["40","120"]:
            tempTimes=0
            allInfo = txtInfo.get(size,{})
            for infoType in typeList:
                tempInfoList = allInfo.get(infoType,[])
                for tempInfo in tempInfoList:
                    if not tempInfo:
                        continue
                    try:
                        self.output.LOG_INFO(f"\t\t^^^^^^^^^^CURRENT TTS {infoType} {size}BYTE NO.{tempTimes} START^^^^^^^^^^")
                        # tempInfo = self.generator.generate_text(infoType, self.testByte)
                        ttsCmd = self.getTTSCmd(txt=tempInfo)
                        ttsRes = self.ttsApi(infoType,ttsCmd,tempInfo,apSerFp,cpSerFp)
                        if not ttsRes:
                            self.output.LOG_INFO(f"\n********** NO {self.runTimes} TTSTest Result Fail **********\n")
                        else:
                            self.output.LOG_INFO(f"\n********** NO {self.runTimes} TTSTest Result Pass **********\n")
                        self.runTimes+=1
                        time.sleep(1)
                        if not self.heartCheck(apSerFp):
                            self.output.LOG_ERROR(f"\n********** 串口通信中断，退出脚本 **********\n")
                            end =True
                            break
                        self.cmdShell(apSerFp, " ")
                        self.cmdShell(apSerFp, " ")
                        tempTimes+=1
                    except Exception as e:
                        traceback.print_exc()
                        print(e)
                        time.sleep(1)
                    except KeyboardInterrupt as e:
                        print("Test Break")
                        self.clearSerThread()
                        end =True
                        break

    def costTimeTest(self):
        if not self.initSerDevice():
            self.output.LOG_ERROR(f"退出当前测试")
            sys.exit()
        # 获取当前可用的串口句柄，可读取对应的串口数据、和配置文件中需要正则的内容
        cskSerFp = self.serFpPools.get("cskApLog", "")
        cskCpSerFp = self.serFpPools.get("cskCpLog", "")
        # 清除所有
        cskSerFp.cleanRegexResultBuff()
        cskCpSerFp.cleanRegexResultBuff()     
        self.transHubTest(cskSerFp,cskCpSerFp)
        self.ttsHubTest(cskSerFp,cskCpSerFp)  
        self.clearSerThread() 
    def apiPipeline(self):
        if not self.initSerDevice():
            self.output.LOG_ERROR(f"退出当前测试")
            sys.exit()
        # 获取当前可用的串口句柄，可读取对应的串口数据、和配置文件中需要正则的内容
        cskSerFp = self.serFpPools.get("cskApLog", "")
        cskCpSerFp = self.serFpPools.get("cskCpLog", "")
        # 清除所有
        cskSerFp.cleanRegexResultBuff()
        cskCpSerFp.cleanRegexResultBuff()
        # 清除单个
        
        cskSerFp.clearSingleRegex("hearCmdRes")
        self.transHubTest(cskSerFp,cskCpSerFp)
        self.ttsHubTest(cskSerFp,cskCpSerFp)
        self.clearSerThread()
        sys.exit()
        self.runTimes=0
        # 播报
        self.cmdShell(cskSerFp, self.ttsPlayStart)
        while True:
            try:
                infoType = random.choice(['chinese','english','number','mixed','mixed_with_number'])
                self.output.LOG_INFO(f"\t\t^^^^^^^^^^CURRENT TTS {infoType} {self.testByte}BYTE NO.{self.runTimes} START^^^^^^^^^^")
                tempInfo = self.generator.generate_text(infoType, self.testByte)
                ttsCmd = self.getTTSCmd(txt=tempInfo,vol=10)
                ttsRes = self.ttsApi(infoType,ttsCmd,tempInfo,cskSerFp,cskCpSerFp)
                if infoType == "chinese":
                    tempTRANSCmd = self.getTransCmd(language=1,txt=tempInfo)
                elif infoType == "english":
                    tempTRANSCmd = self.getTransCmd(language=2,txt=tempInfo)
                else:
                    tempTRANSCmd = self.getTransCmd(language=1,txt=tempInfo)
                transRes = self.transApi(infoType,tempTRANSCmd,tempInfo,cskSerFp,cskCpSerFp)
                if not self.heartCheck(cskSerFp):
                    self.output.LOG_ERROR(f"\n********** 串口通信中断，退出脚本 **********\n")
                    break
                time.sleep(1)
                if not self.checkSerAlive(cskSerFp, cskCpSerFp):
                    self.clearSerThread()
                    self.output.LOG_INFO("重新连接串口")
                    self.initSerDevice()
                    cskSerFp = self.serFpPools.get("cskApLog", "")
                    cskCpSerFp = self.serFpPools.get("cskCpLog", "")
            except Exception as e:
                traceback.print_exc()
                print(e)
                time.sleep(1)
                if not self.checkSerAlive(cskSerFp, cskCpSerFp):
                    self.clearSerThread()
                    self.output.LOG_INFO("重新连接串口")
                    self.initSerDevice()
                    cskSerFp = self.serFpPools.get("cskApLog", "")
                    cskCpSerFp = self.serFpPools.get("cskCpLog", "")
            except KeyboardInterrupt as e:
                print("Test Break")
                self.clearSerThread()
                break
            self.runTimes+=1
            if self.runTimes == self.testNum:
                break
        self.clearSerThread()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="获取外部参数库args")
    parser.add_argument('-f', "--file", type=str, default="scanInfo.json", help="测试配置文件路径")
    parser.add_argument('-t', "--testType", type=str, default=0, help="测试类型简介。")
    parser.add_argument('-n', "--testNum", type=int, default=20, help="测试类型简介。0:永不停止,1:指定次数")
    parser.add_argument('-b', "--testByte", type=int, default=120, help="测试文本大小,单位字节")
    parser.add_argument('-l', "--testLabel", type=str, default="trans_tts_allType_120byte_cost_v1.57", help="当前测试的标注，标记当前的测试内容")
    # parser.add_argument('-l', "--testLabel", type=str, default="temp_test", help="当前测试的标注，标记当前的测试内容")
    args = parser.parse_args()
    deviceInfo = args.file
    if os.path.isfile(deviceInfo):
        otaInfo = load_json(deviceInfo)
        otaRobot = apiTest(otaInfo, args)
        # otaRobot.apiPipeline()
        otaRobot.costTimeTest()
        
    else:
        print(f"请输入正确的测试配置文件,当前配置文件不存在{deviceInfo}")

