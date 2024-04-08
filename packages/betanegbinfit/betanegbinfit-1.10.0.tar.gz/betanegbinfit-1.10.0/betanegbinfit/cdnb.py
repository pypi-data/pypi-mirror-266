#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 20:18:33 2023

@author: georgy
"""
import jax.numpy as jnp
from jax.lax import while_loop, fori_loop, cond, select
from jax import jit, custom_jvp
from gmpy2 import mpfr, log
from collections.abc import Iterable
from functools import partial
# from .utils import frexp

@custom_jvp
def frexp(x):
    x, power = jnp.frexp(x)
    power = power.astype(float)
    return x, power

@frexp.defjvp
def frexp_jvp(primals, tangents):
  primals = frexp(primals[0])
  return primals, (tangents[0] * 2. ** -primals[1], 0.0)

@custom_jvp
def logfrexp(x):
    x /= jnp.log(2)
    power = jnp.round(x)
    x = x - power
    return x, power

@logfrexp.defjvp
def logfrexp_jvp(primals, tangents):
  primals = logfrexp(primals[0])
  return primals, (tangents[0], 0.0)



def _calc_frac(a, b, c, z, i):
    return ((a + i) / (i + 1)) * ((b + i) / (c + i)) * z


@jit
@jnp.vectorize
def logprob(x, n, p):
    z = -(1 - p) ** 2.0 / p 
    zp = z / (z - 1)
    params, pfaff = cond(jnp.abs(z) > 1, 
                lambda: ((1.0 - n, 1.0 - x, 2.0, zp),
                         jnp.log1p(-z) * (n - 1 + 0 * x)),
                lambda: ((1.0 + n, 1.0 - x, 2.0, z),
                         jnp.log1p(-z) * (n - x)))

    def sum_iter(carry):
        last_pos, res, prev_res, mult, term, i = carry
        frac = _calc_frac(*params, i - 1)
        term *= frac 
        prev_res = res
        res, exp = frexp(res + term)
        term /= 2.0 ** exp
        mult += exp
        last_pos = cond(res >= 0, lambda: res, lambda: last_pos)
        return last_pos, res, prev_res, mult, term, i + 1
    
    def cond_iter(carry):
        res, prev_res = carry[1:3]
        i = carry[-1]
        return (prev_res != res) & (i <= x)
    term = 1.0
    res = 1.0
    mult = jnp.log(n) + jnp.log1p(-p) * 2 + jnp.log(p) * (n + x - 1) - jnp.log1p(-p ** n)
    carry = while_loop(cond_iter, sum_iter, (res, res, 0, 0, term, 1))
    res = jnp.log(carry[0]) + mult + carry[3] * jnp.log(2) + pfaff
    p_term = jnp.log((-1 + 1 / p + p) ** n - 1)
    p_term = select(jnp.isfinite(p_term), p_term, n * jnp.log(-1 + 1 / p + p))
    first = jnp.log(p) * n + p_term - jnp.log1p(-p ** n)
    return select(x == 0, first, res)


@partial(jit, donate_argnums=(3,))
@partial(jnp.vectorize, signature='(),(),()->(n)', excluded=(3,))
def logprob_recurrent(r, p, upper, max_sz):
    res = max_sz#jnp.full(max_sz, -float('inf'), dtype=float)
    p_term = jnp.log((-1 + 1 / p + p) ** r - 1) # This expression blows up for sufficiently large r
    p_term = select(jnp.isfinite(p_term), p_term, r * jnp.log(-1 + 1 / p + p))
    f2 = (jnp.log(p) * r + p_term - jnp.log1p(-p ** r)) / jnp.log(2)
    res = res.at[0].set(f2 * jnp.log(2))
    mult = jnp.round(f2) + 1
    f2 -= mult
    t = jnp.log1p(-p) * 2 - jnp.log(p) * r + jnp.log1p(-p ** r) + jnp.log(r) + jnp.log(p) * r + jnp.log(p + 1 / p  - 1) * (r - 1) - p_term - jnp.log1p(-p ** r)
    f1 = f2 + t / jnp.log(2)
    res = res.at[(upper > 1).astype(int)].set((f1 + mult) * jnp.log(2) * (upper > 1) + res.at[0].get() * (upper < 1))
    f1_pow = jnp.round(f1) + 1
    f1 -= f1_pow
    mult += f1_pow
    f2 = jnp.power(2, f2)
    f1 = jnp.power(2, f1)
    def sum_iter(x, carry):
        res, f1, f2, mult = carry
        alpha = -1 + r - 2 * p * r + x + p ** 2 * (-1 + r + x)
        beta = -p * (-2 + x)
        alpha *= p 
        beta *= p ** 2
        f, exp = frexp((alpha * f1 + beta * f2) / (x - (1 - p) * p * x))
        f2 = f1 * 2 ** -exp
        f1 = f
        mult += exp
        res = res.at[x].set(jnp.log(f) + mult * jnp.log(2))
        return (res, f1, f2, mult)
    return fori_loop(2, upper.astype(int), sum_iter, (res, f1, f2, mult))[0]

@partial(jit, static_argnums=(3,))
def logprob_recurrent_meta(r, p, upper, max_sz):
    r = jnp.array(r)
    upper = jnp.array(upper)
    subres = jnp.full(max_sz, -float('inf'), dtype=float)
    n = len(upper)
    def iter_body(carry):
        res, i = carry
        res = res.at[i, :].set(logprob_recurrent(r.at[i].get(), p, upper.at[i].get(), subres))
        return res, i + 1
    def iter_cond(carry):
        i = carry[1]
        return (i < n) & (upper.at[i].get() > 0) 
    res = jnp.full((n, max_sz), -float('inf'), dtype=float)
    return while_loop(iter_cond, iter_body, (res, 0))[0]



@jit
@jnp.vectorize
def cdf(x, r, p):
    f1 = (1 - p) ** 2 * p ** r * (-1 + 1 / p + p) ** (-1 + r) * r / (1 - p ** r)
    f2 = p ** r * (-1 + (-1 + 1 / p + p) ** r) / (1 - p ** r)
    res = (x == 0) * f2 + (x > 0) * (f1 + f2)

    def sum_iter(x, carry):
        res, f1, f2 = carry
        alpha = -1 + r - 2 * p * r + x + p ** 2 * (-1 + r + x)
        beta = -p * (-2 + x)
        alpha *= p 
        beta *= p ** 2
        f = (alpha * f1 + beta * f2) / (x - (1 - p) * p * x)
        res += f
        f2 = f1
        f1 = f
        return (res, f1, f2)
    return fori_loop(2, x.astype(int) + 1, sum_iter, (res, f1, f2))[0]


def long_prob(x, r, p):
    r = mpfr(r)
    p = mpfr(p)
    if not isinstance(x, Iterable):
        x = [x]
    f1 = (1 - p) ** 2 * p ** r * (-1 + 1 / p + p) ** (-1 + r) * r / (1 - p ** r)
    f2 = p ** r * (-1 + (-1 + 1 / p + p) ** r) / (1 - p ** r)
    max_x = max(x)
    res = dict()
    res[0] = float(log(f2)) 
    res[1] = float(log(f1))
    for xt in range(2, max_x + 1):   
        alpha = -1 + r - 2 * p * r + xt + p ** 2 * (-1 + r + xt)
        beta = -p * (-2 + xt)
        alpha *= p 
        beta *= p ** 2
        f = (alpha * f1 + beta * f2) / (xt - (1 - p) * p * xt)
        res[xt] = float(log(f))
        f2 = f1
        f1 = f
    return list(map(res.get, x))


def long_cdf(x, r, p, skip=-1, return_dict=False):
    r = mpfr(r)
    p = mpfr(p)
    if not isinstance(x, Iterable):
        x = [x]
    f1 = (1 - p) ** 2 * p ** r * (-1 + 1 / p + p) ** (-1 + r) * r / (1 - p ** r)
    f2 = p ** r * (-1 + (-1 + 1 / p + p) ** r) / (1 - p ** r)
    max_x = max(x)
    res = dict()
    res[0] = f2 if skip < 0 else 0
    res[1] = f1 + f2 if skip < 1 else 0
    for xt in range(2, max_x + 1):   
        alpha = -1 + r - 2 * p * r + xt + p ** 2 * (-1 + r + xt)
        beta = -p * (-2 + xt)
        alpha *= p 
        beta *= p ** 2
        f = (alpha * f1 + beta * f2) / (xt - (1 - p) * p * xt)
        if xt > skip:
            res[xt] = res[xt - 1] + f
        else:
            res[xt] = 0
        f2 = f1
        f1 = f
    if return_dict:
        return res
    return list(map(res.get, x))
