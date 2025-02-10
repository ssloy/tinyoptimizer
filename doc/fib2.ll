; ModuleID = 'fib.ll'
source_filename = "fib.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind
define dso_local i32 @fib(i32 noundef %n) #0 {
entry:
  %cmp = icmp eq i32 %n, 0
  br i1 %cmp, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  br label %return

if.end:                                           ; preds = %entry
  br label %while.cond

while.cond:                                       ; preds = %while.body, %if.end
  %i.0 = phi i32 [ 1, %if.end ], [ %add2, %while.body ]
  %b.0 = phi i32 [ 1, %if.end ], [ %add, %while.body ]
  %a.0 = phi i32 [ 0, %if.end ], [ %b.0, %while.body ]
  %cmp1 = icmp slt i32 %i.0, %n
  br i1 %cmp1, label %while.body, label %while.end

while.body:                                       ; preds = %while.cond
  %add = add nsw i32 %a.0, %b.0
  %add2 = add nsw i32 %i.0, 1
  br label %while.cond, !llvm.loop !2

while.end:                                        ; preds = %while.cond
  br label %return

return:                                           ; preds = %while.end, %if.then
  %retval.0 = phi i32 [ 0, %if.then ], [ %b.0, %while.end ]
  ret i32 %retval.0
}

attributes #0 = { noinline nounwind "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Debian clang version 16.0.6 (27)"}
!2 = distinct !{!2, !3}
!3 = !{!"llvm.loop.mustprogress"}
