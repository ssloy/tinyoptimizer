# Can I make an *optimizing* compiler under 1k lines of code?
## N.B.: Under construction! This is a fork of my tinycompiler, and I have no idea where it is going.

![](https://ssloy.github.io/tinyoptimizer/home/tinyoptimizer.png)

Here I am playing with code optimizations, if you are interested in lexer/parser/symbol tables and assembly generation, check the [tinycompiler](https://github.com/ssloy/tinycompiler).

The target language for tinycompiler is GNU assembly, however, I need some intermediate representation for the optimization phase. I chose to drop assembly for the moment and I generate LLVM IR language files. While I do not rely on the LLVM library for tinyoptimizer, being compatible with LLVM allows me to run my code directly (check the Makefile) without translating out of the SSA form that can be tricky.

I'll re-add assembly when I am done with optimization passes.
