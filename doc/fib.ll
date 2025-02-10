; ModuleID = 'fib.c'
source_filename = "fib.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind
define dso_local i32 @fib(i32 noundef %n) #0 {
entry:
  %retval = alloca i32, align 4
  %n.addr = alloca i32, align 4
  %a = alloca i32, align 4
  %b = alloca i32, align 4
  %i = alloca i32, align 4
  %c = alloca i32, align 4
  store i32 %n, ptr %n.addr, align 4
  store i32 0, ptr %a, align 4
  store i32 1, ptr %b, align 4
  store i32 1, ptr %i, align 4
  store i32 0, ptr %c, align 4
  %0 = load i32, ptr %n.addr, align 4
  %cmp = icmp eq i32 %0, 0
  br i1 %cmp, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  store i32 0, ptr %retval, align 4
  br label %return

if.end:                                           ; preds = %entry
  br label %while.cond

while.cond:                                       ; preds = %while.body, %if.end
  %1 = load i32, ptr %i, align 4
  %2 = load i32, ptr %n.addr, align 4
  %cmp1 = icmp slt i32 %1, %2
  br i1 %cmp1, label %while.body, label %while.end

while.body:                                       ; preds = %while.cond
  %3 = load i32, ptr %b, align 4
  store i32 %3, ptr %c, align 4
  %4 = load i32, ptr %a, align 4
  %5 = load i32, ptr %b, align 4
  %add = add nsw i32 %4, %5
  store i32 %add, ptr %b, align 4
  %6 = load i32, ptr %c, align 4
  store i32 %6, ptr %a, align 4
  %7 = load i32, ptr %i, align 4
  %add2 = add nsw i32 %7, 1
  store i32 %add2, ptr %i, align 4
  br label %while.cond, !llvm.loop !2

while.end:                                        ; preds = %while.cond
  %8 = load i32, ptr %b, align 4
  store i32 %8, ptr %retval, align 4
  br label %return

return:                                           ; preds = %while.end, %if.then
  %9 = load i32, ptr %retval, align 4
  ret i32 %9
}

attributes #0 = { noinline nounwind "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Debian clang version 16.0.6 (27)"}
!2 = distinct !{!2, !3}
!3 = !{!"llvm.loop.mustprogress"}
