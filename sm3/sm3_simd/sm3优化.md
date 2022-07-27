# 基础 SM3 算法

## 实验目的

实现一个基础的单线程 C++ 语言版本的 SM3 算法，并验证其正确性。

## 算法实现

### 消息填充

SM3的消息扩展步骤是以512位的数据分组作为输入的。因此，我们需要在一开始就把数据长度填充至512位的倍数。数据填充规则和MD5一样，具体步骤如下：

1. 先填充一个“1”，后面加上k个“0”。其中k是满足(n+1+k) mod 512 = 448的最小正整数。
2. 追加64位的数据长度

例如:对消息01100001 01100010 01100011，其长度l=24，经填充得到比特串:
![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/simd2.png?raw=true)

### 消息扩展

SM3的迭代压缩步骤没有直接使用数据分组进行运算，而是使用这个步骤产生的132个消息字。（一个消息字的长度为32位/4个节/8个16j进制数字）概括来说，先将一个512位数据分组划分为16个消息字，并且作为生成的132个消息字的前16个。再用这16个消息字递推生成剩余的116个消息字。

在最终得到的132个消息字中，前68个消息字构成数列 $\{ W_{j} \}$，后64个消息字构成数列 $\{ W_{j}' \}$，其中下标j从0开始计数。

将消息分组$B^{(i)}$按以下方法扩展生成132个字$W_{0},W_{1},\ldots,W_{67},W_{0}'W_{1}',\ldots,W_{63}'$，用于压缩函数CF:

a)将消息分组$B^{(i)}$划分为16个字$W_{0}, W_{1},\ldots, W_{15}$。

b)FOR j=16 TO 67

​    $W_{j} \rightarrow P_{1}(W_{j-16}\oplus W_{j-9}\oplus(W_{j-3}\lll15))\oplus (W_{j-13}\lll7)\oplus W_{j-6}$

​     ENDFOR     

c)FOR j=0 TO 63

   $W_{j}' =W_{j}\oplus W_{j+4}$

​    ENDFOR

### 迭代压缩

在上文已经提过，SM3的迭代过程和MD5类似，也是Merkle-Damgard结构。但和MD5不同的是，SM3使用消息扩展得到的消息字进行运算。这个迭代过程可以用这幅图表示：
![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/simd3.png?raw=true)

初值IV被放在A、B、C、D、E、F、G、H八个32位变量中。整个算法中最核心、也最复杂的地方就在于压缩函数。压缩函数将这八个变量进行64轮相同的计算，一轮的计算过程如下图所示：
![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/simd4.png?raw=true)

### 压缩函数

令A,B,C,D,E,F,G,H为字寄存器,$SS1,SS2,TT1,TT2$为中间变量,压缩函数$V^{i+l} = CF(V^{(i)},B^{(i)},0 \leq i\leq n-1$​。计算过程描述如下:

$ABCDEFGH\leftarrow v^{(i)}$

$FOR\:j=0\:TO\:63$

$SS1\leftarrow((A\lll12)+E+(T_{j}\lll j))\lll7$

$SS2\leftarrow SS1\oplus (A \lll12)$

$TT1\leftarrow FF_{j}(A,B,C)+D+SS2+ W_{j}'$

$TT2\leftarrow GG_{j}(E,F,G)+H+SS1+W_{j}$

$D\leftarrow C$

$C\leftarrow B\lll 9$

$B\leftarrow A$

$A\leftarrow TT1$

$H\leftarrow G$

$G\leftarrow F\lll19$
$F\leftarrow E$

$E\leftarrow P_{0}(TT2)$

$ENDFOR$

$V^{(i+1)}&\leftarrow ABCDEFGH\oplus v^{(i)}$

其中，字的存储为大端(big-endian)格式。

最后，再将计算完成的A、B、C、D、E、F、G、H和原来的A、B、C、D、E、F、G、H分别进行异或，就是压缩函数的输出。这个输出再作为下一次调用压缩函数时的初值。依次类推，直到用完最后一组132个消息字为止。

### 输出结果

将得到的A、B、C、D、E、F、G、H八个变量拼接输出，就是SM3算法的输出。

$ABCDEFGH\leftarrow v^{(n)}$

输出256比特的杂凑值$ y = ABCDEFGH $。

### 数据统计

abc;

杂凑值:66c7f0f4 62eeedd9 d1f2d46b dc10e4e2 4167c487 5cf2f7a2 297da02b 8f4ba8e0

abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd;

杂凑值:debe9ff9 2275b8a1 38604889 c18e5a4d 6fdb70e5 387e5765 293dcba3 9c0c5732

# SM3 算法优化

## 实验目的

采用多线程、SIMD、流水线、循环展开等在各种软件层面加速优化 SM4 算法，并分析优化过的代码的延迟和吞吐量以及相比第 1 部分的单线程基础版本以及开源库的加速比。

## SIMD 指令集优化

将 SM3的消息扩展函数使用SIMD进行优化

![](https://github.com/yuuu218/Innovation-pioneering/blob/main/image/simd1.png?raw=true)

使用SIMD极大的提高了效率。

# 参考文献

[SM3加密算法详解（2021-12-8）](https://blog.csdn.net/qq_40662424/article/details/121637732 )

[[C]跨平台使用 Intrinsic 函数范例 1——使用 SSE、AVX 指令集处理单精度浮点数组求和(支持 vc、gcc，兼容 Windows、Linux、Mac)](https://www.cnblogs.com/zyl910/archive/2012/10/22/simdsumfloat.html)

[数值计算优化方法C/C++(三)——SIMD](https://blog.csdn.net/artorias123/article/details/86524899?utm_source=app&app_version=5.3.0&code=app_1562916241&uLinkId=usr1mkqgl919blen)

[SIMD指令集分析(C/C++)](https://blog.csdn.net/AAAA202012/article/details/123983364?utm_source=app&app_version=4.15.0&code=app_1562916241&uLinkId=usr1mkqgl919blen)

[C++中使用SIMD的方法](https://blog.csdn.net/Mahfaeraak/article/details/88687252?utm_source=app&app_version=4.15.0&code=app_1562916241&uLinkId=usr1mkqgl919blen)

[SIMD指令初学](https://blog.csdn.net/woxiaohahaa/article/details/51014425?ops_request_misc=&request_id=&biz_id=102&utm_term=_mm_load_ps&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-1-51014425.142%5Ev9%5Econtrol,157%5Ev4%5Econtrol&spm=1018.2226.3001.4187)

[How to compile SIMD code with gcc](https://stackoverflow.com/questions/10366670/how-to-compile-simd-code-with-gcc)

