# 第4回：PWMによる速度制御と motor.py へのモジュール化

## 今日の目標

前回は、次のような関数を作りました。

```python
forward()
reverse()
turn_left()
turn_right()
stop()
```

今回は、さらに一歩進めて、モーターの速さを変えられるようにします。

```python
forward(30000)
turn_left(25000)
stop()
```

また、モーター制御の関数を `motor.py` という別ファイルに分けます。

今後ライントレースのプログラムを書くときに、毎回モーター制御の長いコードを書かなくてよいようにするためです。

---

## 今日の流れ（200分）

| 時間 | 内容 |
|---:|---|
| 0〜20分 | 前回の関数の復習 |
| 20〜45分 | PWMの考え方 |
| 45〜75分 | 片側モーターで速度を変える |
| 75〜105分 | 左右モーターをPWM化する |
| 105〜135分 | `drive(left_speed, right_speed)` を作る |
| 135〜165分 | `motor.py` に分ける |
| 165〜190分 | `main.py` から `motor.py` を使う |
| 190〜200分 | チェック課題、片付け |

---

## 1. PWMとは

PWMは、出力を高速にON/OFFすることで、モーターに伝わる力を調整する方法です。

ずっとONなら強く回ります。

```text
ON ON ON ON ON ON ON ON
```

ONの時間が少なければ、弱く回ります。

```text
ON OFF OFF ON OFF OFF ON OFF
```

Pico W の MicroPython では、PWMの強さを `0〜65535` の数値で指定します。

| 値 | 意味 |
|---:|---|
| 0 | 停止 |
| 20000 | 弱め |
| 40000 | 中くらい |
| 65535 | 最大 |

---

## 2. 片側モーターでPWMを試す

まずは左モーターだけで速度を変えてみます。

```python
from machine import Pin, PWM
import time

LEFT_PHASE = Pin(2, Pin.OUT)
LEFT_ENABLE = PWM(Pin(3))
LEFT_ENABLE.freq(1000)

LEFT_FORWARD = 0

LEFT_PHASE.value(LEFT_FORWARD)

LEFT_ENABLE.duty_u16(20000)
time.sleep(1)

LEFT_ENABLE.duty_u16(40000)
time.sleep(1)

LEFT_ENABLE.duty_u16(60000)
time.sleep(1)

LEFT_ENABLE.duty_u16(0)
```

### 確認

* PWM値を大きくすると、モーターの回転は速くなりましたか。
* 小さすぎる値では、モーターが回らないことがありましたか。

---

## 3. モーターには個体差がある

左右のモーターに同じPWM値を与えても、完全に同じ速さで回るとは限りません。

次の表を記録しましょう。

| 項目 | 左モーター | 右モーター |
|---|---:|---:|
| 回り始めたPWM値 | | |
| 安定して回るPWM値 | | |
| 速すぎると感じたPWM値 | | |

ライントレーサーでは、このような「実物のズレ」を調整していくことが大切です。

---

## 4. 左右の速度を指定できる関数

次の関数を作ります。

```python
drive(left_speed, right_speed)
```

この関数では、

* `left_speed` が正の値なら左モーター前進
* `left_speed` が負の値なら左モーター後退
* `left_speed` が 0 なら左モーター停止

とします。

右モーターも同じです。

---

## 5. motor.py を作る

Thonnyで新しいファイルを作り、名前を `motor.py` としてPicoに保存します。

```python
from machine import Pin, PWM

# ===== ピン設定 =====
LEFT_PHASE = Pin(2, Pin.OUT)
LEFT_ENABLE = PWM(Pin(3))
RIGHT_PHASE = Pin(4, Pin.OUT)
RIGHT_ENABLE = PWM(Pin(5))

LEFT_ENABLE.freq(1000)
RIGHT_ENABLE.freq(1000)

# ===== 前進方向の設定 =====
# 逆向きに回る場合は 0 と 1 を入れ替える
LEFT_FORWARD = 0
RIGHT_FORWARD = 0


def limit(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value


def left_motor(speed):
    speed = int(speed)
    speed = limit(speed, -65535, 65535)

    if speed > 0:
        LEFT_PHASE.value(LEFT_FORWARD)
        LEFT_ENABLE.duty_u16(speed)
    elif speed < 0:
        LEFT_PHASE.value(1 - LEFT_FORWARD)
        LEFT_ENABLE.duty_u16(-speed)
    else:
        LEFT_ENABLE.duty_u16(0)


def right_motor(speed):
    speed = int(speed)
    speed = limit(speed, -65535, 65535)

    if speed > 0:
        RIGHT_PHASE.value(RIGHT_FORWARD)
        RIGHT_ENABLE.duty_u16(speed)
    elif speed < 0:
        RIGHT_PHASE.value(1 - RIGHT_FORWARD)
        RIGHT_ENABLE.duty_u16(-speed)
    else:
        RIGHT_ENABLE.duty_u16(0)


def drive(left_speed, right_speed):
    left_motor(left_speed)
    right_motor(right_speed)


def forward(speed):
    drive(speed, speed)


def reverse(speed):
    drive(-speed, -speed)


def stop():
    drive(0, 0)


def turn_left(speed):
    drive(0, speed)


def turn_right(speed):
    drive(speed, 0)


def spin_left(speed):
    drive(-speed, speed)


def spin_right(speed):
    drive(speed, -speed)
```

---

## 6. main.py から motor.py を使う

次に、別のファイル `main.py` を作ります。

```python
import time
import motor

motor.forward(30000)
time.sleep(1)

motor.stop()
time.sleep(0.5)

motor.turn_left(30000)
time.sleep(1)

motor.stop()
time.sleep(0.5)

motor.turn_right(30000)
time.sleep(1)

motor.stop()
```

`motor.py` の中にある関数を使うときは、

```python
motor.forward(30000)
```

のように、前に `motor.` をつけます。

---

## 7. なぜファイルを分けるのか

今後、ライントレースのプログラムでは、センサーを読む処理や白黒判定の処理が増えていきます。

もしモーター制御の長いコードを毎回書くと、プログラムが読みにくくなります。

そこで、モーター制御は `motor.py` にまとめます。

```text
main.py   ：ライントレースの考え方を書く
motor.py  ：モーターを動かす細かい処理を書く
```

このように役割を分けることを、ここでは**モジュール化**と呼びます。

---

## 8. チェック課題

`main.py` を使って、車体を次のように動かしなさい。

1. ゆっくり前進
2. 停止
3. 少し速く前進
4. 停止
5. 左旋回
6. 右旋回
7. 停止

ただし、モーター制御の関数はすべて `motor.py` に書き、`main.py` から呼び出すこと。

---

## 9. 記録すること

| 項目 | 値 |
|---|---:|
| 左モーターが回り始めるPWM値 | |
| 右モーターが回り始めるPWM値 | |
| 直進しやすいPWM値 | |
| 旋回しやすいPWM値 | |

---

## 10. 今日のまとめ

今日学んだことは、次の3つです。

1. PWMを使うと、モーターの速さを変えられる。
2. 左右のモーターは、同じ命令でも完全に同じ動きにはならない。
3. モーター制御を `motor.py` にまとめると、今後のプログラムが書きやすくなる。

次回は、左右2個のRPR-220をPico Wにつないで、白黒の数値を測定します。
