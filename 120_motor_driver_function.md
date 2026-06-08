# 第3回：DRV8835の復習とモーター制御の関数化

## 今日の目標

今回は、ライントレーサーの「走る部分」を作ります。

前回までに、RPR-220を使って白い床と黒いラインを見分ける準備をしました。今回はいったんセンサーから離れて、**Pico W からモータードライバ DRV8835 を使って左右のモーターを動かす**ことに集中します。

今日のゴールは、次のような命令で車体を動かせるようにすることです。

```python
forward()
reverse()
turn_left()
turn_right()
stop()
```

つまり、細かいピン操作を毎回書くのではなく、**動きに名前をつけて使えるようにする**ことが目標です。

---

## 今日の流れ（200分）

| 時間 | 内容 |
|---:|---|
| 0〜20分 | 前回までの確認、今日のゴール説明 |
| 20〜45分 | DRV8835と電源まわりの復習 |
| 45〜70分 | 配線図をノートに描く |
| 70〜100分 | 左右モーターを個別に回す |
| 100〜130分 | 前進・後退・停止を作る |
| 130〜165分 | 左旋回・右旋回を作る |
| 165〜190分 | 関数化する |
| 190〜200分 | チェック課題、片付け |

---

## 1. 今日使う部品

* Raspberry Pi Pico W
* DRV8835 モータードライバ
* タミヤ ツインモーターギアボックス
* 単3電池 4本
* 3.3V三端子レギュレータ NJM2396F33
* ジャンパ線
* すでに組み立てたシャーシ

---

## 2. モータードライバとは

Pico W のピンからは、モーターを直接回すだけの大きな電流を取り出せません。

そこで、Pico W は DRV8835 に対して、

* どちら向きに回すか
* 回すか止めるか

という命令だけを出します。

実際にモーターへ大きな電流を流す仕事は、**モータードライバ**が行います。

```text
Pico W  ── 命令 ──>  DRV8835  ── 電流 ──>  モーター
```

---

## 3. 電源の考え方

今回の回路には、大きく分けて2種類の電源があります。

| 電源 | 使う場所 | 注意 |
|---|---|---|
| 3.3V | Pico W、センサー、DRV8835の制御信号 | Picoのピンは3.3V |
| 電池電源 | モーターを回すための電源 | 大きな電流が流れる |

重要なのは、**GNDを共通にする**ことです。

```text
Pico W の GND
DRV8835 の GND
電池ボックスの - 側

これらをつなぐ
```

GNDが共通でないと、Pico W から出した命令を DRV8835 が正しく読めません。

> ⚠️ 注意  
> 単3電池4本は、新品だと6V程度になることがあります。Pico W に直接入れてはいけません。Pico W には授業で指定された3.3Vレギュレータを通した電源を使います。

---

## 4. DRV8835のモード

この授業では、DRV8835の **MODEピンをGNDにつなぐ**設定で使います。

このモードでは、各モーターに対して、次の2本の信号で制御します。

| 信号 | 役割 |
|---|---|
| PHASE | 回転方向を決める |
| ENABLE | 回す・止めるを決める |

今回はまだPWMによる速度調整はしません。ENABLE を 1 にすると回り、0 にすると止まる、という使い方をします。

---

## 5. この資料でのピン割り当て

授業で別のピンを指定された場合は、先生の指示を優先してください。

| 役割 | Pico W のピン | DRV8835側の例 |
|---|---:|---|
| 左モーター方向 | GP2 | AIN1 / APHASE |
| 左モーターON/OFF | GP3 | AIN2 / AENABLE |
| 右モーター方向 | GP4 | BIN1 / BPHASE |
| 右モーターON/OFF | GP5 | BIN2 / BENABLE |

RPR-220のセンサーでは GP26, GP27 を使う予定なので、モーター制御では GP26, GP27 は使いません。

---

## 6. まずは左モーターだけ回す

次のプログラムで、左モーターだけが回るか確認します。

```python
from machine import Pin
import time

# 左モーター用ピン
LEFT_PHASE = Pin(2, Pin.OUT)
LEFT_ENABLE = Pin(3, Pin.OUT)

# まずはこの向きを「前進」としてみる
LEFT_FORWARD = 0

# 左モーターを前進方向に回す
LEFT_PHASE.value(LEFT_FORWARD)
LEFT_ENABLE.value(1)
time.sleep(1)

# 停止
LEFT_ENABLE.value(0)
```

### 確認

* 左モーターは回りましたか。
* 1秒後に止まりましたか。
* 想定と逆向きに回った場合は、あとで `LEFT_FORWARD` の値を変更します。

---

## 7. 右モーターも回す

次に右モーターも確認します。

```python
from machine import Pin
import time

RIGHT_PHASE = Pin(4, Pin.OUT)
RIGHT_ENABLE = Pin(5, Pin.OUT)

RIGHT_FORWARD = 0

RIGHT_PHASE.value(RIGHT_FORWARD)
RIGHT_ENABLE.value(1)
time.sleep(1)

RIGHT_ENABLE.value(0)
```

### 確認

* 右モーターは回りましたか。
* 1秒後に止まりましたか。
* 左右のモーターで前進方向がそろっていますか。

---

## 8. 関数とは

同じような命令を何度も書くのは大変です。

そこで、よく使う処理に名前をつけておきます。

これを**関数**といいます。

たとえば、次のような細かい命令を、

```python
LEFT_PHASE.value(LEFT_FORWARD)
LEFT_ENABLE.value(1)
RIGHT_PHASE.value(RIGHT_FORWARD)
RIGHT_ENABLE.value(1)
```

次のように使えるようにします。

```python
forward()
```

このようにすると、プログラムが読みやすくなります。

---

## 9. 左右モーターを関数化する

次のプログラムを入力して、左右モーターを関数で動かせるようにします。

```python
from machine import Pin
import time

# ===== ピン設定 =====
LEFT_PHASE = Pin(2, Pin.OUT)
LEFT_ENABLE = Pin(3, Pin.OUT)
RIGHT_PHASE = Pin(4, Pin.OUT)
RIGHT_ENABLE = Pin(5, Pin.OUT)

# ===== 前進方向の設定 =====
# モーターが逆向きに回る場合は、0 と 1 を入れ替える
LEFT_FORWARD = 0
RIGHT_FORWARD = 0


def left_motor_forward():
    LEFT_PHASE.value(LEFT_FORWARD)
    LEFT_ENABLE.value(1)


def left_motor_reverse():
    LEFT_PHASE.value(1 - LEFT_FORWARD)
    LEFT_ENABLE.value(1)


def left_motor_stop():
    LEFT_ENABLE.value(0)


def right_motor_forward():
    RIGHT_PHASE.value(RIGHT_FORWARD)
    RIGHT_ENABLE.value(1)


def right_motor_reverse():
    RIGHT_PHASE.value(1 - RIGHT_FORWARD)
    RIGHT_ENABLE.value(1)


def right_motor_stop():
    RIGHT_ENABLE.value(0)


# ===== 車体全体の動き =====
def forward():
    left_motor_forward()
    right_motor_forward()


def reverse():
    left_motor_reverse()
    right_motor_reverse()


def stop():
    left_motor_stop()
    right_motor_stop()


def turn_left():
    left_motor_stop()
    right_motor_forward()


def turn_right():
    left_motor_forward()
    right_motor_stop()
```

---

## 10. 動作テスト

関数を作ったら、次のテストを行います。

```python
forward()
time.sleep(1)

stop()
time.sleep(0.5)

turn_left()
time.sleep(1)

stop()
time.sleep(0.5)

turn_right()
time.sleep(1)

stop()
time.sleep(0.5)

reverse()
time.sleep(1)

stop()
```

---

## 11. 今日のチェック課題

車体を次の順番で動かしなさい。

1. 1秒前進
2. 0.5秒停止
3. 1秒左旋回
4. 0.5秒停止
5. 1秒右旋回
6. 0.5秒停止
7. 1秒後退
8. 停止

ただし、必ず次の関数を使うこと。

```python
forward()
reverse()
turn_left()
turn_right()
stop()
```

---

## 12. うまく動かないときの確認

| 症状 | 確認すること |
|---|---|
| モーターがまったく回らない | 電池、GND共通、DRV8835の電源 |
| 片方だけ回らない | モーター線、GP番号、はんだ不良 |
| 前進のつもりが後退する | `LEFT_FORWARD` または `RIGHT_FORWARD` を変更 |
| Picoが再起動する | モーター電源とPico電源、GND、電池残量 |
| USBを抜くと動かない | 3.3VレギュレータからPicoへ給電できているか |

---

## 13. 今日のまとめ

今日学んだことは、次の3つです。

1. Pico Wだけではモーターを直接動かさず、DRV8835を使う。
2. Pico W、DRV8835、電池のGNDは共通にする。
3. 細かいピン操作は関数にまとめると、プログラムが読みやすくなる。

次回は、モーターの速さを変える **PWM制御** に進みます。
