from machine import I2C, Pin
import time

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

#------------------------------------------------------------ ここからが本処理
i2c = I2C(0,  scl=Pin(5),  sda=Pin(4))

# i2c スキャンで出席をとる
devices = i2c.scan()
for  i in devices:
    print(hex(i))

while True:
    print(get_temp())	# 温度取得
    time.sleep(1)		# 1 秒まつ
