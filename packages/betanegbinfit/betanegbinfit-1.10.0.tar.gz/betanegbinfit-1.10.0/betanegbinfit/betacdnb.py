# -*- coding: utf-8 -*-
import jax.numpy as jnp
from jax.lax import while_loop, fori_loop, cond, select, lgamma
from jax import jit, custom_jvp
from jax.scipy.special import logsumexp
from functools import partial
from gmpy2 import mpfr, get_context
from mpmath import mp
import gmpy2


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
    return x * jnp.log(2), power

@logfrexp.defjvp
def logfrexp_jvp(primals, tangents):
  primals = logfrexp(primals[0])
  return primals, (tangents[0], 0.0)

def solve_symm(matrix_rows: jnp.ndarray, b: jnp.ndarray,
               parallel: jnp.ndarray, b_par: jnp.ndarray, upper: jnp.ndarray) -> jnp.ndarray:
    n, m = matrix_rows.shape
    k = parallel.shape[1]
    aux = jnp.zeros((n + m, 2 * m + k), dtype=float)
    inds = jnp.arange(n).reshape(-1, 1) - jnp.arange(1, m).reshape(1, -1)
    aux = aux.at[:n, :m - 1].set(jnp.take_along_axis(matrix_rows.at[:, 1:].get(), inds, axis=0).at[:, ::-1].get())
    aux = aux.at[:n, m - 1: 2 * m - 1].set(matrix_rows)
    aux = aux.at[:n, -1].set(b)
    aux = aux.at[:n, -k - 1:-1].set(parallel)
    row_memory = jnp.append(parallel, jnp.zeros((aux.shape[0] - parallel.shape[0], k)), axis=0)
    row_memory = row_memory.at[-1, :].set(b_par)
    row_inds_f = jnp.arange(1, m)
    row_inds = row_inds_f.reshape(-1, 1)
    mult_col_inds = jnp.arange(0, m - 1).at[::-1].get()
    base_col_inds = jnp.arange(m, 2 * m - 1)
    col_inds = (base_col_inds.reshape(-1, 1).at[::-1].get() - jnp.arange(1, m + 1).reshape(1, -1)).at[:,::-1].get()
    t = jnp.ones((col_inds.shape[0], k + 1), dtype=int) * jnp.arange(2 * m - 1, 2 * m + k).reshape(1, -1)
    col_inds = jnp.append(col_inds, t, axis=1)
    memrow_ind = jnp.arange(0, m)
    memrow_ind_app = jnp.arange(row_memory.shape[0] - k - 1, row_memory.shape[0])

    def body_forward(i, carry):
        aux, row_memory = carry
        cur_rows = i + row_inds_f
        mults = -aux.at[cur_rows, mult_col_inds].get()
        mults = mults.reshape(-1, 1)
        row = aux.at[i, m-1:].get()
        a0 = row.at[0].get()
        a0 = jnp.select([a0 == 0, a0 != 0], [1.0, a0])
        row_normed = row / a0
        cur_rows = i + row_inds
        aux = aux.at[cur_rows, col_inds].add(mults * row_normed)
        mults = -row_memory.at[i].get().reshape(-1, 1)
        ind = jnp.append(memrow_ind + i, memrow_ind_app)
        row_memory = row_memory.at[ind].add((mults * row_normed).T)
        return aux, row_memory
    
    aux, row_memory = fori_loop(0, upper, body_forward, (aux, row_memory))
    lagrange_multipliers = jnp.linalg.solve(row_memory.at[-k - 1:-1, :].get(), row_memory.at[-1, :].get())
    def body_backward(i, aux):
        i = -i
        row = aux.at[i, m - 1:].get()
        inds = i + row_inds_f 
        f = row.at[-1].get() - (aux.at[inds, -1].get() * row.at[1:m].get()).sum()
        f -= (row.at[m:-1].get() * lagrange_multipliers).sum()
        a0 = row.at[0].get()
        a0 = jnp.select([a0 == 0, a0 != 0], [10., a0])
        f /= a0
        aux = aux.at[i, -1].set(f)
        return aux

    aux = fori_loop(-upper + 1, 1, body_backward, aux)
    return aux.at[:n, -1].get()

def _calc_frac(a, b, c, z, i):
    return ((a + i) / (i + 1)) * ((b + i) / (c + i)) * z

def _calc_frac_frac(a, b, c, z, i):
    num = (a + i) * (b + i) * z
    denom = (i + 1) * (c + i)
    return num, denom

def hyp2f1(a, b, c, z, eps=1e-14):
    def body(carry):
        last_pos_res, last_pos_exp, res, prev_res, term, exp, i = carry
        term *= _calc_frac(a, b, c, z, i)
        prev_res = res
        res, p = frexp(res + term)
        term /= 2 ** p
        exp += p
        last_pos_res, last_pos_exp = cond(res > 0, lambda: (res, exp), lambda: (last_pos_res, last_pos_exp))
        return last_pos_res, last_pos_exp, res, prev_res, term, exp, i + 1
    def iter_cond(carry):
        _, _, res, prev_res, _, _, i = carry
        return (jnp.abs((res - prev_res) / res) > eps) & (i < n_max)
    n_max = -jnp.floor(b) + 1
    t = while_loop(iter_cond, body, (1., 0., 1., 0., 1.0, 0., 0))
    res, exp = t[:2]
    return jnp.log(res) + exp * jnp.log(2) 

def hyp2f1_long(a, b, c, z):
    from mpmath import hyp2f1
    # return gmpy2.log(mpfr(str(hyp2f1(a, b, c, z))))
    n_max = -gmpy2.floor(b) + 1
    num = mpfr(1)
    denom = mpfr(1)
    # term = mpfr(1)
    res = mpfr(1)
    for i in range(int(n_max)):
        n, d = _calc_frac_frac(a, b, c, z, i)
        num *= n
        denom *= d
        term = num / denom
        res += term
    t = gmpy2.log(mpfr(str(hyp2f1(a, b, c, z))))
    # print('kek',float(t - gmpy2.log(res)))
    return gmpy2.log(res)    
    
# def test_hyp(x, r, p, k):
#     # hyp_1 = hyp2f1(1. + k * p, 1. - r, 2. + k * (-1. + p) - r, 1. - p)
#     from mpmath import hyp2f1 as tt
#     hyp_0 = gmpy2.log(mpfr(str(tt(1. + k * p, 1. - r, 2. + k * (-1. + p) - r, 1. - p))))
#     x = gmpy2.mpfr(x)
#     r = gmpy2.mpfr(r)
#     p = gmpy2.mpfr(p)
#     k = gmpy2.mpfr(k)
#     hyp_2 = hyp2f1_long(1. + k * p, 1. - r, 2. + k * (-1. + p) - r, 1. - p)
#     return float(abs((hyp_0 - hyp_2)/hyp_0)), float(hyp_2), float(hyp_0)
#     return hyp_1, hyp_2

def _calc_b1(a, b1, b2):
    return (4.0 - 3.0 * a + b1 + b2)/(a - 1.0)

def _calc_b2(a, b1, b2):
    return (3. * a - 2. * b1 - 2.0 * b2 - 5.0) / (a - 1.) + b1 * b2/((a - 1.) * (a - 2.))

def _calc_b3(a, b1, b2):
    return -((a - b1 - 2.) / (a - 1.)) * ((a - b2 - 2.) / (a - 2.))

def _calc_c1(a, a2, a3):
    return (2. * a - a2 - a3 - 3.)/(a - 1.)

def _calc_c2(a, a2, a3):
    return (2. - a + a2 + a3) / (a - 1.) - a2 * a3/((a - 1.) * (a - 2.))

def _calc_backward(i, a2, a3, b1, b2, z, f1, f2, f3, log=False):
    B1 = _calc_b1(i, b1, b2)
    B2 = _calc_b2(i, b1, b2)
    B3 = _calc_b3(i, b1, b2)
    C1 = _calc_c1(i, a2, a3)
    C2 = _calc_c2(i, a2, a3)
    alpha_1 = (B1 + C1 * z)
    alpha_2 =  (B2 + C2 * z)
    alpha_3 = B3
    if log:
        b = jnp.array([alpha_1, alpha_2, alpha_3]) / (z - 1.)
        return logsumexp(jnp.array([f1, f2, f3]), b=b, )
    return (alpha_1 * f1 + alpha_2 * f2  + alpha_3 * f3) / (z - 1.)

def calc_coeffs(i, a2, a3, b1, b2, z, p):
    i += 1
    B1 = _calc_b1(i, b1, b2)
    B2 = _calc_b2(i, b1, b2)
    B3 = _calc_b3(i, b1, b2)
    C1 = _calc_c1(i, a2, a3)
    C2 = _calc_c2(i, a2, a3)
    alpha = (B1 + C1 * z) * p / (z - 1)
    beta =  (B2 + C2 * z) * p ** 2 / (z - 1)
    gamma = B3 * p ** 3 / (z - 1)
    return alpha, beta, gamma


def calc_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
              beta_1, beta_2, beta_3, beta_4,
              gamma_1, gamma_2, gamma_3, gamma_4):
    a = alpha_2 ** 2 + beta_3 ** 2 + gamma_4 ** 2 + 1
    e = -alpha_2 + alpha_3 * beta_3 + beta_4 * gamma_4
    f = alpha_4 * gamma_4 - beta_3
    g = -gamma_4
    return a, e, f, g

def calc_first_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
                 beta_1, beta_2, beta_3, beta_4,
                 gamma_1, gamma_2, gamma_3, gamma_4):
    a = beta_3 ** 2 + gamma_4 ** 2 + 1
    e = alpha_3 * beta_3 + beta_4 * gamma_4
    f = alpha_4 * gamma_4 - beta_3
    g = -gamma_4
    return a, e, f, g

def calc_last_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
                    beta_1, beta_2, beta_3, beta_4,
                    gamma_1, gamma_2, gamma_3, gamma_4, c):
    alphas = jnp.array([alpha_1, alpha_2, alpha_3, alpha_4])
    betas = jnp.array([beta_1, beta_2, beta_3, beta_4])
    gammas = jnp.array([gamma_1, gamma_2, gamma_3, gamma_4])
    alphas = alphas.at[:4-c].set(alphas.at[c:].get()); alphas = alphas.at[4-c:].set(0.)
    betas = betas.at[:4-c].set(betas.at[c:].get()); betas = betas.at[4-c:].set(0.)
    gammas = gammas.at[:4-c].set(gammas.at[c:].get()); gammas = gammas.at[4-c:].set(0.)
    
    aefg = calc_aefg(*alphas, *betas, *gammas)
    return aefg

# @partial(jit, static_argnums=(4,))
# @partial(jnp.vectorize, signature='(),(),(),()->(n)', excluded=(4,))
def logprob_recurrent(r, p, k, upper, max_sz):
    ahead_comp = 100
    # upper = upper.astype(int)
    x = upper + ahead_comp
    z = 1. - p
    a2 = k * p + 1.
    a3 = 1. - r
    b1 = 2.
    b2 = 2. - k * (1. - p)  - r
    aux = jnp.zeros((max_sz + ahead_comp, 4), dtype=float)
    b_col = jnp.zeros(aux.shape[0] + 1, dtype=float)
    
    nonhyp_term = jnp.log1p(-p) + jnp.log(p) + jnp.log(r) + lgamma(1 + k) + lgamma(r + k * (1 - p) - 1.)
    t, _ = logsumexp(jnp.array([lgamma(k) + lgamma(k * (1. - p) + r),
                                  lgamma(k * (1. - p)) + lgamma(k + r)]),
                      b=jnp.array([1., -1.]), return_sign=True)
    nonhyp_term -= t
    hyp_1 = hyp2f1(1. + k * p, 1. - r, 2. + k * (-1. + p) - r, 1. - p)
    hyp_0 = hyp2f1(k * p, -r, 1. + k * (-1. + p) - r, 1. - p)
    t = -jnp.expm1(hyp_0)
    b_term = jnp.log(jnp.abs(t))
    hyp_0 = select(jnp.isfinite(b_term), b_term, hyp_0)
    hyp_0 += jnp.log(jnp.abs(1. - r - k * (1. - p))) - jnp.log(k) - jnp.log1p(-p) - jnp.log(p) - jnp.log(r)
    hyp_2 = _calc_backward(3., a2, a3, b1, b2, z, hyp_1, hyp_0, 0.0, log=True)
    
    f2 = hyp_2 + nonhyp_term + jnp.log(p) * 2.
    f2 = jnp.exp(f2)
    f1 = hyp_1 + nonhyp_term + jnp.log(p)
    f1 = jnp.exp(f1) 
    f0 = hyp_0 + nonhyp_term
    f0 = jnp.exp(f0)
    i = 1
    (alpha_1, alpha_2, alpha_3, alpha_4), (beta_1, beta_2, beta_3, beta_4),\
    (gamma_1, gamma_2, gamma_3, gamma_4) = calc_coeffs(jnp.arange(i, i + 4), a2, a3, b1, b2, z, p)
    aefg = calc_first_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
                           beta_1, beta_2, beta_3, beta_4,
                           gamma_1, gamma_2, gamma_3, gamma_4)
    aefg_1 = aefg
    aefg_2 = (0.0, 0.0, 0.0, 0.0)
    aefg_3 = (0.0, 0.0, 0.0, 0.0)
    b_col = b_col.at[:3].set([f0, f1, f2])
    aux = aux.at[0].set(aefg)
    def main_body(i, carry):
        aux, aefgs, (alphas, betas, gammas) = carry
        aefg_1, aefg_2, aefg_3 = aefgs
        alpha_1, alpha_2, alpha_3, alpha_4 = alphas
        beta_1, beta_2, beta_3, beta_4 = betas
        gamma_1, gamma_2, gamma_3, gamma_4 = gammas
        alpha_1, beta_1, gamma_1 = calc_coeffs(i + 3, a2, a3, b1, b2, z, p)
        alpha_1, alpha_2, alpha_3, alpha_4 = alpha_2, alpha_3, alpha_4, alpha_1
        beta_1, beta_2, beta_3, beta_4 = beta_2, beta_3, beta_4, beta_1
        gamma_1, gamma_2, gamma_3, gamma_4 = gamma_2, gamma_3, gamma_4, gamma_1
        aefg = calc_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
                         beta_1, beta_2, beta_3, beta_4,
                         gamma_1, gamma_2, gamma_3, gamma_4)
        aux = aux.at[i - 1].set(aefg)

        aefg_1, aefg_2, aefg_3 = aefg, aefg_1, aefg_2
        aefgs = (aefg_1, aefg_2, aefg_3)
        alphas = (alpha_1, alpha_2, alpha_3, alpha_4)
        betas = (beta_1, beta_2, beta_3, beta_4)
        gammas = (gamma_1, gamma_2, gamma_3, gamma_4)
        return aux, aefgs, (alphas, betas, gammas)
    
    aefgs = (aefg_1, aefg_2, aefg_3)
    alphas = (alpha_1, alpha_2, alpha_3, alpha_4)
    betas = (beta_1, beta_2, beta_3, beta_4)
    gammas = (gamma_1, gamma_2, gamma_3, gamma_4)
    aux, aefgs, (alphas, betas, gammas) = fori_loop(2, x - 3, main_body, (aux, aefgs, (alphas, betas, gammas)))
    aefg_1, aefg_2, aefg_3 = aefgs
    alpha_1, alpha_2, alpha_3, alpha_4 = alphas
    beta_1, beta_2, beta_3, beta_4 = betas
    gamma_1, gamma_2, gamma_3, gamma_4 = gammas

    i = x - 3
    alpha_1, beta_1, gamma_1 = calc_coeffs(i + 3, a2, a3, b1, b2, z, p)
    
    a = x - 3
    for c in range(1, 4):
        i = a + c - 1

        aefg = calc_last_aefg(alpha_1, alpha_2, alpha_3, alpha_4,
                              beta_1, beta_2, beta_3, beta_4,
                              gamma_1, gamma_2, gamma_3, gamma_4, c)
        aux = aux.at[i - 1].set(aefg)
        aefg_1, aefg_2, aefg_3 = aefg, aefg_1, aefg_2
    t1 = jnp.zeros((1, aux.shape[1]))
    t1 = t1.at[0, 0].set(1.0)
    aux = jnp.vstack((t1, aux))
    t1 = jnp.zeros((aux.shape[0], 1))
    t1 = t1.at[x - 1].set(1.0)
    conditions = jnp.hstack([t1, jnp.ones_like(t1)])
    b_cond = jnp.array([0.0, 1.0])
    res = solve_symm(aux, b_col, conditions, b_cond, x).at[:max_sz].get()
    inds = jnp.arange(0, max_sz)
    res = jnp.abs(res)
    res = jnp.log(res) - jnp.log(res.sum())
    return jnp.where(inds < upper, res, -float('inf'))


@partial(jit, static_argnums=(4,))
def logprob_recurrent_meta(r, p, k, upper, max_sz):
    n = len(upper)
    def iter_body(carry):
        res, i = carry
        r_i = r.at[i].get()
        k_i = k.at[i].get()
        lp = logprob_recurrent(r_i, p, k_i, upper.at[i].get(), max_sz)
        res = res.at[i, :].set(lp)
        return res, i + 1
    def iter_cond(carry):
        i = carry[1]
        return (i < n) & (upper.at[i].get() > 0) 
    res = jnp.full((n, max_sz), -float('inf'), dtype=float)
    return while_loop(iter_cond, iter_body, (res, 0))[0]

def long_cdf(x, r, p, k):
    precision = get_context().precision
    new_precision = precision * 4
    get_context().precision = new_precision
    mp.prec = new_precision
    z = mpfr(1 - p)
    a2 = mpfr(k * p + 1)
    a3 = mpfr(1 - r)
    b1 = mpfr(2)
    b2 = mpfr(2 - k * (1 - p)  - r)
    
    log = gmpy2.log
    log1p = gmpy2.log1p
    lgamma = lambda x: gmpy2.lgamma(x)[0]
    nonhyp_term = log1p(-p) + log(p) + log(r) + lgamma(1 + k) + lgamma(r + k * (1 - p) - 1)
    t1, t2 = lgamma(k) + lgamma(k * (1 - p) + r), lgamma(k * (1 - p)) + lgamma(k + r)
    t = log(abs(gmpy2.exp(t1) - gmpy2.exp(t2)))
    nonhyp_term -= t
    hyp_1 = hyp2f1_long(1 + k * p, 1 - r, 2 + k * (-1 + p) - r, 1 - p)
    hyp_0 = hyp2f1_long(k * p, -r, 1 + k * (-1 + p) - r, 1 - p)
    t = -gmpy2.expm1(hyp_0)
    hyp_0 = log(abs(t))
    hyp_0 += log(abs(1. - r - k * (1. - p))) - log(k) - log1p(-p) - log(p) - log(r)
    hyp_2 = log(_calc_backward(3, a2, a3, b1, b2, z, gmpy2.exp(hyp_1), gmpy2.exp(hyp_0), 1.0))
    f2 = hyp_2 + nonhyp_term + log(p) * 2
    f2 = gmpy2.exp(f2)
    f1 = hyp_1 + nonhyp_term + log(p)
    f1 = gmpy2.exp(f1) 
    f0 = hyp_0 + nonhyp_term
    f0 = gmpy2.exp(f0)
    res = mpfr(0)
    res += f0 * (x > 1) + f1 * (x > 2) + f2 * (x > 3)
    for i in range(3, x):
        i = gmpy2.mpfr(i)
        f2, f1, f0 = _calc_backward(i + 1, a2, a3, b1, b2, z, f2 * p, f1 * p ** 2, f0 * p ** 3), f2, f1
        if f2 > 0 and (res + f2) < 1:
            res += f2
        else:
            break
    get_context().precision = precision
    mp.prec = precision
    return res
# # print(*jnp.exp(logprob_recurrent(10., 0.5, 10., 200, 200))[40:50])
# t = 1-long_cdf(1000, 100, 0.5, 10000)
# print(float(-gmpy2.log10(t)), float(t))
