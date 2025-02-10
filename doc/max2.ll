; ModuleID = 'max.ll'
source_filename = "max.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: noinline nounwind
define dso_local i32 @max(i32 noundef %a, i32 noundef %b) #0 {
entry:
  %cmp = icmp sgt i32 %b, %a
  br i1 %cmp, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  br label %if.end

if.end:                                           ; preds = %if.then, %entry
  %result.0 = phi i32 [ %b, %if.then ], [ %a, %entry ]
  ret i32 %result.0
}

; Function Attrs: noinline nounwind
define dso_local i32 @loop() #0 {
entry:
  br label %while.cond

while.cond:                                       ; preds = %while.body, %entry
  %i.0 = phi i32 [ 0, %entry ], [ %inc, %while.body ]
  %cmp = icmp slt i32 %i.0, 10
  br i1 %cmp, label %while.body, label %while.end

while.body:                                       ; preds = %while.cond
  %inc = add nsw i32 %i.0, 1
  br label %while.cond, !llvm.loop !2

while.end:                                        ; preds = %while.cond
  ret i32 %i.0
}

attributes #0 = { noinline nounwind "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-features"="+cx8,+mmx,+sse,+sse2,+x87" }

!llvm.module.flags = !{!0}
!llvm.ident = !{!1}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{!"Debian clang version 16.0.6 (27)"}
!2 = distinct !{!2, !3}
!3 = !{!"llvm.loop.mustprogress"}
