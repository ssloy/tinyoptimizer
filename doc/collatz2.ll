declare i32 @printf(i8*, ...)
@newline = constant [ 2 x i8] c"\0a\00"
@integer = constant [ 3 x i8] c"%d\00"
@string  = constant [ 3 x i8] c"%s\00"
@bool    = constant [11 x i8] c"false\00true\00"

define i32 @main() {
	call void @main_uniqstr2()
	ret i32 0
}
define i32 @collatz_uniqstr1(i32 %collatz_uniqstr1.n.arg) {
entry:
	%uniqstr3 = add i32 0, 0
	br label %uniqstr4.cond
uniqstr4.cond:
	%collatz_uniqstr1.n_uniqstr4.cond = phi i32 [%collatz_uniqstr1.n.arg, %entry], [%collatz_uniqstr1.n_uniqstr16.end, %uniqstr16.end]
	%collatz_uniqstr1.its_uniqstr4.cond = phi i32 [%uniqstr3, %entry], [%uniqstr10, %uniqstr16.end]
	%uniqstr6 = add i32 0, 1
	%uniqstr7 = icmp ne i32 %collatz_uniqstr1.n_uniqstr4.cond, %uniqstr6
	br i1 %uniqstr7, label %uniqstr4.body, label %uniqstr4.end
uniqstr4.body:
	%uniqstr9 = add i32 0, 1
	%uniqstr10 = add i32 %collatz_uniqstr1.its_uniqstr4.cond, %uniqstr9
	%uniqstr12 = add i32 0, 2
	%uniqstr13 = srem i32 %collatz_uniqstr1.n_uniqstr4.cond, %uniqstr12
	%uniqstr14 = add i32 0, 0
	%uniqstr15 = icmp eq i32 %uniqstr13, %uniqstr14
	br i1 %uniqstr15, label %uniqstr16.then, label %uniqstr16.else
uniqstr16.then:
	%uniqstr18 = add i32 0, 2
	%uniqstr19 = sdiv i32 %collatz_uniqstr1.n_uniqstr4.cond, %uniqstr18
	br label %uniqstr16.end
uniqstr16.else:
	%uniqstr20 = add i32 0, 3
	%uniqstr22 = mul i32 %uniqstr20, %collatz_uniqstr1.n_uniqstr4.cond
	%uniqstr23 = add i32 0, 1
	%uniqstr24 = add i32 %uniqstr22, %uniqstr23
	br label %uniqstr16.end
uniqstr16.end:
	%collatz_uniqstr1.n_uniqstr16.end = phi i32 [%uniqstr19, %uniqstr16.then], [%uniqstr24, %uniqstr16.else]
	br label %uniqstr4.cond
uniqstr4.end:
	ret i32 %collatz_uniqstr1.its_uniqstr4.cond
	unreachable
}
define void @main_uniqstr2() {
entry:
	%uniqstr26 = add i32 0, 27
	%uniqstr27 = call i32 @collatz_uniqstr1(i32 %uniqstr26)
	call i32 (i8*, ...)* @printf(ptr @integer, i32 %uniqstr27)
	call i32 (i8*, ...) @printf(ptr @newline)
	ret void
}

