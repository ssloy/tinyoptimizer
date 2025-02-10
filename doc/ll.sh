clang -cc1 -O0 -emit-llvm -disable-O0-optnone max.c -o max.ll
opt -passes=mem2reg max.ll -S -o max2.ll

