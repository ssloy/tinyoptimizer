define i32 @fib(i32 %n) {
entry:
	%cmp = icmp eq i32 %n, 0
	br i1 %cmp, label %if.then, label %if.end
if.then:
	br label %return
if.end:
	br label %while.cond
while.cond:
	%a_while.cond = phi i32 [0, %if.end], [%b_while.cond, %while.body]
	%b_while.cond = phi i32 [1, %if.end], [%add, %while.body]
	%i_while.cond = phi i32 [1, %if.end], [%add2, %while.body]
	%c_while.cond = phi i32 [0, %if.end], [%b_while.cond, %while.body]
	%cmp1 = icmp slt i32 %i_while.cond, %n
	br i1 %cmp1, label %while.body, label %while.end
while.body:
	%add = add i32 %a_while.cond, %b_while.cond
	%add2 = add i32 %i_while.cond, 1
	br label %while.cond
while.end:
	br label %return
return:
	%retval_return = phi i32 [0, %if.then], [%b_while.cond, %while.end]
	%a_return = phi i32 [0, %if.then], [%a_while.cond, %while.end]
	%b_return = phi i32 [1, %if.then], [%b_while.cond, %while.end]
	%i_return = phi i32 [1, %if.then], [%i_while.cond, %while.end]
	%c_return = phi i32 [0, %if.then], [%c_while.cond, %while.end]
	ret i32 %retval_return
}

