from machine import I2C, Pin
import time

TEMP_ADDR = 0x48			# 温度センサーのアドレス
OLED_ADDR = 0x3c			# ディスプレイのアドレス

# i2c 使うよ宣言
i2c = I2C(0,  scl=Pin(5),  sda=Pin(4))

#------------------------------------------------------------
# 温度取得関数
#------------------------------------------------------------
def get_temp():
    """
    get_temp()
    温度センサー ADT7410 から温度を 13 ビットモードで取得する
    4094 を超えたときは氷点下を意味しており、補正している。
    1bit あたり 0.0625 ℃ を表す。
    """
    # 温度を読み取る
    # 値は 2byte で帰ってくる
    d = i2c.readfrom_mem(0x48, 0x00, 2)
    
    # 2byte を結合する
    value = (d[0] << 8) | d[1]
    
    # 13bit モードのとき、下3bit は不要なので右シフトで削除
    value = value >> 3
    
    # ＋/ーを修正する
    # もし 4096 以上なら、それは氷点下を意味している
    if  value >= 4096:
        value = value - 8192
    return value * 0.0625

def oled_cmd(cmd):
    """
    関数 oled_cmd
    LED ディスプレイにいろいろな命令を送る
    """
    # b"\x00" は「これからコマンド(命令)を送るよ」という合図
    # 命令はマニュアルにある
    i2c.writeto(OLED_ADDR, b"\x00" + bytes([cmd]))
    time.sleep_ms(2)

def oled_data(char):
    """
    関数 oled_data
    LED ディスプレイに文字を書き込む
    b"\x40" が左上（位置）を意味していて、文字を表示すると自動的に右にズレていく
    """
    # b"\x40" は「これから文字データを送るよ」という合図
    i2c.writeto(OLED_ADDR, b"\x40" + char.encode())
    time.sleep_ms(2)

def move_cursor(line):
    if line == 1:
        i2c.writeto(OLED_ADDR,  b"\x00\x02")    
    elif line == 2:
        i2c.writeto(OLED_ADDR,  b"\x00\xa0")
    else:	
        pass	# なにもしない
    time.sleep_ms(2)

# 0x01: Clear Display
# 0x02: カーソルを左上に
# 0x0f: 表示 ON
# 0x01: Clear Display
# OLED 初期化
for c in [0x01, 0x02, 0x0f, 0x01]:
     oled_cmd(c)

# --- メッセージ表示 ---
msg = "Hello Pico 2!"

move_cursor(2)
for char in msg:
     oled_data(char)

while True:
    # 一行目に移動
    move_cursor(1)
    # オ
    i2c.writeto(OLED_ADDR, b"\x40\xb5")
    time.sleep_ms(2)
    # ン
    i2c.writeto(OLED_ADDR, b"\x40\xdd")
    time.sleep_ms(2)
    # ト
    i2c.writeto(OLED_ADDR, b"\x40\xc4")
    time.sleep_ms(2)
    # 濁点゛
    i2c.writeto(OLED_ADDR, b"\x40\xde")
    time.sleep_ms(2)
    msg = f":{get_temp():.2f} C"
    for char in msg:
         oled_data(char)
    time.sleep(1)
