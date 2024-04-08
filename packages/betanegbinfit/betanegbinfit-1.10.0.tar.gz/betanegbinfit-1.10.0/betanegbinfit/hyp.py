# -*- coding: utf-8 -*-
"""
This module concerns mostly effective gradient-friendly computation of 3f2
function and CDF of negative beta binomial distirbution.
"""
import jax.numpy as jnp
from jax.scipy.special import betaln, gammaln
from jax.lax import cond, switch, while_loop
from jax import jit
from functools import partial



def __calc_one(a1, a2, b1, b2, n):
    return 1.0

def __calc_neg_one(a1, a2, b1, b2, n):
    return -1.0

def __calc_r0(a1, a2, b1, b2, n):
    return -((n + b1 - a2 - 1)*(n + b2 - a2 - 1)) / ((2 * n - 1)*(2 * n + a2 - 1))

def __calc_r1(a1, a2, b1, b2, n):
    return -((n + b1 - 1)*(n + b2 - 1)) / (2 * n * (2 * n + a1 - 1))

def __calc_r2(a1, a2, b1, b2, n):
    return -((n + b1 - a1)*(n + b2 - a1)) / ((2 * n + a1)*(2 * n + a2))

def _calc_r(a1, a2, b1, b2, n):
    i = n % 3 + 3 * (n < 2)
    return switch(i, [__calc_r0, __calc_r1, __calc_r2, __calc_one, __calc_neg_one], a1, a2, b1, b2, n // 3)

def __calc_q0(a1, a2, b1, b2, n):
    return ((3 * n + b1 - 1)*(3 * n + b2 - 1) - 2 * n * (2 * n + a2)) / (2 * n * (2 * n + a1 - 1))

def __calc_q1(a1, a2, b1, b2, n):
    return ((3 * n + b1) * (3 * n + b2) - (2 * n + 1) * (2 * n + a1)) / ((2 * n + a1) * (2 * n + a2))

def __calc_q2(a1, a2, b1, b2, n):
    return ((3 * n + b1 + 1) * (3 * n + b2 + 1) - (2 * n + a1 + 1) * (2 * n + a2 + 1)) / ((2 * n + 1) * (2 * n + a2 + 1))

def _calc_q(a1, a2, b1, b2, n):
    i = n % 3 + 3 * (n == 0)
    return switch(i, [__calc_q0, __calc_q1, __calc_q2, __calc_one], a1, a2, b1, b2, n // 3)


def hyp3f2(a1, a2, b1, b2, n=20, eps=1e-1, tiny=1e-100):
    def lentz_iteration(prev):
        res, params, c, d, i = prev
        rn = _calc_r(*params, i)
        qn = _calc_q(*params, i)
        c = qn + rn / c
        t = qn + rn * d
        c = jnp.where(c == 0, tiny, c)
        t = jnp.where(t == 0, tiny, t)
        d = 1.0 / t
        res *= c * d
        return res, params, c, d, i + 1
    
    def lentz_cond(prev):
        t = prev[-2] * prev[-3]
        return ((jnp.abs(t - 1) > eps))  & (prev[-1] <= n)

    params = (a1, a2, b1, b2)
    res = tiny
    c = res
    d = 0.0
    carry = while_loop(lentz_cond, lentz_iteration, (res, params, c, d, 0))
    return carry[0] - tiny

@jnp.vectorize
def compute_c(x, r, p, k):
    return betaln(r + k * p, k * (1 - p) + x + 1) -(betaln( r, x + 1) + betaln(k * p, k * (1 - p)) + jnp.log(x + 1))

@jnp.vectorize
def _cdf(x, r, p, k, eps=1e-6):
    p = 1 - p
    c = jnp.exp(compute_c(x, r, p, k))
    t = hyp3f2(r + x + 1, -p * k + k + x + 1, r + k + x + 1, x + 2, eps=eps)
    return 1 - t * c

@jnp.vectorize
def _cdfc(x, r, p, k, eps=1e-6):
    x, r = r, x
    x -= 1
    r += 1
    c = jnp.exp(compute_c(x, r, p, k))
    t = hyp3f2(r + x + 1, -p * k + k + x + 1, r + k + x + 1, x + 2, eps=eps)
    return t * c

def calc_cond(x, p, r):
    # p = 1 - p
    return (1-p) / p * x

@partial(jit, static_argnames=['eps'])
@jnp.vectorize
def cdf(x, r, p, k, eps=1e-6):
    c = r < (1-p) / p * x 
    # a_fun = partial(_cdf, eps=eps)
    # b_fun = partial(_cdfc, eps=eps)
    a_fun = _cdf
    b_fun = _cdfc
    return cond(c, a_fun, b_fun, x, r, p, k)
