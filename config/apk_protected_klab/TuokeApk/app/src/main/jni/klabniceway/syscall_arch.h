//
// Created by li-j on 2021-02-03.
//

#ifdef _64_BIT

#define __SYSCALL_LL_O(x) (x)
#define __SYSCALL_LL_E(x) (x)

#define __asm_syscall(...) do { \
	__asm__ __volatile__ ( "svc 0" \
	: "=r"(x0) : __VA_ARGS__ : "memory", "cc"); \
	return x0; \
	} while (0)

__attribute__((always_inline))
static inline long __syscall0(long n)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0");
	__asm_syscall("r"(x8));
}

__attribute__((always_inline))
static inline long __syscall1(long n, long a)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	__asm_syscall("r"(x8), "0"(x0));
}
__attribute__((always_inline))
static inline long __syscall2(long n, long a, long b)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	register long x1 __asm__("x1") = b;
	__asm_syscall("r"(x8), "0"(x0), "r"(x1));
}
__attribute__((always_inline))
static inline long __syscall3(long n, long a, long b, long c)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	register long x1 __asm__("x1") = b;
	register long x2 __asm__("x2") = c;
	__asm_syscall("r"(x8), "0"(x0), "r"(x1), "r"(x2));
}
__attribute__((always_inline))
static inline long __syscall4(long n, long a, long b, long c, long d)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	register long x1 __asm__("x1") = b;
	register long x2 __asm__("x2") = c;
	register long x3 __asm__("x3") = d;
	__asm_syscall("r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3));
}

__attribute__((always_inline))
static inline long __syscall5(long n, long a, long b, long c, long d, long e)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	register long x1 __asm__("x1") = b;
	register long x2 __asm__("x2") = c;
	register long x3 __asm__("x3") = d;
	register long x4 __asm__("x4") = e;
	__asm_syscall("r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3), "r"(x4));
}

__attribute__((always_inline))
static inline long __syscall6(long n, long a, long b, long c, long d, long e, long f)
{
	register long x8 __asm__("x8") = n;
	register long x0 __asm__("x0") = a;
	register long x1 __asm__("x1") = b;
	register long x2 __asm__("x2") = c;
	register long x3 __asm__("x3") = d;
	register long x4 __asm__("x4") = e;
	register long x5 __asm__("x5") = f;
	__asm_syscall("r"(x8), "0"(x0), "r"(x1), "r"(x2), "r"(x3), "r"(x4), "r"(x5));
}

#define VDSO_USEFUL
#define VDSO_CGT_SYM "__kernel_clock_gettime"
#define VDSO_CGT_VER "LINUX_2.6.39"

#define IPC_64 0

#else

#define __SYSCALL_LL_E(x) \
((union { long long ll; long l[2]; }){ .ll = x }).l[0], \
((union { long long ll; long l[2]; }){ .ll = x }).l[1]
#define __SYSCALL_LL_O(x) 0, __SYSCALL_LL_E((x))

#ifdef __thumb__

/* Avoid use of r7 in asm constraints when producing thumb code,
 * since it's reserved as frame pointer and might not be supported. */
#define __ASM____R7__
#define __asm_syscall(...) do { \
	__asm__ __volatile__ ( "mov %1,r7 ; mov r7,%2 ; svc 0 ; mov r7,%1" \
	: "=r"(r0), "=&r"((int){0}) : __VA_ARGS__ : "memory"); \
	return r0; \
	} while (0)

#else

#define __ASM____R7__ __asm__("r7")
#define __asm_syscall(...) do { \
	__asm__ __volatile__ ( "svc 0" \
	: "=r"(r0) : __VA_ARGS__ : "memory"); \
	return r0; \
	} while (0)
#endif

/* For thumb2, we can allow 8-bit immediate syscall numbers, saving a
 * register in the above dance around r7. Does not work for thumb1 where
 * only movs, not mov, supports immediates, and we can't use movs because
 * it doesn't support high regs. */
#ifdef __thumb2__
#define R7_OPERAND "rI"(r7)
#else
#define R7_OPERAND "r"(r7)
#endif

__attribute__((always_inline))
static inline long __syscall0(long n)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0");
    __asm_syscall(R7_OPERAND);
}

__attribute__((always_inline))
static inline long __syscall1(long n, long a)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    __asm_syscall(R7_OPERAND, "0"(r0));
}

__attribute__((always_inline))
static inline long __syscall2(long n, long a, long b)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    __asm_syscall(R7_OPERAND, "0"(r0), "r"(r1));
}

__attribute__((always_inline))
static inline long __syscall3(long n, long a, long b, long c)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    __asm_syscall(R7_OPERAND, "0"(r0), "r"(r1), "r"(r2));
}

__attribute__((always_inline))
static inline long __syscall4(long n, long a, long b, long c, long d)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    register long r3 __asm__("r3") = d;
    __asm_syscall(R7_OPERAND, "0"(r0), "r"(r1), "r"(r2), "r"(r3));
}

__attribute__((always_inline))
static inline long __syscall5(long n, long a, long b, long c, long d, long e)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    register long r3 __asm__("r3") = d;
    register long r4 __asm__("r4") = e;
    __asm_syscall(R7_OPERAND, "0"(r0), "r"(r1), "r"(r2), "r"(r3), "r"(r4));
}

__attribute__((always_inline))
static inline long __syscall6(long n, long a, long b, long c, long d, long e, long f)
{
    register long r7 __ASM____R7__ = n;
    register long r0 __asm__("r0") = a;
    register long r1 __asm__("r1") = b;
    register long r2 __asm__("r2") = c;
    register long r3 __asm__("r3") = d;
    register long r4 __asm__("r4") = e;
    register long r5 __asm__("r5") = f;
    __asm_syscall(R7_OPERAND, "0"(r0), "r"(r1), "r"(r2), "r"(r3), "r"(r4), "r"(r5));
}

#define VDSO_USEFUL
#define VDSO_CGT32_SYM "__vdso_clock_gettime"
#define VDSO_CGT32_VER "LINUX_2.6"
#define VDSO_CGT_SYM "__vdso_clock_gettime64"
#define VDSO_CGT_VER "LINUX_2.6"

#define SYSCALL_FADVISE_6_ARG

#define SYSCALL_IPC_BROKEN_MODE

#endif