#!/bin/bash

#shell变量、参数、数组
name='cuixing'  #变量赋值等号两边不能有空格
echo "字符串："$name
echo "获取字符串长度："${#name}
echo "提取字符串第2到6位(索引从0开始)："${name:1:5} 
echo "查找子字符串i或n所在位置(索引从1开始)："`expr index "${name}" ix` 	

arr=(1 2 3 4 5)
echo "列表：("${arr[*]}")"
echo "读取数组第一位："${arr[0]}
echo "读取数组所有位："${arr[*]}
echo "获取数组长度："${#arr[*]}

echo "传递参数:"				 #传递参数
echo "执行的文件名:$0"
echo "第一个参数:$1"
echo "参数个数:$#"
echo "显示所有参数:$*"

#$*和$@的区别
echo "---\$*演示---" 			 #$*相当于传递了一个参数
for i in "$*"
do
	echo $i
done

echo "---\$@演示---"			 #$@相当于传递了n个参数
for i in $@;do
	echo $i
done

#shell运算符
a=10
b=20
val=`expr $a + $b`				#expr是一款表达式计算工具，表达式和运算符之间要有空格，如2 + 2，完整的表达式要被` `包含
echo "a + b : $val"
val=`expr $a \* $b`             #乘号(*)前边必须加反斜杠(\)才能实现乘法运算；
echo "a * b : $val"

if [ $a != $b ]				    #条件表达式要放在方括号之间，并且要有空格，例如: [$a==$b] 是错误的，必须写成 [ $a == $b ]
then
   echo "a 不等于 b"
fi

#shell echo命令
echo `date`						#显示当前时间日期
echo `date` > myfile			#重定向到文件

#shell printf命令
printf "%d %s %.2f\n" 6 "cx" 6.666 #printf不能自动换行

#shell流程控制
int=1
while(($int<=5))
do
	echo $int
	let "int++"                  #let命令后的变量不需要加$
done


#shell函数
funWithReturn()
{
    echo "这个函数会对输入的两个数字进行相加运算..."
	echo "输入第一个数字: "
	read aNum
	echo "输入第二个数字: "
	read anotherNum
	echo "两个数字分别为 $aNum 和 $anotherNum !"
	return $(($aNum+$anotherNum))
}
funWithReturn
echo "输入的两个数字之和为 $? !"  #函数返回值在调用该函数后通过 $? 来获得


#批量修改文件夹下的图片名称，以顺延后缀方式重命名
for name in LiuShiShi/*
do
	echo $name
	let i=i+1
	new=$i
	echo $new
	mv $name LiuShiShi/"LiuShiShi"_$new.jpg
done


#小数运算
no=22
result=`echo "$no * 1.3" | bc`
echo $result
