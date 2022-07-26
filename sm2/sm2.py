import random
import time
import math
import numpy as np
import rsa
import base64
import bitcoin
from pysmx.SM3 import digest as sm3

# 小素数列表，加快判断素数速度
small_primes = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
                         43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109,
                         113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191,
                         193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269,
                         271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353,
                         359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
                         443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523,
                         541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617,
                         619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709,
                         719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
                         821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
                         911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997])


def is_prime(num):
    # 排除0,1和负数
    if num < 2:
        return False
    # 排除小素数的倍数
    for prime in small_primes:
        if num % prime == 0:
            return False
    # 未分辨出来的大整数用rabin算法判断
    return rabin_miller(num)


def rabin_miller(num):
    s = num - 1
    t = 0
    while s & 1 == 0:
        s >>= 1
        t += 1
    for trials in range(5):
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = v * v % num
    return True


# 将字节转换为int
def to_int(byte):
    return int.from_bytes(byte, byteorder='big')


# 转换为bytes，第二参数为字节数（可不填）
def to_byte(x, size=None):
    if isinstance(x, int):
        if size is None:  # 计算合适的字节数
            size = 0
            tmp = x >> 64
            while tmp:
                size += 8
                tmp >>= 64
            tmp = x >> (size << 3)
            while tmp:
                size += 1
                tmp >>= 8
        elif x >> (size << 3):  # 指定的字节数不够则截取低位
            x &= (1 << (size << 3)) - 1
        return x.to_bytes(size, byteorder='big')
    elif isinstance(x, str):
        x = x.encode()
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字符
        return x
    elif isinstance(x, bytes):
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字节
        return x
    elif isinstance(x, tuple) and len(x) == 2 and type(x[0]) == type(x[1]) == int:
        # 针对坐标形式(x, y)
        return to_byte(x[0], size) + to_byte(x[1], size)
    return bytes(x)


# 将列表元素转换为bytes并连接
def join_bytes(data_list):
    return b''.join([to_byte(i) for i in data_list])


# 求最大公约数
def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)


# 求乘法逆元过程中的辅助递归函数
def get_(a, b):
    if b == 0:
        return 1, 0
    x1, y1 = get_(b, a % b)
    x, y = y1, x1 - a // b * y1
    return x, y


# 求乘法逆元
def get_inverse(a, p):
    # return pow(a, p-2, p) # 效率较低、n倍点的时候两种计算方法结果会有不同
    if gcd(a, p) == 1:
        x, y = get_(a, p)
        return x % p
    return 1


def get_cpu_time():
    return time.perf_counter()


# 密钥派生函数（从一个共享的秘密比特串中派生出密钥数据）
# SM2第3部分 5.4.3
# Z为bytes类型
# klen表示要获得的密钥数据的比特长度（8的倍数），int类型
# 输出为bytes类型
def KDF(Z, klen):
    ksize = klen >> 3
    K = bytearray()
    for ct in range(1, math.ceil(ksize / HASH_SIZE) + 1):
        K.extend(sm3(Z + to_byte(ct, 4)))
    return K[:ksize]

# 计算比特位数
def get_bit_num(x):
    if isinstance(x, int):
        num = 0
        tmp = x >> 64
        while tmp:
            num += 64
            tmp >>= 64
        tmp = x >> num >> 8
        while tmp:
            num += 8
            tmp >>= 8
        x >>= num
        while x:
            num += 1
            x >>= 1
        return num
    elif isinstance(x, str):
        return len(x.encode()) << 3
    elif isinstance(x, bytes):
        return len(x) << 3
    return 0


# 椭圆曲线密码类（实现一般的EC运算，不局限于SM2）
class ECC:
    def __init__(self, p, a, b, n, G, h=None):
        self.p = p
        self.a = a
        self.b = b
        self.n = n
        self.G = G
        if h:
            self.h = h
        self.O = (-1, -1)  # 定义仿射坐标下无穷远点（零点）

        # 预先计算Jacobian坐标两点相加时用到的常数
        self._2 = get_inverse(2, p)
        self.a_3 = (a + 3) % p

    # 椭圆曲线上两点相加（仿射坐标）
    # SM2第1部分 3.2.3.1
    # 仅提供一个参数时为相同坐标点相加
    def add(self, P1, P2=None):
        x1, y1 = P1
        if P2 is None or P1 == P2:  # 相同坐标点相加
            # 处理无穷远点
            if P1 == self.O:
                return self.O
            # 计算斜率k（k已不具备明确的几何意义）
            k = (3 * x1 * x1 + self.a) * get_inverse(2 * y1, self.p) % self.p
            # 计算目标点坐标
            x3 = (k * k - x1 - x1) % self.p
            y3 = (k * (x1 - x3) - y1) % self.p
        else:
            x2, y2 = P2
            # 处理无穷远点
            if P1 == self.O:
                return P2
            if P2 == self.O:
                return P1
            if x1 == x2:
                return self.O
            # 计算斜率k
            k = (y2 - y1) * get_inverse(x2 - x1, self.p) % self.p
            # 计算目标点坐标
            x3 = (k * k - x1 - x2) % self.p
            y3 = (k * (x1 - x3) - y1) % self.p
        return x3, y3

    # 椭圆曲线上的点乘运算（仿射坐标）
    def multiply(self, k, P):
        # 判断常数k的合理性
        assert type(k) is int and k >= 0, 'factor value error'
        # 处理无穷远点
        if k == 0 or P == self.O:
            return self.O
        if k == 1:
            return P
        elif k == 2:
            return self.add(P)
        elif k == 3:
            return self.add(P, self.add(P))
        elif k & 1 == 0:  # k/2 * P + k/2 * P
            return self.add(self.multiply(k >> 1, P))
        elif k & 1 == 1:  # P + k/2 * P + k/2 * P
            return self.add(P, self.add(self.multiply(k >> 1, P)))

    # 输入P，返回-P
    def minus(self, P):
        Q = list(P)
        Q[1] = -Q[1]
        return tuple(Q)

    # Jacobian加重射影坐标下两点相加
    # SM2第1部分 A.1.2.3.2
    # 输入点包含两项时为仿射坐标，三项为Jacobian加重射影坐标，两点坐标系可不同
    # 两点相同时省略第二个参数
    def Jacb_add(self, P1, P2=None):
        if P2 is None or P1 == P2:  # 相同点相加
            # 处理无穷远点
            if P1 == self.O:
                return self.O

            # 根据参数包含的项数判断坐标系（是仿射坐标则转Jacobian坐标）
            x1, y1, z1 = P1 if len(P1) == 3 else (*P1, 1)

            # t1 = 3 * x1**2 + self.a * pow(z1, 4, self.p)
            # t2 = 4 * x1 * y1**2
            # t3 = 8 * pow(y1, 4, self.p)
            # x3 = (t1**2 - 2 * t2) % self.p
            # y3 = (t1 * (t2 - x3) - t3) % self.p
            # z3 = 2 * y1 * z1 % self.p
            z3 = (y1 * z1 << 1) % self.p
            if z3 == 0:  # 处理无穷远点
                return self.O
            T2 = y1 * y1 % self.p
            T4 = (T2 << 3) % self.p
            T5 = x1 * T4 % self.p
            T6 = z1 * z1 % self.p
            T1 = (x1 + T6) * (x1 - T6) * 3 % self.p
            T1 = (T1 + self.a_3 * T6 * T6) % self.p
            T3 = T1 * T1 % self.p
            T2 = T2 * T4 % self.p
            x3 = (T3 - T5) % self.p
            T4 = T5 + (T5 + self.p >> 1) - T3 if T5 & 1 else T5 + (T5 >> 1) - T3
            T1 = T1 * T4 % self.p
            y3 = (T1 - T2) % self.p
        else:  # 不同点相加
            # 处理无穷远点
            if P1 == self.O:
                return P2
            if P2 == self.O:
                return P1

            # 根据参数包含的项数判断坐标系（是仿射坐标则转Jacobian坐标）
            x1, y1, z1 = P1 if len(P1) == 3 else (*P1, 1)
            x2, y2, z2 = P2 if len(P2) == 3 else (*P2, 1)

            if z2 != 1 and z1 != 1:
                z1_2 = z1 * z1 % self.p
                z2_2 = z2 * z2 % self.p
                t1 = x1 * z2_2 % self.p
                t2 = x2 * z1_2 % self.p
                t3 = t1 - t2
                z3 = z1 * z2 * t3 % self.p
                if z3 == 0:  # 处理无穷远点
                    return self.O
                t4 = y1 * z2 * z2_2 % self.p
                t5 = y2 * z1 * z1_2 % self.p
                t6 = t4 - t5
                t7 = t1 + t2
                t8 = t4 + t5
                t3_2 = t3 * t3 % self.p
                x3 = (t6 * t6 - t7 * t3_2) % self.p
                t9 = (t7 * t3_2 - (x3 << 1)) % self.p
                y3 = (t9 * t6 - t8 * t3 * t3_2) * self._2 % self.p
            else:  # 可简化计算
                if z1 == 1:  # 确保第二个点的z1=1
                    x1, y1, z1, x2, y2 = x2, y2, z2, x1, y1
                T1 = z1 * z1 % self.p
                T2 = y2 * z1 % self.p
                T3 = x2 * T1 % self.p
                T1 = T1 * T2 % self.p
                T2 = T3 - x1
                z3 = z1 * T2 % self.p
                if z3 == 0:  # 处理无穷远点
                    return self.O
                T3 = T3 + x1
                T1 = T1 - y1
                T4 = T2 * T2 % self.p
                T5 = T1 * T1 % self.p
                T2 = T2 * T4 % self.p
                T3 = T3 * T4 % self.p
                T4 = x1 * T4 % self.p
                x3 = T5 - T3 % self.p
                T2 = y1 * T2 % self.p
                T3 = T4 - x3
                T1 = T1 * T3 % self.p
                y3 = T1 - T2 % self.p
                # T1 = z1 * z1 % self.p
                # T3 = x2 * T1 % self.p
                # T2 = T3 - x1
                # z3 = z1 * T2 % self.p
                # if z3 == 0: # 处理无穷远点
                # return self.O
                # T1 = (T1 * y2 * z1  - y1) % self.p
                # T4 = T2 * T2 % self.p
                # x3 = T1 * T1 - (T3 + x1) * T4 % self.p
                # T1 = T1 * (x1 * T4 - x3) % self.p
                # y3 = T1 - y1 * T2 * T4 % self.p

        return x3, y3, z3

    # Jacobian加重射影坐标下的点乘运算
    # SM2第1部分 A.3
    # 输入点包含两项时为仿射坐标，三项为Jacobian坐标
    # conv=True时结果转换为仿射坐标，否则不转换
    # algo表示选择的算法， r表示算法三（滑动窗法）的窗口值
    def Jacb_multiply(self, k, P, conv=True, algo=2, r=5):
        # 处理无穷远点
        if k == 0 or P == self.O:
            return self.O

        # 仿射坐标转Jacobian坐标
        # if len(P) == 2:
        # P = (*P, 1)

        # 算法一：二进制展开法
        if algo == 1:
            Q = P
            for i in bin(k)[3:]:
                Q = self.Jacb_add(Q)
                if i == '1':
                    Q = self.Jacb_add(Q, P)

        # 算法二：加减法
        elif algo == 2:
            h = bin(3 * k)[2:]
            k = bin(k)[2:]
            k = '0' * (len(h) - len(k)) + k
            Q = P
            minusP = self.minus(P)
            for i in range(1, len(h) - 1):
                Q = self.Jacb_add(Q)
                if h[i] == '1' and k[i] == '0':
                    Q = self.Jacb_add(Q, P)
                elif h[i] == '0' and k[i] == '1':
                    Q = self.Jacb_add(Q, minusP)

        # 算法三：滑动窗法
        # 当k为255/256位时，通过test_r函数测试，r=5复杂度最低
        elif algo == 3:
            k = bin(k)[2:]
            l = len(k)
            if r >= l:  # 如果窗口大于k的二进制位数，则本算法无意义
                return self.Jacb_multiply(int(k, 2), P, conv, 2)

            # 保存P[j]值的字典
            P_ = {1: P, 2: self.Jacb_add(P)}
            for i in range(1, 1 << (r - 1)):
                P_[(i << 1) + 1] = self.Jacb_add(P_[(i << 1) - 1], P_[2])

            t = r
            while k[t - 1] != '1':
                t -= 1
            hj = int(k[:t], 2)
            Q = P_[hj]
            j = t
            while j < l:
                if k[j] == '0':
                    Q = self.Jacb_add(Q)
                    j += 1
                else:
                    t = min(r, l - j)
                    while k[j + t - 1] != '1':
                        t -= 1
                    hj = int(k[j:j + t], 2)
                    Q = self.Jacb_add(self.Jacb_multiply(1 << t, Q, False, 2), P_[hj])
                    j += t

        return self.Jacb_to_affine(Q) if conv else Q

    # Jacobian加重射影坐标转仿射坐标
    # SM2第1部分 A.1.2.3.2
    def Jacb_to_affine(self, P):
        if len(P) == 2:  # 已经是仿射坐标
            return P
        x, y, z = P
        # 处理无穷远点
        if z == 0:
            return self.O
        z_ = get_inverse(z, self.p)  # z的乘法逆元
        x2 = x * z_ * z_ % self.p
        y2 = y * z_ * z_ * z_ % self.p
        return x2, y2

    # 判断是否为无穷远点（零点）
    def is_zero(self, P):
        if len(P) == 2:  # 仿射坐标
            return P == self.O
        else:  # Jacobian加重射影坐标
            return P[2] == 0

    # 判断是否为域Fp中的元素
    # 可输入多个元素，全符合才返回True
    def on_Fp(self, *x):
        for i in x:
            if 0 <= i < self.p:
                pass
            else:
                return False
        return True

    # 判断是否在椭圆曲线上
    def on_curve(self, P):
        if self.is_zero(P):
            return False
        if len(P) == 2:  # 仿射坐标
            x, y = P
            return y * y % self.p == (x * x * x + self.a * x + self.b) % self.p
        else:  # Jacobian加重射影坐标
            x, y, z = P
            return y * y % self.p == (x * x * x + self.a * x * pow(z, 4, self.p) + self.b * pow(z, 6, self.p)) % self.p

    # 生成密钥对
    # 返回值：d为私钥，P为公钥
    # SM2第1部分 6.1
    def gen_keypair(self):
        d = random.randint(1, self.n - 2)
        P = self.Jacb_multiply(d, self.G)
        return d, P

    # 公钥验证
    # SM2第1部分 6.2.1
    def pk_valid(self, P):
        # 判断点P的格式
        if P and len(P) == 2 and type(P[0]) == type(P[1]) == int:
            pass
        else:
            self.error = '格式有误'  # 记录错误信息
            return False
        # a) 验证P不是无穷远点O
        if self.is_zero(P):
            self.error = '无穷远点'
            return False
        # b) 验证公钥P的坐标xP和yP是域Fp中的元素
        if not self.on_Fp(*P):
            self.error = '坐标值不是域Fp中的元素'
            return False
        # c) 验证y^2 = x^3 + ax + b (mod p)
        if not self.on_curve(P):
            self.error = '不在椭圆曲线上'
            return False
        # d) 验证[n]P = O
        if not self.is_zero(self.Jacb_multiply(self.n, P, False)):
            self.error = '[n]P不是无穷远点'
            return False
        return True

    # 确认目前已有公私钥对
    def confirm_keypair(self):
        if not hasattr(self, 'pk') or not self.pk_valid(self.pk) or self.pk != self.Jacb_multiply(self.sk, self.G):
            # 目前没有合格的公私钥对则生成
            while True:
                d, P = self.gen_keypair()
                if self.pk_valid(P):  # 确保公钥通过验证
                    self.sk, self.pk = d, P
                    return


# 国家密码管理局：SM2椭圆曲线公钥密码算法推荐曲线参数
SM2_p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
SM2_a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
SM2_b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
SM2_n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
SM2_Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
SM2_Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0

PARA_SIZE = 32  # 参数长度（字节）
HASH_SIZE = 32  # sm3输出256位（32字节）
KEY_LEN = 128  # 默认密钥位数


# SM2类继承ECC
class SM2(ECC):
    # 默认使用SM2推荐曲线参数
    def __init__(self, p=SM2_p, a=SM2_a, b=SM2_b, n=SM2_n, G=(SM2_Gx, SM2_Gy), h=None,
                 ID=None, sk=None, pk=None, genkeypair=True):  # genkeypair表示是否自动生成公私钥对
        if not h:  # 余因子h默认为1
            h = 1
        ECC.__init__(self, p, a, b, n, G, h)

        self.keysize = len(to_byte(n))  # 密钥长度（字节）
        if type(ID) in (int, str):  # 身份ID（数字或字符串）
            self.ID = ID
        else:
            self.ID = ''
        if sk and pk:  # 如果提供的公私钥对通过验证，即使genkeypair=True也不会重新生成
            self.sk = sk  # 私钥（int [1,n-2]）
            self.pk = pk  # 公钥（x, y）
            self.confirm_keypair()  # 验证该公私钥对，不合格则生成
        elif genkeypair:  # 自动生成合格的公私钥对
            self.confirm_keypair()

        # 预先计算用到的常数
        if hasattr(self, 'sk'):  # 签名时
            self.d_1 = get_inverse(1 + self.sk, self.n)

    # 椭圆曲线系统参数验证
    # SM2第1部分 5.2.2
    def para_valid(self):
        # a) 验证q = p是奇素数
        if not is_prime(self.p):
            self.error = 'p不是素数'  # 记录错误信息
            return False
        # b) 验证a、b、Gx和Gy是区间[0, p−1]中的整数
        if not self.on_Fp(self.a, self.b, *self.G):
            self.error = 'a、b或G坐标值不是域Fp中的元素'
            return False
        # d) 验证(4a^3 + 27b^2) mod p != 0
        if (4 * self.a * self.a * self.a + 27 * self.b * self.b) % self.p == 0:
            self.error = '(4a^3 + 27b^2) mod p = 0'
            return False
        # e) 验证Gy^2 = Gx^3 + aGx + b (mod p)
        if not self.on_curve(self.G):
            self.error = 'G不在椭圆曲线上'
            return False
        # f) 验证n是素数，n > 2^191 且 n > 4p^1/2
        if not is_prime(self.n) or self.n <= 1 << 191 or self.n <= 4 * self.p ** 0.5:
            self.error = 'n不是素数或n不够大'
            return False
        # g) 验证[n]G = O
        if not self.is_zero(self.Jacb_multiply(self.n, self.G, False)):
            self.error = '[n]G不是无穷远点'
            return False
        # i) 验证抗MOV攻击条件和抗异常曲线攻击条件成立（A.4.2.1）
        B = 27  # MOV阈B
        t = 1
        for i in range(B):
            t = t * self.p % self.n
            if t == 1:
                self.error = '不满足抗MOV攻击条件'
                return False
        # 椭圆曲线的阶N=#E(Fp)计算太复杂，未实现A.4.2.2验证
        # Fp上的绝大多数椭圆曲线确实满足抗异常曲线攻击条件
        return True

    # 计算Z
    # SM2第2部分 5.5
    # ID为数字或字符串，P为公钥（不提供参数时返回自身Z值）
    def get_Z(self, ID=None, P=None):
        save = False
        if not P:  # 不提供参数
            if hasattr(self, 'Z'):  # 再次计算，返回曾计算好的自身Z值
                return self.Z
            else:  # 首次计算自身Z值
                ID = self.ID
                P = self.pk
                save = True
        entlen = get_bit_num(ID)
        ENTL = to_byte(entlen, 2)
        Z = sm3(join_bytes([ENTL, ID, self.a, self.b, *self.G, *P]))
        if save:  # 保存自身Z值
            self.Z = Z
        return Z

    # 数字签名
    # SM2第2部分 6.1
    # 输入：待签名的消息M、随机数k（不填则自动生成）、输出类型（默认bytes）、对M是否hash（默认是）
    # 输出：r, s（int类型）或拼接后的bytes
    def sign(self, M, k=None, outbytes=True, dohash=True):
        if dohash:
            M_ = join_bytes([self.get_Z(), M])
            e = to_int(sm3(M_))
        else:
            e = to_int(to_byte(M))
        while True:
            if not k:
                k = random.randint(1, self.n - 1)
            # x1, y1 = self.multiply(k, self.G)
            x1, y1 = self.Jacb_multiply(k, self.G)
            r = (e + x1) % self.n
            if r == 0 or r + k == self.n:
                k = 0
                continue
            # s = get_inverse(1 + self.sk, self.n) * (k - r * self.sk) % self.n
            s = self.d_1 * (k - r * self.sk) % self.n
            if s == 0:
                k = 0
            else:
                break
        if outbytes:
            return to_byte((r, s), self.keysize)
        else:
            return r, s,e

    # 数字签名验证
    # SM2第2部分 7.1
    # 输入：收到的消息M′及其数字签名(r′, s′)、签名者的身份标识IDA及公钥PA、对M是否hash（默认是）
    # 输出：True or False
    def verify(self, M, sig, IDA, PA, dohash=True):
        if isinstance(sig, bytes):
            r = to_int(sig[:self.keysize])
            s = to_int(sig[self.keysize:])
        else:
            r, s = sig
        if not 1 <= r <= self.n - 1:
            return False
        if not 1 <= s <= self.n - 1:
            return False
        if dohash:
            M_ = join_bytes([self.get_Z(IDA, PA), M])
            e = to_int(sm3(M_))
        else:
            e = to_int(to_byte(M))
        t = (r + s) % self.n
        if t == 0:
            return False
        sG = self.Jacb_multiply(s, self.G, False)
        tPA = self.Jacb_multiply(t, PA, False)
        x1, y1 = self.Jacb_to_affine(self.Jacb_add(sG, tPA))
        R = (e + x1) % self.n
        if R == r:
            return True
        else:  # 避免Jacobian坐标下的等价点导致判断失败
            x1, y1 = self.add(self.Jacb_to_affine(sG), self.Jacb_to_affine(tPA))
            R = (e + x1) % self.n
            return R == r



# SM2示例中的椭圆曲线系统参数
def demo_para():
    p = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
    a = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
    b = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
    xG = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
    yG = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    G = (xG, yG)
    h = 1
    return p, a, b, n, G, h


def deterministic_generate_k(msghash, priv):
    v = b'\x01' * 32
    k = b'\x00' * 32
    priv = bitcoin.encode_privkey(priv, 'bin')
    msghash = bitcoin.encode(bitcoin.hash_to_int(msghash), 256, 32)
    k = bitcoin.hmac.new(k, v + b'\x00' + priv + msghash, bitcoin.hashlib.sha256).digest()
    v = bitcoin.hmac.new(k, v, bitcoin.hashlib.sha256).digest()
    k = bitcoin.hmac.new(k, v + b'\x01' + priv + msghash, bitcoin.hashlib.sha256).digest()
    v = bitcoin.hmac.new(k, v, bitcoin.hashlib.sha256).digest()
    return bitcoin.decode(bitcoin.hmac.new(k, v, bitcoin.hashlib.sha256).digest(), 256)

# SM2数字签名与验证测试
# SM2第2部分 A.1 A.2
def test_signature():
    IDA = 'ALICE123@YAHOO.COM'
    M = 'message digest'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    # A、B双方初始化
    sm2_A = SM2(*demo_para(), IDA, dA, PA)
    sm2_B = SM2(*demo_para())
    M_ = join_bytes([sm2_A.get_Z(), M])
    k1 = deterministic_generate_k(M_, dA)
    #print("新生成的k为：",k1)
    time_1 = get_cpu_time()
    sig = sm2_A.sign(M, k)
    # B对消息M签名进行验证
    res = sm2_B.verify(M, sig, IDA, PA)
    time_2 = get_cpu_time()
    print('SM2签名、验证完毕，耗时%.2f ms' % ((time_2 - time_1) * 1000))
    print('结果：%s，r值：%s' % (res, sig[:sm2_A.keysize].hex()))
    print('结果：%s，s值：%s' % (res, sig[sm2_A.keysize:2*sm2_A.keysize].hex()))
    # 验证通过，输出的r值(40f1ec59f793d9f49e09dcef49130d4194f79fb1eed2caa55bacdb49c4e755d1)与SM2第2部分 A.2中的结果一致
def pk_fron_signature():
    IDA = 'ALICE123@YAHOO.COM'
    M = 'message digest'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    a = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
    b = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
    xG = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
    yG = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
    G=(xG,yG)
    sm2_A = SM2(*demo_para(), IDA, dA, PA)
    sm2_B = SM2(*demo_para())
    # A、B双方初始化
    # A对消息M进行签名
    r,s,e = sm2_A.sign(M, k,0,)
    # A将消息M签名(r, s)发送给B
    xA1 = 0x0
    yA1 = 0x0
    x1 = (r- e) % n;
    #y1 = pow((x1 * x1 * x1 + a * x1 + b)%n,0.5);
    y1=12844692015861483985796897070387313459524129685989174230708833771946472557082
    kG = (x1, y1)
    fan = sm2_A.minus(sm2_A.Jacb_multiply(s, G))
    xA1, yA1 = sm2_A.Jacb_multiply(get_inverse(r + s, n), sm2_A.add(kG, fan));
    xA1=hex(xA1);
    yA1 = hex(yA1);
    PA1 = (xA1, yA1)
    print("公钥为",PA1)
def leaking_k():
    IDA = 'ALICE123@YAHOO.COM'
    M = 'message digest'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    # A、B双方初始化
    sm2_A = SM2(*demo_para(), IDA, dA, PA)
    sm2_B = SM2(*demo_para())
    r, s,e= sm2_A.sign(M, k, 0, )
    d=get_inverse(r + s, n)*(k-s)%n;
    print("d为：",hex(d))
def reusing_k():
    IDA1 = 'ALICE123@YAHOO.COM'
    M1 = 'message digest'
    IDA2 = 'BOB123@YAHOO.COM'
    M2 = 'practice'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    # A、B双方初始化
    sm2_A1 = SM2(*demo_para(), IDA1, dA, PA)
    sm2_B1 = SM2(*demo_para())
    r1, s1, e1 = sm2_A1.sign(M1, k, 0, )
    sm2_A2 = SM2(*demo_para(), IDA2, dA, PA)
    sm2_B2 = SM2(*demo_para())
    r2, s2, e2 = sm2_A1.sign(M2, k, 0, )
    d = ((s2 - s1) * get_inverse(s1 - s2 + r1 - r2, n)) % n;
    print("d为：", hex(d))
def Malleability():
    IDA = 'ALICE123@YAHOO.COM'
    M = 'message digest'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    # A、B双方初始化
    sm2_A = SM2(*demo_para(), IDA, dA, PA)
    sm2_B = SM2(*demo_para())
    r, s, e = sm2_A.sign(M, k, 0, )
    keysize = len(to_byte(n))
    sig1=to_byte((r, s), keysize)
    sig2 = to_byte((r, (-s)%n), keysize)
    res1 = sm2_B.verify(M, sig1, IDA, PA)
    res2 = sm2_B.verify(M, sig2, IDA, PA)
    print(res1,res2)
def same_d_k():
    IDA1 = 'ALICE123@YAHOO.COM'
    M1 = 'message digest'
    IDA2 = 'BOB123@YAHOO.COM'
    M2 = 'practice'
    dA = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    xA = 0x0AE4C7798AA0F119471BEE11825BE46202BB79E2A5844495E97C04FF4DF2548A
    yA = 0x7C0240F88F1CD4E16352A73C17B7F16F07353E53A176D684A9FE0C6BB798E857
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    PA = (xA, yA)
    k = 0x6CB28D99385C175C94F94E934817663FC176D925DD72B727260DBAAE1FB2F96F
    # A、B双方初始化
    sm2_A1 = SM2(*demo_para(), IDA1, dA, PA)
    sm2_B1 = SM2(*demo_para())
    r1, s1, e1 = sm2_A1.sign(M1, k, 0, )
    sm2_A2 = SM2(*demo_para(), IDA2, dA, PA)
    sm2_B2 = SM2(*demo_para())
    r2, s2, e2 = sm2_A1.sign(M2, k, 0, )
    d = ((s2 - s1) * get_inverse(s1 - s2 + r1 - r2, n)) % n;
    print("d为：",hex(d))
def twoP_sign():
    IDA = 'ALICE123@YAHOO.COM'
    IDB = 'BOB123@YAHOO.COM'
    M = 'message digest'
    n = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
    xG = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
    yG = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
    G=(xG,yG)
    d1= random.randint(1, n - 1)
    sm2_A = SM2(*demo_para(),);sm2_B = SM2(*demo_para(),)
    p1=(0,0)
    p=(0,0)
    p1=sm2_A.Jacb_multiply(get_inverse(d1, n),G)
    d2 = random.randint(1, n - 1)
    d=get_inverse(d1*d2,n)-1
    fan = sm2_B.minus(G)
    p2=sm2_B.Jacb_multiply(get_inverse(d2, n),G)
    p = sm2_B.add(sm2_B.Jacb_multiply(get_inverse(d2, n), p1),fan)  #公钥
    sm2_A =SM2(*demo_para(),IDA,d,p )
    sm2_B= SM2(*demo_para(), IDB, d, p)
    k1 = random.randint(1, n - 1)
    q1=(0,0)
    q1=sm2_A.Jacb_multiply(k1,G)
    M_ = join_bytes([sm2_A.get_Z(), M])
    e = to_int(sm3(M_))

    k2 = random.randint(1, n - 1)
    k3 = random.randint(1, n - 1)
    q2 = (0, 0);x1=0;y1=0;
    q2 = sm2_B.Jacb_multiply(k2, G)
    x1,y1=sm2_B.add(sm2_B.Jacb_multiply(k3, q1),q2)
    q3 = (x1, y1)
    r=(x1+e)%n
    s2=(d2*k3)%n
    s3=(d2*(r+k2))%n
    s=((d1*k1)*s2+d1*s3-r)%n
    print("签名为：",hex(r),hex(s))
    keysize = len(to_byte(n))
    sig = to_byte((r, s), keysize)
    res = sm2_A.verify(M, sig, IDA, p)
    print("验证签名为：",res)

if __name__ == "__main__":
    #test_signature()
    #pk_fron_signature()
    #leaking_k()
    #reusing_k()
    #Malleability()
    #same_d_k()
    twoP_sign()
