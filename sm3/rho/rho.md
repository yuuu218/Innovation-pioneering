# 方法一

从一个初始值a出发，a=f(a),不断计算SM3值，就可能成环（前n bit)

## python运行结果

f=2x+1

8bit:

![](C:\Users\74463\Desktop\8.png)

12bit:

![](C:\Users\74463\Desktop\12.png)

16bit:

![](C:\Users\74463\Desktop\16.png)

20bit:

![](C:\Users\74463\Desktop\20.png)

24bit：

![](C:\Users\74463\Desktop\24.png)

28bit:

![](C:\Users\74463\Desktop\28.png)

# 方法二

从一个初始值出发，a=sm3(a),不断计算SM3值，就可能成环（前n bit)

```c++
    string kaishi = strRand(16);
	vector<string> temp;
	while (1) {
		string hh(sm3(kaishi), 0, bit / 4);
		temp.push_back(hh);
		cout << hh<< endl;
		kaishi = sm3(kaishi);
		string xx(sm3(kaishi), 0, bit / 4);
		vector<string>::iterator result = find(temp.begin(), temp.end(), xx); //查找3
		if (result != temp.end()) //找到
		{
			cout << xx << endl;
			cout << "Yes" << endl;
			return;
		}
```



## C++运行结果

8bit:

![](C:\Users\74463\Desktop\cpp8.png)

12bit:

![](C:\Users\74463\Desktop\cpp12.png)

16bit:

![](C:\Users\74463\Desktop\cpp16.png)

20bit:

![](C:\Users\74463\Desktop\cpp20.png)

24bit:

![](C:\Users\74463\Desktop\cpp24.png)