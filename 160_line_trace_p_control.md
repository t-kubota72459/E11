# 第7回：P制御の入口 — ズレの大きさで曲がり方を変える

## 今日の目標

前回は、ON/OFF制御でライントレースを行いました。

ON/OFF制御では、

* 左が黒なら左へ曲がる
* 右が黒なら右へ曲がる
* どちらも白なら直進

というように、場合分けで動かしました。

今回は、もう少し工学らしい考え方に進みます。

今日のテーマは、

> どちらにズレているかだけでなく、どれくらいズレているかを使う

です。

これが **P制御** の入口です。

---

## 今日の流れ（200分）

| 時間 | 内容 |
|---:|---|
| 0〜20分 | 前回のON/OFF制御の問題点を共有 |
| 20〜40分 | P制御の考え方 |
| 40〜65分 | 左右センサー値の差 `error` を表示する |
| 65〜90分 | 手で車体を動かし、`error` の変化を見る |
| 90〜115分 | `correction = Kp * error` を理解する |
| 115〜150分 | P制御版ライントレースを実装する |
| 150〜180分 | `Kp` を変えて走りを比較する |
| 180〜200分 | ON/OFF制御との違いを記録する |

---

## 1. ON/OFF制御の弱点

ON/OFF制御は分かりやすいですが、次のような弱点があります。

* カクカク走りやすい。
* 直線でも左右にふらつきやすい。
* 速くするとラインから外れやすい。
* 少しズレた場合も、大きくズレた場合も、同じ曲がり方をしてしまう。

そこで今回は、センサーの値をそのまま使います。

---

## 2. ズレを数値で表す

左右のセンサー値を読みます。

```python
left_val = left_sensor.read_u16()
right_val = right_sensor.read_u16()
```

今回の回路では、黒いラインを見たときに値が大きくなる想定です。

そこで、次のようにします。

```python
error = left_val - right_val
```

`error` は「ズレ」を表す数値です。

| 状態 | left_val | right_val | error |
|---|---:|---:|---:|
| ほぼ中央 | 20000 | 21000 | -1000 |
| 左センサーが黒 | 50000 | 18000 | 32000 |
| 右センサーが黒 | 18000 | 50000 | -32000 |

`error` が正なら、ラインは左側にあります。

`error` が負なら、ラインは右側にあります。

---

## 3. P制御の考え方

P制御では、ズレが大きいほど強く修正します。

```text
修正量 = Kp × ズレ
```

プログラムでは次のように書きます。

```python
correction = Kp * error
```

ここで `Kp` は、曲がり方の強さを決める値です。

| Kp | 走り方 |
|---:|---|
| 小さい | あまり曲がらない |
| ちょうどよい | なめらかに追従しやすい |
| 大きすぎる | 左右にブルブル振れやすい |

---

## 4. まずは error を表示する

最初に、車体を走らせずに `error` を表示します。

```python
from machine import ADC, Pin
import time

left_sensor = ADC(Pin(26))
right_sensor = ADC(Pin(27))

while True:
    left_val = left_sensor.read_u16()
    right_val = right_sensor.read_u16()
    error = left_val - right_val

    print("L:", left_val, "R:", right_val, "error:", error)
    time.sleep_ms(100)
```

車体を手で動かして、次を確認します。

* 左センサーが黒ラインに乗ると `error` はどうなるか。
* 右センサーが黒ラインに乗ると `error` はどうなるか。
* ラインが中央付近のとき `error` は0に近いか。

---

## 5. P制御版ライントレース

次のプログラムを `main.py` として使います。

```python
from machine import ADC, Pin
import time
import motor

left_sensor = ADC(Pin(26))
right_sensor = ADC(Pin(27))

BASE_SPEED = 28000
Kp = 0.4


def limit(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value


while True:
    left_val = left_sensor.read_u16()
    right_val = right_sensor.read_u16()

    # 左右センサー値の差をズレとして使う
    error = left_val - right_val

    # ズレに比例して修正量を決める
    correction = int(Kp * error)

    # errorが正なら左に寄っているので、左モーターを遅く、右モーターを速くする
    left_speed = BASE_SPEED - correction
    right_speed = BASE_SPEED + correction

    # PWMの範囲に収める
    left_speed = limit(left_speed, 0, 65535)
    right_speed = limit(right_speed, 0, 65535)

    motor.drive(left_speed, right_speed)

    time.sleep_ms(10)
```

---

## 6. Kpを変えてみる

次のように、`Kp` を変えて走り方を比べます。

| Kp | 走り方のメモ |
|---:|---|
| 0.1 | |
| 0.2 | |
| 0.4 | |
| 0.6 | |
| 0.8 | |

`Kp` を大きくしすぎると、左右に揺れやすくなります。

`Kp` が小さすぎると、カーブで曲がりきれないことがあります。

---

## 7. BASE_SPEEDも関係する

P制御では、`Kp` だけでなく `BASE_SPEED` も重要です。

| BASE_SPEED | 起こりやすいこと |
|---:|---|
| 小さい | 安定しやすいが遅い |
| 中くらい | 調整しやすい |
| 大きい | 速いがラインアウトしやすい |

速く走らせるほど、修正も素早く行う必要があります。

---

## 8. ON/OFF制御とP制御の比較

次の表を記録します。

| 比較項目 | ON/OFF制御 | P制御 |
|---|---|---|
| 直線のふらつき | | |
| カーブの曲がりやすさ | | |
| 速度を上げたとき | | |
| 調整のしやすさ | | |

---

## 9. 今日のチェック課題

次の2つを行います。

1. `error` の値を表示し、左右どちらにズレているか説明できる。
2. P制御版のプログラムで、短いコースを走行できる。

余裕がある人は、ON/OFF制御とP制御の両方で走らせ、違いを記録します。

---

## 10. 今日のまとめ

今日学んだことは、次の3つです。

1. 左右センサー値の差を使うと、ラインからのズレを数値で表せる。
2. P制御では、ズレが大きいほど強く曲げる。
3. `Kp` は、曲がり方の強さを決める調整値である。

今日扱ったのは、PID制御のうちの **P制御** だけです。

PID制御には、PのほかにIとDもありますが、今回はまずPだけでライントレーサーを調整します。
