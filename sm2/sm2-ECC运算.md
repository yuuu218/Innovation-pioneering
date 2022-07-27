impl sm2 with RFC6979

——使用RFC6979实现SM2算法

椭圆曲线密码类（实现一般的ECC运算）

class ECC:

def \__init__(self, p, a, b, n, G, h=None):

self.p = p

self.a = a

self.b = b

self.n = n

self.G = G

if h:

self.h = h

self.O = (-1, -1) \# 定义仿射坐标下无穷远点（零点）

\# 预先计算Jacobian坐标两点相加时用到的常数

self._2 = get_inverse(2, p)

self.a_3 = (a + 3) % p

\# 椭圆曲线上两点相加（仿射坐标）

\# SM2第1部分 3.2.3.1

\# 仅提供一个参数时为相同坐标点相加

def add(self, P1, P2=None):

x1, y1 = P1

if P2 is None or P1 == P2: \# 相同坐标点相加

\# 处理无穷远点

if P1 == self.O:

return self.O

\# 计算斜率k（k已不具备明确的几何意义）

k = (3 \* x1 \* x1 + self.a) \* get_inverse(2 \* y1, self.p) % self.p

\# 计算目标点坐标

x3 = (k \* k - x1 - x1) % self.p

y3 = (k \* (x1 - x3) - y1) % self.p

else:

x2, y2 = P2

\# 处理无穷远点

if P1 == self.O:

return P2

if P2 == self.O:

return P1

if x1 == x2:

return self.O

\# 计算斜率k

k = (y2 - y1) \* get_inverse(x2 - x1, self.p) % self.p

\# 计算目标点坐标

x3 = (k \* k - x1 - x2) % self.p

y3 = (k \* (x1 - x3) - y1) % self.p

return x3, y3

\# 椭圆曲线上的点乘运算（仿射坐标）

def multiply(self, k, P):

\# 判断常数k的合理性

assert type(k) is int and k \>= 0, 'factor value error'

\# 处理无穷远点

if k == 0 or P == self.O:

return self.O

if k == 1:

return P

elif k == 2:

return self.add(P)

elif k == 3:

return self.add(P, self.add(P))

elif k & 1 == 0: \# k/2 \* P + k/2 \* P

return self.add(self.multiply(k \>\> 1, P))

elif k & 1 == 1: \# P + k/2 \* P + k/2 \* P

return self.add(P, self.add(self.multiply(k \>\> 1, P)))

\# 输入P，返回-P

def minus(self, P):

Q = list(P)

Q[1] = -Q[1]

return tuple(Q)

\# Jacobian加重射影坐标下两点相加

\# SM2第1部分 A.1.2.3.2

\# 输入点包含两项时为仿射坐标，三项为Jacobian加重射影坐标，两点坐标系可不同

\# 两点相同时省略第二个参数

def Jacb_add(self, P1, P2=None):

if P2 is None or P1 == P2: \# 相同点相加

\# 处理无穷远点

if P1 == self.O:

return self.O

\# 根据参数包含的项数判断坐标系（是仿射坐标则转Jacobian坐标）

x1, y1, z1 = P1 if len(P1) == 3 else (\*P1, 1)

\# t1 = 3 \* x1\*\*2 + self.a \* pow(z1, 4, self.p)

\# t2 = 4 \* x1 \* y1\*\*2

\# t3 = 8 \* pow(y1, 4, self.p)

\# x3 = (t1\*\*2 - 2 \* t2) % self.p

\# y3 = (t1 \* (t2 - x3) - t3) % self.p

\# z3 = 2 \* y1 \* z1 % self.p

z3 = (y1 \* z1 \<\< 1) % self.p

if z3 == 0: \# 处理无穷远点

return self.O

T2 = y1 \* y1 % self.p

T4 = (T2 \<\< 3) % self.p

T5 = x1 \* T4 % self.p

T6 = z1 \* z1 % self.p

T1 = (x1 + T6) \* (x1 - T6) \* 3 % self.p

T1 = (T1 + self.a_3 \* T6 \* T6) % self.p

T3 = T1 \* T1 % self.p

T2 = T2 \* T4 % self.p

x3 = (T3 - T5) % self.p

T4 = T5 + (T5 + self.p \>\> 1) - T3 if T5 & 1 else T5 + (T5 \>\> 1) - T3

T1 = T1 \* T4 % self.p

y3 = (T1 - T2) % self.p

else: \# 不同点相加

\# 处理无穷远点

if P1 == self.O:

return P2

if P2 == self.O:

return P1

\# 根据参数包含的项数判断坐标系（是仿射坐标则转Jacobian坐标）

x1, y1, z1 = P1 if len(P1) == 3 else (\*P1, 1)

x2, y2, z2 = P2 if len(P2) == 3 else (\*P2, 1)

if z2 != 1 and z1 != 1:

z1_2 = z1 \* z1 % self.p

z2_2 = z2 \* z2 % self.p

t1 = x1 \* z2_2 % self.p

t2 = x2 \* z1_2 % self.p

t3 = t1 - t2

z3 = z1 \* z2 \* t3 % self.p

if z3 == 0: \# 处理无穷远点

return self.O

t4 = y1 \* z2 \* z2_2 % self.p

t5 = y2 \* z1 \* z1_2 % self.p

t6 = t4 - t5

t7 = t1 + t2

t8 = t4 + t5

t3_2 = t3 \* t3 % self.p

x3 = (t6 \* t6 - t7 \* t3_2) % self.p

t9 = (t7 \* t3_2 - (x3 \<\< 1)) % self.p

y3 = (t9 \* t6 - t8 \* t3 \* t3_2) \* self._2 % self.p

else: \# 可简化计算

if z1 == 1: \# 确保第二个点的z1=1

x1, y1, z1, x2, y2 = x2, y2, z2, x1, y1

T1 = z1 \* z1 % self.p

T2 = y2 \* z1 % self.p

T3 = x2 \* T1 % self.p

T1 = T1 \* T2 % self.p

T2 = T3 - x1

z3 = z1 \* T2 % self.p

if z3 == 0: \# 处理无穷远点

return self.O

T3 = T3 + x1

T1 = T1 - y1

T4 = T2 \* T2 % self.p

T5 = T1 \* T1 % self.p

T2 = T2 \* T4 % self.p

T3 = T3 \* T4 % self.p

T4 = x1 \* T4 % self.p

x3 = T5 - T3 % self.p

T2 = y1 \* T2 % self.p

T3 = T4 - x3

T1 = T1 \* T3 % self.p

y3 = T1 - T2 % self.p

\# T1 = z1 \* z1 % self.p

\# T3 = x2 \* T1 % self.p

\# T2 = T3 - x1

\# z3 = z1 \* T2 % self.p

\# if z3 == 0: \# 处理无穷远点

\# return self.O

\# T1 = (T1 \* y2 \* z1 - y1) % self.p

\# T4 = T2 \* T2 % self.p

\# x3 = T1 \* T1 - (T3 + x1) \* T4 % self.p

\# T1 = T1 \* (x1 \* T4 - x3) % self.p

\# y3 = T1 - y1 \* T2 \* T4 % self.p

return x3, y3, z3

\# Jacobian加重射影坐标下的点乘运算

\# SM2第1部分 A.3

\# 输入点包含两项时为仿射坐标，三项为Jacobian坐标

\# conv=True时结果转换为仿射坐标，否则不转换

\# algo表示选择的算法， r表示算法三（滑动窗法）的窗口值

def Jacb_multiply(self, k, P, conv=True, algo=2, r=5):

\# 处理无穷远点

if k == 0 or P == self.O:

return self.O

\# 仿射坐标转Jacobian坐标

\# if len(P) == 2:

\# P = (\*P, 1)

\# 算法一：二进制展开法

if algo == 1:

Q = P

for i in bin(k)[3:]:

Q = self.Jacb_add(Q)

if i == '1':

Q = self.Jacb_add(Q, P)

\# 算法二：加减法

elif algo == 2:

h = bin(3 \* k)[2:]

k = bin(k)[2:]

k = '0' \* (len(h) - len(k)) + k

Q = P

minusP = self.minus(P)

for i in range(1, len(h) - 1):

Q = self.Jacb_add(Q)

if h[i] == '1' and k[i] == '0':

Q = self.Jacb_add(Q, P)

elif h[i] == '0' and k[i] == '1':

Q = self.Jacb_add(Q, minusP)

\# 算法三：滑动窗法

\# 当k为255/256位时，通过test_r函数测试，r=5复杂度最低

elif algo == 3:

k = bin(k)[2:]

l = len(k)

if r \>= l: \# 如果窗口大于k的二进制位数，则本算法无意义

return self.Jacb_multiply(int(k, 2), P, conv, 2)

\# 保存P[j]值的字典

P\_ = {1: P, 2: self.Jacb_add(P)}

for i in range(1, 1 \<\< (r - 1)):

P_[(i \<\< 1) + 1] = self.Jacb_add(P_[(i \<\< 1) - 1], P_[2])

t = r

while k[t - 1] != '1':

t -= 1

hj = int(k[:t], 2)

Q = P_[hj]

j = t

while j \< l:

if k[j] == '0':

Q = self.Jacb_add(Q)

j += 1

else:

t = min(r, l - j)

while k[j + t - 1] != '1':

t -= 1

hj = int(k[j:j + t], 2)

Q = self.Jacb_add(self.Jacb_multiply(1 \<\< t, Q, False, 2), P_[hj])

j += t

return self.Jacb_to_affine(Q) if conv else Q

\# Jacobian加重射影坐标转仿射坐标

\# SM2第1部分 A.1.2.3.2

def Jacb_to_affine(self, P):

if len(P) == 2: \# 已经是仿射坐标

return P

x, y, z = P

\# 处理无穷远点

if z == 0:

return self.O

z\_ = get_inverse(z, self.p) \# z的乘法逆元

x2 = x \* z\_ \* z\_ % self.p

y2 = y \* z\_ \* z\_ \* z\_ % self.p

return x2, y2

\# 判断是否为无穷远点（零点）

def is_zero(self, P):

if len(P) == 2: \# 仿射坐标

return P == self.O

else: \# Jacobian加重射影坐标

return P[2] == 0

\# 判断是否为域Fp中的元素

\# 可输入多个元素，全符合才返回True

def on_Fp(self, \*x):

for i in x:

if 0 \<= i \< self.p:

pass

else:

return False

return True

\# 判断是否在椭圆曲线上

def on_curve(self, P):

if self.is_zero(P):

return False

if len(P) == 2: \# 仿射坐标

x, y = P

return y \* y % self.p == (x \* x \* x + self.a \* x + self.b) % self.p

else: \# Jacobian加重射影坐标

x, y, z = P

return y \* y % self.p == (x \* x \* x + self.a \* x \* pow(z, 4, self.p) + self.b \* pow(z, 6, self.p)) % self.p

\# 生成密钥对

\# 返回值：d为私钥，P为公钥

\# SM2第1部分 6.1

def gen_keypair(self):

d = random.randint(1, self.n - 2)

P = self.Jacb_multiply(d, self.G)

return d, P

\# 公钥验证

\# SM2第1部分 6.2.1

def pk_valid(self, P):

\# 判断点P的格式

if P and len(P) == 2 and type(P[0]) == type(P[1]) == int:

pass

else:

self.error = '格式有误' \# 记录错误信息

return False

\# a) 验证P不是无穷远点O

if self.is_zero(P):

self.error = '无穷远点'

return False

\# b) 验证公钥P的坐标xP和yP是域Fp中的元素

if not self.on_Fp(\*P):

self.error = '坐标值不是域Fp中的元素'

return False

\# c) 验证y\^2 = x\^3 + ax + b (mod p)

if not self.on_curve(P):

self.error = '不在椭圆曲线上'

return False

\# d) 验证[n]P = O

if not self.is_zero(self.Jacb_multiply(self.n, P, False)):

self.error = '[n]P不是无穷远点'

return False

return True

\# 确认目前已有公私钥对

def confirm_keypair(self):

if not hasattr(self, 'pk') or not self.pk_valid(self.pk) or self.pk != self.Jacb_multiply(self.sk, self.G):

\# 目前没有合格的公私钥对则生成

while True:

d, P = self.gen_keypair()

if self.pk_valid(P): \# 确保公钥通过验证

self.sk, self.pk = d, P

return目6 implement sm2 2P sign with real network communication

/\*门限密码算法通常用 (n， k）形式表示，n 表示参与者的个数， k 表示门限值（也被称为阈值），表示要完成秘密运算时最少需要的参与者个数。在攻击者能够攻破或完全控制的参与者个数少于 k 个的前提下，门限密码算法依然能够保持其安全性。  
  
 接下来介绍一下这种 SM2 门限密码方案的原理：它是一种（2，2）门限密码方案，即需要两个参与方，才能完成用到私钥的密码运算（如签名、解密）。\*/

\#include\<iostream\>

\#include"sm3.h"

\#include"SHA256.h"

using namespace std;

long n; int G[2],e,d1,d2,c1[2],klen,c2,c3;

long gcd(long a, long b)

{

while (a != b)

{

if (a \> b)

{

a = a - b;

}

else

{

b = b - a;

}

}

return a;

}

long ExGcd(long a, long b, long& x, long& y) {

if (!b)

{

x = 1;

y = 0;

return a;

}

long ans = ExGcd(b, a % b, x, y);

long temp = x;

x = y;

y = temp - a / b \* y;

return ans;

}

long getInverse(long a, long p)//a模n的乘法逆元

{

if (gcd(a, p) != 1)

return -1;

long x, y;

ExGcd(a, p, x, y);

return (x + p) % p;

}

/\*公钥及私钥份额生成算法：当需要生成 SM2 非对称密钥时，由两个参与方各自独立生成一个私钥份额（或称为私钥片段、私钥分量），双方通过交互通信、传输一些辅助计算数据，由其中一方合并辅助数据生成 SM2 公钥。只要这两个参与方不串通，就没有办法恢复出完整的 SM2 私钥。在攻击者至多只能攻破其中一个参与方的情况下，攻击者也没有办法恢复出完整的 SM2 私钥。\*/

struct USER1 {

int d1 = rand() % n;

int d1_1 = getInverse(d1, n);

int k1 = rand() % n;

};

struct USER2 {

int d2 = rand() % n;

int d2_1 = getInverse(d2, n);

int k2 = rand() % n;

int k3 = rand() % n;

int q2[2];

int x1, y1;

};

USER1 user1; USER2 user2;

/\*门限签名算法：当需要对消息进行 SM2 签名时，两个参与方分别使用各自持有的签名私钥片段，计算生成签名片段，然后双方交互传输签名片段等辅助计算数据，由其中一方对收到的数据进行合并计算，生成 SM2 签名。\*/

bool sign()

{

int p1[2];

p1[0] = user1.d1_1 \* G[0]; p1[1] = user1.d1_1 \* G[1];

int p[2];

p[0] = user2.d2_1 \* p1[0]-G[0]; p[1] = user2.d2_1 \* p1[1] - G[1];

int q1[2];

q1[0] = user1.k1 \* G[0]; q1[1] = user1.k1 \* G[1];

user2.q2[0] = user2.k2 \* G[0]; user2.q2[1] = user2.k2 \* G[1];

user2.x1 = user2.k3 \* q1[0] + user2.q2[0];

user2.y1 = user2.k3 \* q1[1] + user2.q2[1];

int r = (user2.x1 + e) % n;

int s2, s3;

if (r != 0)

{

s2 = d2 \* user2.k3 % n;

s3 = d2 \* (r + user2.k2) % n;

}

else

return false;

int s = ((d1 \* user1.k1) \* s2 + d1 \* s3 - r)%n;

if (s != 0 && s != (n - r))

{

cout \<\< "r=:" \<\< r \<\< " , s=:" \<\< s \<\< endl;

return true;

}

}
