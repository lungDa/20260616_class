import sys
import asyncio
import random
import discord
import os
from discord.ext import commands
from fastapi import FastAPI
import uvicorn

# ─── 1. 建立 FastAPI 網頁伺服器 ───
app = FastAPI()

@app.get("/")
async def home_get():
    return {"status": "🤖 誰是臥底機器人 24 暢通運作中！"}

@app.head("/")
async def home_head():
    return None

# ─── 2. Discord 機器人基本設定 ───
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

games = {}

# 多元題型詞庫（共 254 組）
# level 1 / level 2：平民同一個詞，臥底同一個詞
# level 3：平民同一個詞，兩個臥底各拿不同詞
WORD_BANK = [
    {"civilian": "珍珠奶茶", "undercover": "燕麥奶茶", "undercover_alt": "紅茶拿鐵"},
    {"civilian": "可樂", "undercover": "雪碧", "undercover_alt": "芬達"},
    {"civilian": "牛肉麵", "undercover": "陽春麵", "undercover_alt": "榨菜肉絲麵"},
    {"civilian": "雞排", "undercover": "鹽酥雞", "undercover_alt": "炸雞"},
    {"civilian": "滷肉飯", "undercover": "雞肉飯", "undercover_alt": "肉燥飯"},
    {"civilian": "鍋貼", "undercover": "水餃", "undercover_alt": "煎餃"},
    {"civilian": "壽司", "undercover": "手卷", "undercover_alt": "生魚片"},
    {"civilian": "拉麵", "undercover": "烏龍麵", "undercover_alt": "蕎麥麵"},
    {"civilian": "披薩", "undercover": "焗烤", "undercover_alt": "千層麵"},
    {"civilian": "火鍋", "undercover": "燒烤", "undercover_alt": "壽喜燒"},
    {"civilian": "蛋餅", "undercover": "蔥抓餅", "undercover_alt": "蘿蔔糕"},
    {"civilian": "豆漿", "undercover": "米漿", "undercover_alt": "杏仁茶"},
    {"civilian": "漢堡", "undercover": "三明治", "undercover_alt": "熱狗堡"},
    {"civilian": "薯條", "undercover": "洋蔥圈", "undercover_alt": "雞塊"},
    {"civilian": "炒飯", "undercover": "燴飯", "undercover_alt": "炒麵"},
    {"civilian": "關東煮", "undercover": "滷味", "undercover_alt": "鹽水雞"},
    {"civilian": "奶酪", "undercover": "布丁", "undercover_alt": "優格"},
    {"civilian": "冰淇淋", "undercover": "霜淇淋", "undercover_alt": "雪酪"},
    {"civilian": "紅茶", "undercover": "綠茶", "undercover_alt": "烏龍茶"},
    {"civilian": "咖啡", "undercover": "拿鐵", "undercover_alt": "美式咖啡"},
    {"civilian": "蛋糕", "undercover": "泡芙", "undercover_alt": "甜甜圈"},
    {"civilian": "巧克力", "undercover": "可可", "undercover_alt": "牛奶糖"},
    {"civilian": "水蜜桃", "undercover": "蘋果", "undercover_alt": "梨子"},
    {"civilian": "西瓜", "undercover": "哈密瓜", "undercover_alt": "香瓜"},
    {"civilian": "葡萄", "undercover": "藍莓", "undercover_alt": "櫻桃"},
    {"civilian": "鳳梨", "undercover": "芒果", "undercover_alt": "木瓜"},
    {"civilian": "香蕉", "undercover": "芭樂", "undercover_alt": "奇異果"},
    {"civilian": "草莓", "undercover": "覆盆莓", "undercover_alt": "蔓越莓"},
    {"civilian": "炸蝦", "undercover": "炸魚", "undercover_alt": "炸牡蠣"},
    {"civilian": "牛排", "undercover": "豬排", "undercover_alt": "羊排"},
    {"civilian": "雞腿便當", "undercover": "排骨便當", "undercover_alt": "控肉便當"},
    {"civilian": "茶葉蛋", "undercover": "滷蛋", "undercover_alt": "水煮蛋"},
    {"civilian": "麻辣鍋", "undercover": "酸菜白肉鍋", "undercover_alt": "石頭火鍋"},
    {"civilian": "奶茶", "undercover": "鮮奶茶", "undercover_alt": "奶綠"},
    {"civilian": "黑糖珍奶", "undercover": "波霸奶茶", "undercover_alt": "仙草奶凍"},
    {"civilian": "烤玉米", "undercover": "烤地瓜", "undercover_alt": "烤香腸"},
    {"civilian": "鹹酥雞", "undercover": "雞米花", "undercover_alt": "雞柳條"},
    {"civilian": "豆花", "undercover": "仙草", "undercover_alt": "愛玉"},
    {"civilian": "肉圓", "undercover": "碗粿", "undercover_alt": "米糕"},
    {"civilian": "蚵仔煎", "undercover": "蝦仁煎", "undercover_alt": "菜脯蛋"},
    {"civilian": "臭豆腐", "undercover": "炸豆腐", "undercover_alt": "豆干"},
    {"civilian": "小籠包", "undercover": "湯包", "undercover_alt": "肉包"},
    {"civilian": "牛排館", "undercover": "鐵板燒", "undercover_alt": "燒肉店"},
    {"civilian": "咖哩飯", "undercover": "丼飯", "undercover_alt": "燉飯"},
    {"civilian": "義大利麵", "undercover": "炒麵", "undercover_alt": "涼麵"},
    {"civilian": "鹽水雞", "undercover": "滷味", "undercover_alt": "雞胸肉"},
    {"civilian": "燒仙草", "undercover": "熱豆花", "undercover_alt": "紅豆湯"},
    {"civilian": "芋圓", "undercover": "粉圓", "undercover_alt": "地瓜圓"},
    {"civilian": "便當", "undercover": "自助餐", "undercover_alt": "合菜"},
    {"civilian": "炸醬麵", "undercover": "麻醬麵", "undercover_alt": "乾麵"},
    {"civilian": "英雄聯盟", "undercover": "DOTA2", "undercover_alt": "傳說對決"},
    {"civilian": "Minecraft", "undercover": "Terraria", "undercover_alt": "Roblox"},
    {"civilian": "原神", "undercover": "崩壞星穹鐵道", "undercover_alt": "鳴潮"},
    {"civilian": "FF14", "undercover": "魔獸世界", "undercover_alt": "黑色沙漠"},
    {"civilian": "寶可夢", "undercover": "數碼寶貝", "undercover_alt": "妖怪手錶"},
    {"civilian": "CS2", "undercover": "VALORANT", "undercover_alt": "Apex"},
    {"civilian": "艾爾登法環", "undercover": "黑暗靈魂", "undercover_alt": "血源詛咒"},
    {"civilian": "魔物獵人", "undercover": "討鬼傳", "undercover_alt": "Wild Hearts"},
    {"civilian": "航海王", "undercover": "火影忍者", "undercover_alt": "死神"},
    {"civilian": "鬼滅之刃", "undercover": "咒術迴戰", "undercover_alt": "進擊的巨人"},
    {"civilian": "柯南", "undercover": "金田一", "undercover_alt": "神探伽利略"},
    {"civilian": "七龍珠", "undercover": "幽遊白書", "undercover_alt": "獵人"},
    {"civilian": "鋼彈", "undercover": "EVA", "undercover_alt": "Code Geass"},
    {"civilian": "皮卡丘", "undercover": "伊布", "undercover_alt": "傑尼龜"},
    {"civilian": "魯夫", "undercover": "鳴人", "undercover_alt": "一護"},
    {"civilian": "瑪利歐", "undercover": "索尼克", "undercover_alt": "洛克人"},
    {"civilian": "薩爾達", "undercover": "魔物獵人", "undercover_alt": "艾爾登法環"},
    {"civilian": "隻狼", "undercover": "仁王", "undercover_alt": "黑神話悟空"},
    {"civilian": "星海爭霸", "undercover": "世紀帝國", "undercover_alt": "紅色警戒"},
    {"civilian": "天堂", "undercover": "RO仙境傳說", "undercover_alt": "楓之谷"},
    {"civilian": "Switch", "undercover": "PS5", "undercover_alt": "Xbox"},
    {"civilian": "動物森友會", "undercover": "星露谷物語", "undercover_alt": "牧場物語"},
    {"civilian": "GTA", "undercover": "看門狗", "undercover_alt": "黑道聖徒"},
    {"civilian": "刺客教條", "undercover": "古墓奇兵", "undercover_alt": "秘境探險"},
    {"civilian": "太鼓達人", "undercover": "節奏天國", "undercover_alt": "初音未來"},
    {"civilian": "跑跑卡丁車", "undercover": "瑪利歐賽車", "undercover_alt": "極速快感"},
    {"civilian": "糖豆人", "undercover": "Among Us", "undercover_alt": "鵝鴨殺"},
    {"civilian": "爐石戰記", "undercover": "遊戲王", "undercover_alt": "闇影詩章"},
    {"civilian": "暗黑破壞神", "undercover": "流亡黯道", "undercover_alt": "火炬之光"},
    {"civilian": "模擬市民", "undercover": "Cities Skylines", "undercover_alt": "動物園之星"},
    {"civilian": "勇者鬥惡龍", "undercover": "Final Fantasy", "undercover_alt": "女神異聞錄"},
    {"civilian": "瑪奇", "undercover": "洛奇英雄傳", "undercover_alt": "黑色沙漠"},
    {"civilian": "PUBG", "undercover": "Fortnite", "undercover_alt": "Apex"},
    {"civilian": "惡靈古堡", "undercover": "沉默之丘", "undercover_alt": "絕命異次元"},
    {"civilian": "集合啦動物森友會", "undercover": "牧場物語", "undercover_alt": "星露谷物語"},
    {"civilian": "快打旋風", "undercover": "鐵拳", "undercover_alt": "拳皇"},
    {"civilian": "任天堂明星大亂鬥", "undercover": "MultiVersus", "undercover_alt": "索尼克賽車"},
    {"civilian": "Splatoon", "undercover": "Overwatch", "undercover_alt": "Valorant"},
    {"civilian": "尼爾自動人形", "undercover": "異度神劍", "undercover_alt": "緋紅結繫"},
    {"civilian": "神奇寶貝紅版", "undercover": "寶可夢朱紫", "undercover_alt": "寶可夢劍盾"},
    {"civilian": "庫洛魔法使", "undercover": "美少女戰士", "undercover_alt": "小魔女DoReMi"},
    {"civilian": "灌籃高手", "undercover": "黑子的籃球", "undercover_alt": "排球少年"},
    {"civilian": "間諜家家酒", "undercover": "輝夜姬想讓人告白", "undercover_alt": "月刊少女野崎君"},
    {"civilian": "葬送的芙莉蓮", "undercover": "無職轉生", "undercover_alt": "哥布林殺手"},
    {"civilian": "鏈鋸人", "undercover": "咒術迴戰", "undercover_alt": "炎炎消防隊"},
    {"civilian": "Re:Zero", "undercover": "刀劍神域", "undercover_alt": "Overlord"},
    {"civilian": "JOJO", "undercover": "刃牙", "undercover_alt": "北斗神拳"},
    {"civilian": "哆啦A夢", "undercover": "蠟筆小新", "undercover_alt": "櫻桃小丸子"},
    {"civilian": "神隱少女", "undercover": "霍爾的移動城堡", "undercover_alt": "龍貓"},
    {"civilian": "你的名字", "undercover": "天氣之子", "undercover_alt": "鈴芽之旅"},
    {"civilian": "PLC", "undercover": "DCS", "undercover_alt": "PAC"},
    {"civilian": "GX Works3", "undercover": "Studio5000", "undercover_alt": "TIA Portal"},
    {"civilian": "三菱", "undercover": "AB", "undercover_alt": "西門子"},
    {"civilian": "變頻器", "undercover": "伺服驅動器", "undercover_alt": "軟啟動器"},
    {"civilian": "HMI", "undercover": "SCADA", "undercover_alt": "IPC"},
    {"civilian": "Modbus", "undercover": "Profinet", "undercover_alt": "EtherNet/IP"},
    {"civilian": "PT100", "undercover": "熱電偶", "undercover_alt": "NTC"},
    {"civilian": "接觸器", "undercover": "繼電器", "undercover_alt": "SSR"},
    {"civilian": "AutoCAD", "undercover": "EPLAN", "undercover_alt": "SolidWorks"},
    {"civilian": "Python", "undercover": "Java", "undercover_alt": "C#"},
    {"civilian": "FastAPI", "undercover": "Flask", "undercover_alt": "Django"},
    {"civilian": "GitHub", "undercover": "GitLab", "undercover_alt": "Bitbucket"},
    {"civilian": "RS485", "undercover": "RS232", "undercover_alt": "Ethernet"},
    {"civilian": "NPN", "undercover": "PNP", "undercover_alt": "Dry Contact"},
    {"civilian": "光電開關", "undercover": "近接開關", "undercover_alt": "限動開關"},
    {"civilian": "馬達", "undercover": "伺服馬達", "undercover_alt": "步進馬達"},
    {"civilian": "220V", "undercover": "380V", "undercover_alt": "480V"},
    {"civilian": "三相", "undercover": "單相", "undercover_alt": "直流"},
    {"civilian": "變壓器", "undercover": "整流器", "undercover_alt": "UPS"},
    {"civilian": "FX5U", "undercover": "Q系列", "undercover_alt": "R系列"},
    {"civilian": "DVP32ES3", "undercover": "FX5U", "undercover_alt": "S7-1200"},
    {"civilian": "DOP-112MX", "undercover": "GP-Pro EX", "undercover_alt": "Weintek HMI"},
    {"civilian": "DIADesigner", "undercover": "ISPSoft", "undercover_alt": "GX Works3"},
    {"civilian": "MS300", "undercover": "VFD-E", "undercover_alt": "FR-D700"},
    {"civilian": "IO模組", "undercover": "通訊模組", "undercover_alt": "類比模組"},
    {"civilian": "DI", "undercover": "DO", "undercover_alt": "AI"},
    {"civilian": "AO", "undercover": "AI", "undercover_alt": "DO"},
    {"civilian": "PID", "undercover": "ON/OFF控制", "undercover_alt": "斜坡控制"},
    {"civilian": "端子台", "undercover": "中繼端子", "undercover_alt": "保險絲座"},
    {"civilian": "線號", "undercover": "端子號", "undercover_alt": "設備位號"},
    {"civilian": "急停", "undercover": "安全門", "undercover_alt": "光柵"},
    {"civilian": "馬達保護開關", "undercover": "無熔絲開關", "undercover_alt": "漏電斷路器"},
    {"civilian": "電磁閥", "undercover": "氣缸", "undercover_alt": "調壓閥"},
    {"civilian": "流量計", "undercover": "壓力計", "undercover_alt": "液位計"},
    {"civilian": "溫度控制器", "undercover": "PLC溫控", "undercover_alt": "SSR控制"},
    {"civilian": "RJ45", "undercover": "M12接頭", "undercover_alt": "D-SUB"},
    {"civilian": "TCP/IP", "undercover": "UDP", "undercover_alt": "Serial"},
    {"civilian": "伺服定位", "undercover": "步進定位", "undercover_alt": "變頻調速"},
    {"civilian": "自保持", "undercover": "互鎖", "undercover_alt": "邊緣觸發"},
    {"civilian": "SFC", "undercover": "梯形圖", "undercover_alt": "ST語言"},
    {"civilian": "布林代數", "undercover": "真值表", "undercover_alt": "卡諾圖"},
    {"civilian": "繼電器盤", "undercover": "PLC盤", "undercover_alt": "MCC盤"},
    {"civilian": "控制電源", "undercover": "主電源", "undercover_alt": "儀表電源"},
    {"civilian": "AC480V", "undercover": "AC220V", "undercover_alt": "DC24V"},
    {"civilian": "FUSE", "undercover": "MCCB", "undercover_alt": "ELCB"},
    {"civilian": "接地", "undercover": "遮蔽", "undercover_alt": "隔離"},
    {"civilian": "扭力起子", "undercover": "剝線鉗", "undercover_alt": "壓接鉗"},
    {"civilian": "配線槽", "undercover": "DIN Rail", "undercover_alt": "端子排"},
    {"civilian": "盤內配線", "undercover": "現場拉線", "undercover_alt": "線槽配管"},
    {"civilian": "Recipe", "undercover": "Alarm", "undercover_alt": "Trend"},
    {"civilian": "資料庫", "undercover": "Google Sheet", "undercover_alt": "CSV"},
    {"civilian": "Streamlit", "undercover": "FastAPI", "undercover_alt": "Gradio"},
    {"civilian": "Discord Bot", "undercover": "Telegram Bot", "undercover_alt": "LINE Bot"},
    {"civilian": "Render", "undercover": "Railway", "undercover_alt": "Fly.io"},
    {"civilian": "requirements.txt", "undercover": "Dockerfile", "undercover_alt": "Procfile"},
    {"civilian": "環境變數", "undercover": "密碼檔", "undercover_alt": "Token"},
    {"civilian": "Git commit", "undercover": "Pull request", "undercover_alt": "Issue"},
    {"civilian": "除錯", "undercover": "測試", "undercover_alt": "部署"},
    {"civilian": "API", "undercover": "Webhook", "undercover_alt": "Socket"},
    {"civilian": "非同步", "undercover": "多執行緒", "undercover_alt": "多行程"},
    {"civilian": "JSON", "undercover": "YAML", "undercover_alt": "XML"},
    {"civilian": "Pandas", "undercover": "NumPy", "undercover_alt": "OpenPyXL"},
    {"civilian": "Uvicorn", "undercover": "Gunicorn", "undercover_alt": "Nginx"},
    {"civilian": "主管", "undercover": "老闆", "undercover_alt": "經理"},
    {"civilian": "加班", "undercover": "值班", "undercover_alt": "輪班"},
    {"civilian": "薪水", "undercover": "獎金", "undercover_alt": "津貼"},
    {"civilian": "工程師", "undercover": "技術員", "undercover_alt": "作業員"},
    {"civilian": "女朋友", "undercover": "老婆", "undercover_alt": "曖昧對象"},
    {"civilian": "ChatGPT", "undercover": "Gemini", "undercover_alt": "Claude"},
    {"civilian": "早餐", "undercover": "午餐", "undercover_alt": "晚餐"},
    {"civilian": "上班", "undercover": "加班", "undercover_alt": "開會"},
    {"civilian": "請假", "undercover": "曠職", "undercover_alt": "補休"},
    {"civilian": "手機", "undercover": "平板", "undercover_alt": "筆電"},
    {"civilian": "LINE", "undercover": "Discord", "undercover_alt": "Telegram"},
    {"civilian": "PS5", "undercover": "Xbox", "undercover_alt": "Switch"},
    {"civilian": "BMW", "undercover": "賓士", "undercover_alt": "Audi"},
    {"civilian": "iPhone", "undercover": "Samsung", "undercover_alt": "Google Pixel"},
    {"civilian": "老闆畫大餅", "undercover": "主管開會", "undercover_alt": "同事甩鍋"},
    {"civilian": "待辦事項", "undercover": "會議記錄", "undercover_alt": "工作日誌"},
    {"civilian": "週報", "undercover": "月報", "undercover_alt": "日報"},
    {"civilian": "下班", "undercover": "準時走", "undercover_alt": "偷跑"},
    {"civilian": "咖啡因", "undercover": "能量飲料", "undercover_alt": "提神飲料"},
    {"civilian": "報告", "undercover": "簡報", "undercover_alt": "企劃書"},
    {"civilian": "Bug", "undercover": "Feature", "undercover_alt": "Hotfix"},
    {"civilian": "已讀不回", "undercover": "秒回", "undercover_alt": "裝忙"},
    {"civilian": "拖延症", "undercover": "選擇困難", "undercover_alt": "懶癌"},
    {"civilian": "紅包", "undercover": "年終", "undercover_alt": "績效獎金"},
    {"civilian": "健身房", "undercover": "跑步機", "undercover_alt": "重訓區"},
    {"civilian": "外送", "undercover": "內用", "undercover_alt": "自取"},
    {"civilian": "社恐", "undercover": "邊緣人", "undercover_alt": "宅宅"},
    {"civilian": "冷氣", "undercover": "電風扇", "undercover_alt": "除濕機"},
    {"civilian": "鬧鐘", "undercover": "提醒", "undercover_alt": "行事曆"},
    {"civilian": "睡過頭", "undercover": "賴床", "undercover_alt": "補眠"},
    {"civilian": "存錢", "undercover": "投資", "undercover_alt": "記帳"},
    {"civilian": "股票", "undercover": "ETF", "undercover_alt": "基金"},
    {"civilian": "房租", "undercover": "水電費", "undercover_alt": "管理費"},
    {"civilian": "租屋", "undercover": "買房", "undercover_alt": "宿舍"},
    {"civilian": "車貸", "undercover": "信貸", "undercover_alt": "信用卡"},
    {"civilian": "洗衣機", "undercover": "烘衣機", "undercover_alt": "洗碗機"},
    {"civilian": "貓奴", "undercover": "狗奴", "undercover_alt": "鏟屎官"},
    {"civilian": "約會", "undercover": "聚餐", "undercover_alt": "唱歌"},
    {"civilian": "火鍋局", "undercover": "烤肉局", "undercover_alt": "喝酒局"},
    {"civilian": "手搖飲", "undercover": "便利商店", "undercover_alt": "咖啡店"},
    {"civilian": "颱風假", "undercover": "特休", "undercover_alt": "國定假日"},
    {"civilian": "週末", "undercover": "連假", "undercover_alt": "補班日"},
    {"civilian": "面試", "undercover": "履歷", "undercover_alt": "錄取通知"},
    {"civilian": "試用期", "undercover": "轉正", "undercover_alt": "離職"},
    {"civilian": "新人", "undercover": "老鳥", "undercover_alt": "主管"},
    {"civilian": "薪轉戶", "undercover": "信用卡", "undercover_alt": "金融卡"},
    {"civilian": "發票", "undercover": "收據", "undercover_alt": "報帳"},
    {"civilian": "公司電腦", "undercover": "私人筆電", "undercover_alt": "工業電腦"},
    {"civilian": "安全帽", "undercover": "反光背心", "undercover_alt": "工作鞋"},
    {"civilian": "工地", "undercover": "工廠", "undercover_alt": "辦公室"},
    {"civilian": "會議室", "undercover": "茶水間", "undercover_alt": "倉庫"},
    {"civilian": "高鐵", "undercover": "台鐵", "undercover_alt": "捷運"},
    {"civilian": "機車", "undercover": "腳踏車", "undercover_alt": "電動車"},
    {"civilian": "飛機", "undercover": "直升機", "undercover_alt": "熱氣球"},
    {"civilian": "遊艇", "undercover": "渡輪", "undercover_alt": "帆船"},
    {"civilian": "計程車", "undercover": "Uber", "undercover_alt": "公車"},
    {"civilian": "台北", "undercover": "新北", "undercover_alt": "桃園"},
    {"civilian": "台中", "undercover": "彰化", "undercover_alt": "南投"},
    {"civilian": "台南", "undercover": "高雄", "undercover_alt": "屏東"},
    {"civilian": "花蓮", "undercover": "台東", "undercover_alt": "宜蘭"},
    {"civilian": "日本", "undercover": "韓國", "undercover_alt": "泰國"},
    {"civilian": "東京", "undercover": "大阪", "undercover_alt": "京都"},
    {"civilian": "沖繩", "undercover": "北海道", "undercover_alt": "福岡"},
    {"civilian": "巴黎", "undercover": "倫敦", "undercover_alt": "羅馬"},
    {"civilian": "紐約", "undercover": "洛杉磯", "undercover_alt": "舊金山"},
    {"civilian": "海邊", "undercover": "山上", "undercover_alt": "湖邊"},
    {"civilian": "飯店", "undercover": "民宿", "undercover_alt": "青年旅館"},
    {"civilian": "行李箱", "undercover": "背包", "undercover_alt": "登機箱"},
    {"civilian": "護照", "undercover": "簽證", "undercover_alt": "身分證"},
    {"civilian": "機票", "undercover": "車票", "undercover_alt": "船票"},
    {"civilian": "導航", "undercover": "地圖", "undercover_alt": "指南針"},
    {"civilian": "籃球", "undercover": "排球", "undercover_alt": "足球"},
    {"civilian": "棒球", "undercover": "壘球", "undercover_alt": "板球"},
    {"civilian": "羽球", "undercover": "網球", "undercover_alt": "桌球"},
    {"civilian": "游泳", "undercover": "潛水", "undercover_alt": "衝浪"},
    {"civilian": "慢跑", "undercover": "健走", "undercover_alt": "登山"},
    {"civilian": "重訓", "undercover": "瑜伽", "undercover_alt": "皮拉提斯"},
    {"civilian": "拳擊", "undercover": "柔道", "undercover_alt": "跆拳道"},
    {"civilian": "自行車", "undercover": "飛輪", "undercover_alt": "滑板"},
    {"civilian": "露營", "undercover": "野餐", "undercover_alt": "烤肉"},
    {"civilian": "釣魚", "undercover": "賞鳥", "undercover_alt": "攝影"},
    {"civilian": "鋼琴", "undercover": "吉他", "undercover_alt": "小提琴"},
    {"civilian": "唱歌", "undercover": "跳舞", "undercover_alt": "饒舌"},
    {"civilian": "電影", "undercover": "影集", "undercover_alt": "綜藝"},
    {"civilian": "小說", "undercover": "漫畫", "undercover_alt": "雜誌"},
    {"civilian": "畫畫", "undercover": "攝影", "undercover_alt": "剪輯"},
    {"civilian": "料理", "undercover": "烘焙", "undercover_alt": "調酒"},
    {"civilian": "咖啡拉花", "undercover": "手沖咖啡", "undercover_alt": "義式咖啡"},
    {"civilian": "園藝", "undercover": "多肉植物", "undercover_alt": "盆栽"},
    {"civilian": "模型", "undercover": "公仔", "undercover_alt": "樂高"},
    {"civilian": "桌遊", "undercover": "撲克牌", "undercover_alt": "麻將"},
]

def get_game_state(guild_id):
    if guild_id not in games:
        games[guild_id] = {
            "is_active": False,
            "level": 1,
            "players": [],
            "words": {},
            "identities": {},
            "undercover_ids": [],
            "voted_users": {}
        }
    return games[guild_id]


def reset_all_game(guild_id):
    if guild_id in games:
        del games[guild_id]


def build_result_text(ctx, game):
    lines = []
    for player in game["players"]:
        identity = game["identities"].get(player.id, "未知")
        word = game["words"].get(player.id, "未知")
        lines.append(f"・{player.display_name}：{identity}｜{word}")

    # 有些玩家可能已被淘汰，但仍在 identities / words 中，補進結算
    alive_ids = {p.id for p in game["players"]}
    for player_id, identity in game["identities"].items():
        if player_id not in alive_ids:
            member = ctx.guild.get_member(player_id)
            name = member.display_name if member else str(player_id)
            word = game["words"].get(player_id, "未知")
            lines.append(f"・{name}：{identity}｜{word}")

    return "\n".join(lines)


@bot.event
async def on_ready():
    print(f"🤖 誰是臥底主機已連線：{bot.user.name}")


@bot.command(name="玩法")
async def show_rules(ctx):
    await ctx.send(
        "🎮 **誰是臥底玩法等級**\n"
        "`!開局 1`：1 個臥底，其他都是平民。\n"
        "`!開局 2`：2 個臥底，其他都是平民。\n"
        "`!開局 3`：2 個臥底，但兩個臥底拿到不同詞彙，其他都是平民。\n\n"
        "範例：`!開局 3`"
    )


@bot.command(name="報名")
async def sign_up(ctx):
    game = get_game_state(ctx.guild.id)

    if game["is_active"]:
        await ctx.send("⚠️ 遊戲正在進行，請稍候。")
        return

    if ctx.author in game["players"]:
        await ctx.send(f"❓ {ctx.author.mention} 你已經報名過囉！")
        return

    game["players"].append(ctx.author)
    await ctx.send(f"✅ {ctx.author.mention} 報名成功！目前人數：{len(game['players'])} 人")


@bot.command(name="取消報名")
async def cancel_sign_up(ctx):
    game = get_game_state(ctx.guild.id)

    if game["is_active"]:
        await ctx.send("⚠️ 遊戲正在進行，不能取消報名。")
        return

    if ctx.author not in game["players"]:
        await ctx.send(f"❓ {ctx.author.mention} 你目前沒有報名。")
        return

    game["players"].remove(ctx.author)
    await ctx.send(f"✅ {ctx.author.mention} 已取消報名。目前人數：{len(game['players'])} 人")


@bot.command(name="名單")
async def show_players(ctx):
    game = get_game_state(ctx.guild.id)

    if not game["players"]:
        await ctx.send("目前還沒有人報名。")
        return

    names = "、".join([p.display_name for p in game["players"]])
    await ctx.send(f"📋 **目前報名名單**：{names}")


@bot.command(name="開局")
async def start_game(ctx, level: int = 1):
    game = get_game_state(ctx.guild.id)

    if game["is_active"]:
        await ctx.send("⚠️ 遊戲已經開始，請先 `!重置` 再開新局。")
        return

    if level not in [1, 2, 3]:
        await ctx.send("❌ 等級只能輸入 `1`、`2`、`3`。例如：`!開局 2`")
        return

    player_count = len(game["players"])

    if level == 1 and player_count < 3:
        await ctx.send(f"❌ 1級玩法至少需要 3 人！目前：{player_count} 人")
        return

    if level in [2, 3] and player_count < 4:
        await ctx.send(f"❌ {level}級玩法至少需要 4 人！目前：{player_count} 人")
        return

    game["is_active"] = True
    game["level"] = level
    game["words"].clear()
    game["identities"].clear()
    game["undercover_ids"].clear()
    game["voted_users"].clear()

    await ctx.send(f"🎲 **{level}級玩法發牌中！請確認 Discord「私訊」。**")

    selected_pair = random.choice(WORD_BANK)

    undercover_count = 1 if level == 1 else 2
    undercover_players = random.sample(game["players"], undercover_count)
    game["undercover_ids"] = [p.id for p in undercover_players]

    for player in game["players"]:
        if player.id in game["undercover_ids"]:
            game["identities"][player.id] = "臥底"

            # 3級：兩個臥底詞彙不一樣
            if level == 3:
                first_undercover_id = game["undercover_ids"][0]
                if player.id == first_undercover_id:
                    game["words"][player.id] = selected_pair["undercover"]
                else:
                    game["words"][player.id] = selected_pair["undercover_alt"]
            else:
                game["words"][player.id] = selected_pair["undercover"]
        else:
            game["identities"][player.id] = "平民"
            game["words"][player.id] = selected_pair["civilian"]

        try:
            await player.send(
                f"🤫 【神祕詞彙】這一局你拿到的是：**【 {game['words'][player.id]} 】**"
            )
        except discord.Forbidden:
            await ctx.send(f"⚠️ 無法私訊給 {player.mention}，請他開啟伺服器成員私訊。")

    names = "、".join([p.display_name for p in game["players"]])
    await ctx.send(
        f"🏁 **遊戲開始！**\n"
        f"玩法等級：**{level}級**\n"
        f"參賽者：{names}\n"
        f"請輪流發言，投票請用：`!投 @玩家`"
    )


@bot.command(name="投")
async def vote_player(ctx, member: discord.Member = None):
    game = get_game_state(ctx.guild.id)

    if not game["is_active"]:
        await ctx.send("⚠️ 目前沒有正在進行的遊戲。")
        return

    if ctx.author not in game["players"]:
        await ctx.send("❌ 你不是本局存活玩家，不能投票。")
        return

    if not member or member not in game["players"]:
        await ctx.send("❌ 請標記在場存活玩家，例如：`!投 @玩家`")
        return

    game["voted_users"][ctx.author.id] = member.id
    await ctx.send(
        f"🗳️ {ctx.author.mention} 已投票！"
        f"（{len(game['voted_users'])}/{len(game['players'])}）"
    )

    if len(game["voted_users"]) >= len(game["players"]):
        await ctx.send("🔔 **投票結束！系統計票中...**")
        await asyncio.sleep(1.5)

        vote_counts = {}
        for target_id in game["voted_users"].values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        highest_vote = max(vote_counts.values())
        highest_voted_ids = [
            target_id for target_id, count in vote_counts.items()
            if count == highest_vote
        ]

        # 平票不淘汰，避免 max 隨機淘汰造成爭議
        if len(highest_voted_ids) > 1:
            tied_names = []
            for target_id in highest_voted_ids:
                member_obj = ctx.guild.get_member(target_id)
                tied_names.append(member_obj.display_name if member_obj else str(target_id))

            game["voted_users"].clear()
            await ctx.send(
                f"⚖️ **本輪平票，無人淘汰！**\n"
                f"平票玩家：{ '、'.join(tied_names) }\n"
                f"請重新討論後再投票。"
            )
            return

        eliminated_id = highest_voted_ids[0]
        eliminated = ctx.guild.get_member(eliminated_id)

        if eliminated is None:
            game["voted_users"].clear()
            await ctx.send("⚠️ 找不到被投票玩家資料，本輪投票作廢。")
            return

        await ctx.send(f"🪓 **{eliminated.display_name}** 獲得最高票，慘遭淘汰！")
        await check_win_condition(ctx, eliminated)


async def check_win_condition(ctx, eliminated):
    game = get_game_state(ctx.guild.id)

    if eliminated in game["players"]:
        game["players"].remove(eliminated)

    game["voted_users"].clear()

    alive_undercover_ids = [
        player.id for player in game["players"]
        if game["identities"].get(player.id) == "臥底"
    ]
    alive_civilian_ids = [
        player.id for player in game["players"]
        if game["identities"].get(player.id) == "平民"
    ]

    # 平民勝利：所有臥底都被淘汰
    if len(alive_undercover_ids) == 0:
        result_text = build_result_text(ctx, game)
        await ctx.send(
            "🎉 **【平民獲勝！】** 成功抓出所有臥底！\n\n"
            f"📌 **本局身分公開：**\n{result_text}"
        )
        reset_all_game(ctx.guild.id)
        return

    # 臥底勝利：臥底人數 >= 平民人數
    if len(alive_undercover_ids) >= len(alive_civilian_ids):
        undercover_mentions = []
        for player_id in alive_undercover_ids:
            member = ctx.guild.get_member(player_id)
            undercover_mentions.append(member.mention if member else str(player_id))

        result_text = build_result_text(ctx, game)
        await ctx.send(
            f"😈 **【臥底獲勝！】** 臥底人數已經大於或等於平民人數！\n"
            f"存活臥底：{'、'.join(undercover_mentions)}\n\n"
            f"📌 **本局身分公開：**\n{result_text}"
        )
        reset_all_game(ctx.guild.id)
        return

    alive_names = "、".join([p.display_name for p in game["players"]])
    await ctx.send(
        f"⏳ **遊戲繼續！**\n"
        f"剩餘存活者：**{alive_names}**\n"
        f"請開始下一輪討論與投票。"
    )


@bot.command(name="重置")
async def force_stop(ctx):
    reset_all_game(ctx.guild.id)
    await ctx.send("⏹️ 遊戲資料庫已清空重置。")


# ─── 3. 用同一個事件循環啟動 ───
async def main():
    TOKEN = os.getenv("DISCORD_TOKEN")

    if not TOKEN:
        print("❌ 錯誤：找不到環境變數 DISCORD_TOKEN")
        return

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=10000,
        log_level="info"
    )
    server = uvicorn.Server(config)

    await asyncio.gather(
        server.serve(),
        bot.start(TOKEN)
    )


if __name__ == "__main__":
    asyncio.run(main())
