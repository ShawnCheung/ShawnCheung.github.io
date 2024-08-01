---
layout: post
title: Simple Justification Techniques
date: 2024-07-28 14:26 +0800
categories: [数学, 简单证明技巧]
tags: [数学]
---

## 简单的证明技巧
sometimes, we will want to make claims about something. In order to rigorously make such claims, we must use mathematical language and in order to back up such claims, we must justify or prove our statements.

### 1. 反证法
The two primary such methods are the use of the contrapositive and the contradiction.
The use of the contrapositive method is like looking through a negative mirror.
To justify the statement “if p is true, then q is true,” we establish that “if q is not true, then p is not true” instead.
Logically, these two statements are the same, but the latter, which is called the contrapositive of the first, may be easier to think about.

**Example:**  Let a and b be integers. If ab is even, then a is even or b is even.
**Justification:** To justify this claim, consider the contrapositive, “If a is odd and b is odd, then ab is odd.” So, suppose a = 2j+1 and b = 2k+1, for some integers j and k. Then ab = 4jk+2j+2k+1 = 2(2jk+j+k)+1; hence, ab is odd.

Another negative justification technique is justification by contradiction, which also often involves using DeMorgan’s Law.
In applying the justification by contradiction technique, we establish that a statement q is true by first supposing that q is false and then showing that this assumption leads to a contradiction (such as 2 = 2 or 1 > 3).
By reaching such a contradiction, we show that no consistent situation exists with q being false, so q must be true. Of course, in order to reach this conclusion, we must be sure our situation is consistent before we assume q is false.

**Example**: Let a and b be integers. If ab is odd, then a is odd and b is odd.
**Justification**: Let ab be odd. We wish to show that a is odd and b is odd. So,
with the hope of leading to a contradiction, let us assume the opposite, namely,
suppose a is even or b is even. In fact, without loss of generality, we can assume
that a is even (since the case for b is symmetric). Then a = 2 j for some integer
j. Hence, ab = (2 j)b = 2(jb), that is, ab is even. But this is a contradiction: ab
cannot simultaneously be odd and even. Therefore, a is odd and b is odd.

### 2. 数学归纳法
Most of the claims we make about a running time or a space bound involve an integer parameter n(usually denoting an intuitive notion of the "size" of the problem). Moreover, most of these claims are equivalent to saying some statement q(n) is true "for all n>=1". Since this is making a claim about an infinite set of numbers, we cannot justify this exhaustively in a direct fashion.

* Induction

This technique amounts to showing that, for any particular n>=1, there is a finite sequence of implications that starts with something known to be true and ultimately leads to showing that q(n) is true. Specifically, we begin a justification by induciont by showing that q(n) is true for n=1(and possibly some other values n=2,3,...,k for some constant k). Then we justify that the inductive "step" is true for n > k, namely, we show "if q(j) is true for all j < n, then q(n) is true." The combination of these two pieces completes the justification by induction.

**Proposition**: Consider the Fibonacci function F(n), which is defined such that F(1)=1, F(2)=2, and F(n)=F(n-1)+F(n-2) for n>=3. Then F(n) < 2^n for all n>=1.

**Justification**: We will show our claim is correct by induction

**Base case**: (n<=2). F(1) = 1 < 2^1 =2 and F(2) = 2 < 2^2 = 4. So, our claim is true for n<=2.

**Induction step**: (n>2). Suppose our claim is true for all n'<n. Consider n>2, F(n)=F(n-2)+F(n-1). Moreover, since both n-2 and n-1 are less than n, we can apply the inductive assumption (sometimes called the "inductive hypothesis") to imply that F(n) < 2^(n-2) +2^(n-1) since,

2^(n-2) + 2^(n-1) < 2^(n-1) + 2^(n-1) = 2 * 2^(n-1) = 2^n.

So, our claim is true for all n>=1.


Let us do another inductive argument, this time for a fact we have seen before.

**Proposition**: 

$$\Sigma_{i=1}^n i=\frac{n(n+1)}{2}$$


**Justification**: We will show our claim is correct by induction

**Base case**: (n=1). $\Sigma_{i=1}^1 i=1=\frac{1(1+1)}{2}$

**Induction step**: (n>1). Suppose our claim is true for all n'<n. Consider n>1, $\Sigma_{i=1}^n i=\Sigma_{i=1}^{n-1} i + n=\frac{(n-1)n}{2}+n=\frac{n(n+1)}{2}$

So, our claim is true for all n>=1.

* Loop Invariants

To prove some statement L about a loop is correct, define L in terms of a series of smaller statements L0,L1,...,Lk, where:

    1. The initial claim, L0, is true before the loop begins.
    2. If Lj−1 is true before iteration j, then Lj will be true after iteration j.
    3. The final statement, Lk, implies the desired statement L to be true.

Let us give a simple example of using a loop-invariant argument to justify the correctness of an algorithm. In particular, we use a loop invariant to justify that the function, finds the smallest index at which element val occurs in sequence S.

```python
def find(S, val):
"""Return index j such that S[j] == val, or -1 if no such element."""
n = len(S)
j=0
while j < n:
    if S[j] == val:
        return j # a match was found at index j
    j += 1
return −1
```

To show that find is correct, we inductively define a series of statements, Lj, that lead to the correctness of our algorithm. Specifically, we claim the following is true at the beginning of iteration j of the while loop:

Lj: val is not equal to any of the first j elements of S.

This claim is true at the beginning of the first iteration of the loop, because j is 0 and there are no elements among the first 0 in S (this kind of a trivially true claim is said to hold vacuously(空虚的真)). In iteration j, we compare element val to element S[j] and return the index j if these two elements are equivalent, which is clearly correct and completes the algorithm in this case. If the two elements val and S[ j] are not
equal, then we have found one more element not equal to val and we increment the index j. Thus, the claim Lj will be true for this new value of j; hence, it is true at the beginning of the next iteration. If the while loop terminates without ever returning an index in S, then we have j = n。 That is, Ln is true—there are no elements of S equal to val. Therefore, the algorithm correctly returns −1 to indicate that val is not in S.

### 3. 直接证明法
### 4. 构造法

### 5. 反例法
Some claims are of the generic form, "there is an element x in a set S that has property P." To justify such a claim, we only need to produce a particular x in S that has property P. 
Likewise, some hard-to-believe claims are of the generic form, "Every element x in a set S has property P." To justify such a claim is false, we only need to produce a particular x in S that does not have property P.


### 6. 分类讨论法

### 7. 引理法

### 8. 递推法

### 9. 递归法

### 10. 极限法

### 11. 拟似证明法

### 12. 证明技巧总结