define i32 @fib(i32 %n) {
entry:
	%retval = alloca i32
	%n.addr = alloca i32
	%a = alloca i32
	%b = alloca i32
	%i = alloca i32
	%c = alloca i32
	store i32 %n, ptr %n.addr
	store i32 0, ptr %a
	store i32 1, ptr %b
	store i32 1, ptr %i
	store i32 0, ptr %c
	%0 = load i32, ptr %n.addr
	%cmp = icmp eq i32 %0, 0
	br i1 %cmp, label %if.then, label %if.end
if.then:
	store i32 0, ptr %retval
	br label %return
if.end:
	br label %while.cond
while.cond:
	%1 = load i32, ptr %i
	%2 = load i32, ptr %n.addr
	%cmp1 = icmp slt i32 %1, %2
	br i1 %cmp1, label %while.body, label %while.end
while.body:
	%3 = load i32, ptr %b
	store i32 %3, ptr %c
	%4 = load i32, ptr %a
	%5 = load i32, ptr %b
	%add = add i32 %4, %5
	store i32 %add, ptr %b
	%6 = load i32, ptr %c
	store i32 %6, ptr %a
	%7 = load i32, ptr %i
	%add2 = add i32 %7, 1
	store i32 %add2, ptr %i
	br label %while.cond
while.end:
	%8 = load i32, ptr %b
	store i32 %8, ptr %retval
	br label %return
return:
	%9 = load i32, ptr %retval
	ret i32 %9
}

