from machine import I2C, Pin
import time

def oled_cmd(cmd):
    """
    関数 oled_cmd
    LED ディスプレイにいろいろな命令を送る
    """
    # b"\x00" は「これからコマンド(命令)を送るよ」という合図
    # 命令はマニュアルにある
    i2c.writeto(OLED_ADDR,  b"\x00" + bytes([cmd]))
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

# ------------------------------------------------------------
# ここから本処理
# ------------------------------------------------------------
i2c = I2C(0,  scl=Pin(5),  sda=Pin(4))
OLED_ADDR = 0x3c
   
# 0x01: Clear Display
# 0x02: カーソルを左上に
# 0x0f: 表示 ON
# 0x01: Clear Display
for c in [0x01, 0x02, 0x0f, 0x01]:
     oled_cmd(c)

# --- メッセージ表示 ---
msg = "Hello Pico 2!"
for c in msg:
    oled_data(c)