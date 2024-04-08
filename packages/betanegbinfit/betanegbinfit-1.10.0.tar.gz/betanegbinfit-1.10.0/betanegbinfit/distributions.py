# -*- coding: utf-8 -*-
"""Custom pyro-compatiable distribution"""
from jax.scipy.special import betaln, gammaln, logsumexp
from .betainc import betainc, logbetainc
from . import cdnb, betacdnb
import jax.numpy as jnp
from scipy import stats
from scipy.stats import betabinom as scipy_betabinom
from scipy.stats import nbinom as scipy_nb, beta
from scipy.stats import binom as scipy_binom
from abc import abstractmethod
from math import ceil
import numpy as np
import gmpy2
import mpmath


class Distribution():
    @staticmethod
    @abstractmethod
    def sample(size: int, **kwargs) -> jnp.ndarray:
        pass
    
    @staticmethod
    @abstractmethod
    def logprob(data: jnp.ndarray, **kwargs) -> jnp.ndarray:
        pass
    
    @staticmethod
    @abstractmethod
    def long_logprob(data, **kwargs) -> list:
        pass
    
    @classmethod
    def long_cdf(cls, x, *args, **kwargs) -> list:
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        logprob = lambda t: cls.long_logprob(t, *args, **kwargs)
        cdfs = dict()
        m = max(x)
        nums = list(range(ceil(m)))
        nums.append(m)
        s = 0
        for v in nums:
            s += gmpy2.exp(logprob(int(v))[0])
            cdfs[v] = s
        return list(map(cdfs.get, x))

    @classmethod
    def long_sf(cls, x, *args, **kwargs) -> list:
        cdf = cls.long_cdf(x, *args, **kwargs)
        one = gmpy2.mpfr('1')
        return [one - cdf for cdf in cdf]
    
    @staticmethod
    @abstractmethod
    def mean(**kwargs):
        pass
    
    @staticmethod
    @abstractmethod
    def long_mean(return_long=False, **kwargs):
        pass
    
    @abstractmethod
    def cdf(**kwargs):
        pass
    
    @abstractmethod
    def sf(**kwargs):
        pass
    

class NB(Distribution):
    @staticmethod
    def sample(r, p, size, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        return scipy_nb.rvs(n=r, p=1.0 - p, size=size)

    @staticmethod
    def logprob(x, r, p, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        p = r * jnp.log1p(-p) + x * jnp.log(p)
        return p  + gammaln(x + r) - gammaln(r) - gammaln(x + 1.0)
    
    @staticmethod
    def long_logprob(x, r, p, r_transform=None) -> list:
        r = NB.r_transform(r, p, r_transform)
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        res = list()
        for x in x:
            t = r * gmpy2.log1p(-p) + x * gmpy2.log(p)
            res.append(t + gmpy2.lgamma(x + r)[0] - gmpy2.lgamma(r)[0] - gmpy2.lgamma(x + 1.0)[0])
        return res

    @staticmethod
    def mean(r, p, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        return p * r / (1 - p)
    
    @staticmethod
    def long_mean(r, p, return_long=False, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        r = gmpy2.mpfr(str(r))
        p = gmpy2.mpfr(str(p))
        mean = p * r / (gmpy2.mpfr('1') - p)
        if return_long:
            return mean
        return float(mean)
    
    @staticmethod
    def long_cdf(x, r, p, skip=-1, ret_dict=False, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        r = gmpy2.mpfr(str(r)); p = gmpy2.mpfr('1') - gmpy2.mpfr(str(p))
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdfs = dict()
        m = max(x)
        nums = list(range(ceil(m)))
        nums.append(m)
        nums = [gmpy2.mpz(int(n)) for n in nums]
        pdf = p ** r
        sp = (gmpy2.mpfr('1') - p)
        if 0 > skip:
            s = pdf
        else:
            s = 0
        cdfs[0] = s
        last_cdf = s
        for v in nums[1:]:
            pdf *= (v + r - 1) / v * sp
            if v > skip:
                s += pdf
            if s < 1:
                last_cdf = s
            cdfs[v] = last_cdf
        if ret_dict:
            return cdfs
        return list(map(cdfs.get, x))
    
    
    @staticmethod
    def cdf(x, r, p, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        return betainc(r, x + 1.0, 1.0 - p)

    @staticmethod
    def sf(x, r, p, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        return betainc(x + 1.0, r, p)

    @staticmethod
    def logsf(x, r, p, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        return logbetainc(x + 1.0, r, p)
    
    @staticmethod
    def r_transform(r, p, r_transform):
        if r_transform in (None, 'NB'):
            return r
        elif r_transform == 'mean':
            return r * (1 - p) / p


class MCNB(Distribution):
    @staticmethod
    def sample(r, p, size):
        raise NotImplementedError

    @staticmethod
    def logprob(x, r, p, r_transform=None):
        r = MCNB.r_transform(r, p, r_transform)
        return cdnb.logprob(x, r, p)
    
    @staticmethod
    def logprob_recurrent(x, r, p, max_sz, r_transform=None):
        r = MCNB.r_transform(r, p, r_transform)
        return cdnb.logprob_recurrent_meta(r, p, x + 1, max_sz)
        
    
    @staticmethod
    def long_logprob(x, r, p) -> list:
        raise NotImplementedError
    
    @staticmethod
    def mean(r, p, r_transform=None):
        r = MCNB.r_transform(r, p, r_transform)
        return p * r / (1 - p ** r)

    @staticmethod
    def long_mean(r, p, return_long=False, r_transform=None):
        r = gmpy2.mpfr(str(r))
        p = gmpy2.mpfr(str(p))
        r = MCNB.r_transform(r, p, r_transform)
        mean = p * r / (1 - p ** r)
        if return_long:
            return mean
        return float(mean)

    @staticmethod
    def long_cdf(x, r, p, skip=-1, ret_dict=False, r_transform=None):
        r = MCNB.r_transform(r, p, r_transform)
        return cdnb.long_cdf(x, r, p, skip=skip, return_dict=ret_dict)
    
    
    @staticmethod
    def cdf(x, r, p, r_transform=None):
        r = MCNB.r_transform(r, p, r_transform=r_transform)
        return cdnb.cdf(x, r, p)

    @staticmethod
    def sf(x, r, p, r_transform=None):
        return 1.0 - MCNB.cdf(x - 1, r, p, r_transform=r_transform)

    @staticmethod
    def logsf(x, r, p, r_transform=None):
        return jnp.log1p(-MCNB.cdf(x - 1, r, p, r_transform=r_transform))
    
    @staticmethod
    def r_transform(r, p, r_transform):
        if not r_transform:
            return r
        if type(r) in (list, tuple):
            r = np.array(r)
        if type(p) in (list, tuple):
            p = np.array(p)
        if r_transform == 'rescale':
            return r / p
        if r_transform == 'NB':
            return r * (1 - p ** r) / (1 - p)
        if r_transform == 'mean':
            return r * (1 - p ** r) / p

class BetaMCNB(Distribution):
    @staticmethod
    def sample(mu, concentration, r, size):
        raise NotImplementedError

    @staticmethod
    def logprob(x, mu, concentration, r, r_transform=None):
        # Should not really be used, merely a workaround for mixalime plotter compatability. Not JIT-compatible.
        r = BetaMCNB.r_transform(mu, concentration, r, r_transform)
        if type(x) in (float, int):
            max_sz = x + 1
            x = int(x)
        else:
            x = jnp.array(x, dtype=int)
            max_sz = int(x.max() + 1)
        lp = betacdnb.logprob_recurrent(r, mu, concentration, max_sz, max_sz)
        return lp[x]
    
    @staticmethod
    def logprob_recurrent(x, mu, concentration, r, max_sz, r_transform=None):
        r = BetaMCNB.r_transform(mu, concentration, r, r_transform)
        return betacdnb.logprob_recurrent_meta(r, mu, concentration, x + 1, max_sz)
        
    
    @staticmethod
    def long_logprob(x, r, p) -> list:
        raise NotImplementedError
    
    
    @staticmethod
    def mean(mu, concentration, r, r_transform=None):
        r = BetaMCNB.r_transform(mu, concentration, r, r_transform)
        k = concentration
        p = mu
        q = 1 - p
        kq = k * q
        num = jnp.log(k) + jnp.log(p) * 2 + jnp.log(r) + gammaln(kq) + gammaln(k + r)
        denom = logsumexp(jnp.array([gammaln(kq + 1) + gammaln(k + r),
                                     jnp.log(k) + jnp.log1p(-p) + gammaln(k) + gammaln(kq + r)]).T,
                          b=jnp.array([1, -1]), axis=-1)
        return jnp.exp(num - denom)
    
    @staticmethod
    def long_mean(r, p, return_long=False, r_transform=None):
        raise NotImplementedError
    
    @staticmethod
    def long_cdf(x, mu, concentration, r, skip=-1, ret_dict=False, r_transform=None):
        raise NotImplementedError
        # TODO
        r = BetaMCNB.r_transform(mu, concentration, r, r_transform)
        return MCNB.long_cdf(x, mu, concentration, r, skip=skip, return_dict=ret_dict)
    
    
    @staticmethod
    def cdf(x, mu, concentration, r, r_transform=None):
        raise NotImplementedError
        # TODO
        r = BetaMCNB.r_transform(mu, concentration, r, r_transform)
        return betacdnb.cdf(x, r, mu, concentration)

    @staticmethod
    def sf(x, r, p, r_transform=None):
        raise NotImplementedError
        # TODO
        r = MCNB.r_transform(r, p, r_transform)
        return 1.0 - MCNB.cdf(x - 1, r, p)

    @staticmethod
    def logsf(x, r, p, r_transform=None):
        raise NotImplementedError
        # TODO
        r = MCNB.r_transform(r, p, r_transform)
        return jnp.log1p(-MCNB.cdf(x - 1, r, p))
    
    @staticmethod
    def r_transform(mu, concentration, r, r_transform):
        if not r_transform:
            return r
        if r_transform == 'rescale':
            return r / mu
        mean = BetaMCNB.mean(mu, concentration, r, None)
        if r_transform == 'NB':
            return r ** 2 / mean * mu / (1 - mu)
        if r_transform == 'mean':
            return r ** 2 / mean

class Binom(Distribution):
    @staticmethod
    def sample(r, p, size, r_transform=None):
        return scipy_binom.rvs(n=r, p=1.0 - p, size=size)

    @staticmethod
    def logprob(x, r, p, r_transform=None):
        p = x * jnp.log(p) + (r-x) * jnp.log1p(-p)
        return p + gammaln(r + 1) - gammaln(x + 1) - gammaln(r - x + 1)
    
    @staticmethod
    def cdf(x, r, p, r_transform=None):
        return betainc(r - x, x + 1.0, 1.0 - p)
    
    @staticmethod
    def sf(x, r, p, r_transform=None):
        return betainc(x + 1.0, r - x, p)
    
    @staticmethod
    def mean(r, p, r_transform=None):
        return r * p
    
    @staticmethod
    def long_mean(r, p, return_long=False, r_transform=None):
        r = gmpy2.mpfr(str(r))
        p = gmpy2.mpfr(str(p))
        mean = p * r
        if return_long:
            return mean
        return float(mean)
    
    @staticmethod
    def long_cdf(x, r, p, skip=-1, ret_dict=False, r_transform=None):
        return scipy_binom.cdf(x, r, p)
    
    @staticmethod
    def long_sf(x, r, p, r_transform=None):
        return scipy_binom.sf(x, r, p)

class BetaBinom(Distribution):
    @staticmethod
    def sample(r, mu, concentration, size, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return scipy_betabinom.rvs(n=r, a=a, b=b, size=size)

    @staticmethod
    def logprob(x, r, mu, concentration, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return scipy_betabinom.logpmf(x, n=r, a=a, b=b)
    
    @staticmethod
    def cdf(x, r, mu, concentration, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return scipy_betabinom.cdf(x, n=r, a=a, b=b)
    
    @staticmethod
    def sf(x, r, mu, concentration, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return scipy_betabinom.sf(x, n=r, a=a, b=b)
    
    @staticmethod
    def mean(r, mu, concentration, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        return scipy_betabinom.mean(n=r, a=a, b=b)
    
    @staticmethod
    def long_mean(r, p, return_long=False, r_transform=None):
        raise NotImplementedError
    
    @staticmethod
    def long_cdf(x, r, mu, concentration, skip=-1, ret_dict=False, r_transform=None):
        mu = gmpy2.mpq(str(mu)); concentration = gmpy2.mpfr(str(concentration))
        r = gmpy2.mpfr(str(r))
        a = mu * concentration
        b = (gmpy2.mpq('1') - mu) * concentration
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdfs = dict()
        m = max(x)
        nums = list(range(ceil(m)))
        nums.append(m)
        nums = [gmpy2.mpz(int(n)) for n in nums]
        base = gmpy2.mpfr(str(mpmath.gammaprod(list(map(str, [b + r, a + b])), 
                                                list(map(str, [a + r + b, b])))))
        if 0 > skip:
            s = base
        else:
            s = 0
        cdfs[0] = s
        last_cdf = s
        pmf = base
        num = gmpy2.mpq('1')
        denum = gmpy2.mpq('1')
        order = 0
        pow_2 = gmpy2.mpfr('2')
        for v in nums[1:]:
            order_num, num = gmpy2.frexp(num * (1 + r - v) * (a + v - 1))
            order_denum, denum = gmpy2.frexp(denum * v * (b + r - v))
            order += order_num - order_denum
            pmf = (num / denum) * base * pow_2 ** order
            if v > skip:
                s += pmf
            if s < 1:
                last_cdf = s
            cdfs[v] = last_cdf
        if ret_dict:
            return cdfs
        return list(map(cdfs.get, x))
    
    @staticmethod
    def long_sf(x, r, mu, concentration, r_transform=None):
        o = gmpy2.mpfr('1')
        return [o - t for t in BetaBinom.long_cdf(x, r, mu, concentration, r_transform=r_transform)]  
    

class LeftTruncatedBinom(Binom):
    def __init__(self, r, probs, left=5, validate_args=None):
        self.left = left
        self.left_vals = jnp.arange(1, left)
        super().__init__(r, probs, validate_args=validate_args)

    @staticmethod
    def sample(r, p, left, size: int, r_transform=None):
        u = stats.uniform.rvs(size=size)
        b = scipy_binom(p=p, n=r)
        cdf = b.cdf
        a = cdf(left)
        return b.ppf(a + u * (1.0 - a))

    @staticmethod
    def logprob(x, r, p, left, r_transform=None):
        left = float(left)
        logprob = Binom.logprob
        lp = jnp.where(x <= left, -jnp.inf, logprob(x, r, p))
        lp = logprob(x, r, p) - jnp.log1p(-sum(jnp.exp(logprob(i, r, p))
                                               for i in range(int(left) + 1)))
        return jnp.where(x <= left, -jnp.inf, lp)

    @staticmethod
    def long_logprob(x, r, p, left, r_transform=None) -> list:
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        res = list()
        logprob = super(Binom, Binom).long_logprob
        denom = gmpy2.log1p(-sum(gmpy2.exp(logprob(i, r, p)[0])
                                 for i in range(int(left) + 1)))
        for x in x:
            res.append(logprob(x, r, p)[0] - denom)
        return res

    @staticmethod
    def long_cdf(x, r, p, left, r_transform=None):
        s = super(LeftTruncatedBinom, LeftTruncatedBinom)
        if type(r) in (list, np.ndarray):
            sm = list(map(gmpy2.mpfr, s.long_sf(left, r, p)))
            res = [gmpy2.mpfr(cdf) / denom for cdf, denom in zip(s.long_cdf(x, r, p, r_transform=r_transform, skip=left), sm)]
        else:
            sm = gmpy2.mpfr(s.long_sf(left, r, p, r_transform=r_transform, skip=left))
            res = [gmpy2.mpfr(c) / sm for c in s.long_cdf(x, r, p)]
        return res 
    
    @staticmethod
    def long_sf(x, r, p, left, r_transform=None):
        sf = super(LeftTruncatedBinom, LeftTruncatedBinom).long_sf
        return sf(x, r, p) / sf(left, r, p)

    @staticmethod
    def mean(r, p, left, r_transform=None):
        s = super(LeftTruncatedBinom, LeftTruncatedBinom)
        m = s.mean(r, p) 
        m -= sum(i * jnp.exp(s.logprob(i, r, p)) for i in range(1, left + 1)) 
        return m / s.sf(left, r, p)
    
    @staticmethod
    def long_mean(r, p, left, return_long=False, r_transform=None):
        s = super(Binom, Binom)
        m = s.long_mean(r, p, return_long=True) 
        m -= sum(i * gmpy2.exp(s.long_logprob(i, r, p)[0]) for i in range(1, left + 1)) 
        mean = m / (gmpy2.mpfr('1') - s.long_cdf(left, r, p)[0])
        if return_long:
            return mean
        return float(mean)

    @staticmethod
    def cdf(x, r, p, left, r_transform=None):
        return sum(jnp.exp(Binom.logprob(i, r, p, left))
                   for i in range(x + 1))

    @staticmethod
    def sf(x, r, p, left, r_transform=None):
        return 1 - Binom.cdf(x, r, p, left)


class LeftTruncatedBetaBinom(BetaBinom):
    @staticmethod
    def sample(r, p, left, size: int, r_transform=None):
        raise NotImplementedError

    @staticmethod
    def logprob(x, r, mu, concentration, left, r_transform=None):
        left = float(left)
        logprob = BetaBinom.logprob
        lp = jnp.where(x <= left, -jnp.inf, logprob(x, r, mu, concentration))
        lp = logprob(x, r, mu, concentration) - jnp.log1p(-sum(jnp.exp(logprob(i, r, mu, concentration))
                                               for i in range(int(left) + 1)))
        return jnp.where(x <= left, -jnp.inf, lp)

    @staticmethod
    def long_logprob(x, r, mu, concentration, left, r_transform=None) -> list:
        raise NotImplementedError

    @staticmethod
    def long_cdf(x, r, mu, concentration, left, r_transform=None):
        s = super(LeftTruncatedBetaBinom, LeftTruncatedBetaBinom)
        if type(r) in (list, np.ndarray):
            sm = s.long_sf(left, r, mu, concentration)
            res = [gmpy2.mpfr(cdf) / denom for cdf, denom in zip(s.long_cdf(x, r, mu, concentration, r_transform=r_transform,
                                                                            skip=left), sm)]
        else:
            sm = s.long_sf(left, r, mu, concentration, r_transform=r_transform)[0]
            res = [gmpy2.mpfr(c) / sm for c in s.long_cdf(x, r, mu, concentration,
                                                          skip=left)]
        return res 
    
    @staticmethod
    def long_sf(x, r, mu, concentration, left, r_transform=None):
        return [1 - t for t in LeftTruncatedBetaBinom.long_cdf(x, r, mu, concentration, left, r_transform)]

    @staticmethod
    def mean(r, mu, concentration, left, r_transform=None):
        s = super(LeftTruncatedBetaBinom, LeftTruncatedBetaBinom)
        m = s.mean(r, mu, concentration) 
        m -= sum(i * jnp.exp(s.logprob(i, r, mu, concentration)) for i in range(1, left + 1)) 
        return m / s.sf(left, r, mu, concentration)
    
    @staticmethod
    def long_mean(r, mu, concentration, left, return_long=False, r_transform=None):
        s = super(BetaBinom, BetaBinom)
        m = s.long_mean(r, mu, concentration, return_long=True) 
        m -= sum(i * gmpy2.exp(s.long_logprob(i, r, mu, concentration)[0]) for i in range(1, left + 1)) 
        mean = m / (gmpy2.mpfr('1') - s.long_cdf(left, r, mu, concentration)[0])
        if return_long:
            return mean
        return float(mean)

    @staticmethod
    def cdf(x, r, mu, concentration, left, r_transform=None):
        return sum(jnp.exp(BetaBinom.logprob(i, r, mu, concentration, left))
                   for i in range(x + 1))

    @staticmethod
    def sf(x, r, mu, concentration, left, r_transform=None):
        raise NotImplementedError



    
class LeftTruncatedNB(NB):
    def __init__(self, r, probs, left=5, validate_args=None):
        self.left = left
        self.left_vals = jnp.arange(1, left)
        super().__init__(r, probs, validate_args=validate_args)

    @staticmethod
    def sample(r, p, left, size: int, r_transform=None):
        r = NB.r_transform(r, p, r_transform)
        u = stats.uniform.rvs(size=size)
        nb = scipy_nb(p=1 - p, n=r)
        cdf = nb.cdf
        a = cdf(left)
        return nb.ppf(a + u * (1.0 - a))

    @staticmethod
    def logprob(x, r, p, left, r_transform=None):
        left = float(left)
        logprob = super(LeftTruncatedNB, LeftTruncatedNB).logprob
        left_cdf = sum(jnp.exp(logprob(i, r, p, r_transform=r_transform)) for i in range(int(left) + 1))
        denom = jnp.log1p(-left_cdf)
        lp = logprob(x, r, p, r_transform=r_transform) - denom
        return jnp.where((x <= left) , -jnp.inf, lp)

    @staticmethod
    def long_logprob(x, r, p, left, r_transform=None) -> list:
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        res = list()
        logprob = super(LeftTruncatedNB, LeftTruncatedNB).long_logprob
        denom = gmpy2.log1p(-sum(gmpy2.exp(logprob(i, r, p, r_transform=r_transform)[0])
                                 for i in range(int(left) + 1)))
        for x in x:
            res.append(logprob(x, r, p)[0] - denom)
        return res

    @staticmethod
    def long_cdf(x, r, p, left, r_transform=None):
        s = super(LeftTruncatedNB, LeftTruncatedNB)
        cdf = s.long_cdf
        sm = gmpy2.mpfr('1') - cdf(left, r, p, r_transform=r_transform)[0]
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdf = cdf(x, r, p, skip=left, ret_dict=True, r_transform=r_transform)
        res = list()
        precision_loss = False
        for x in x:
            if precision_loss:
                res.append(res[-1])
                continue
            r = cdf[x] / sm if x > left else 0.0
            while r >= 1:
                x -= 1
                r = cdf[x] / sm
                precision_loss = True
            res.append(r)
        return res 

    @staticmethod
    def mean(r, p, left, r_transform=None):
        s = super(LeftTruncatedNB, LeftTruncatedNB)
        m = s.mean(r, p) 
        m -= sum(i * jnp.exp(s.logprob(i, r, p, r_transform=r_transform)) for i in range(1, left + 1)) 
        return m / s.sf(left, r, p)
    
    @staticmethod
    def long_mean(r, p, left, return_long=False, r_transform=None):
        s = super(LeftTruncatedNB, LeftTruncatedNB)
        m = s.long_mean(r, p, return_long=True, r_transform=r_transform) 
        m -= sum(i * gmpy2.exp(s.long_logprob(i, r, p)[0]) for i in range(1, left + 1)) 
        mean = m / (gmpy2.mpfr('1') - s.long_cdf(left, r, p, r_transform=r_transform)[0])
        if return_long:
            return mean
        return float(mean)

    @staticmethod
    def cdf(x, r, p, left, r_transform=None):
        return sum(jnp.exp(LeftTruncatedNB.logprob(i, r, p, left, r_transform=r_transform))
                   for i in range(x + 1))

    @staticmethod
    def sf(x, r, p, left, r_transform=None):
        return 1 - LeftTruncatedNB.cdf(x, r, p, left, r_transform=r_transform)

class LeftTruncatedMCNB(MCNB):

    @staticmethod
    def sample(r, p, left, size: int):
        raise NotImplementedError

    @staticmethod
    def logprob(x, r, p, left, r_transform=None):
        left = float(left)
        logprob = MCNB.logprob
        # logsf = MCNB.logsf
        # lp = logprob(x, r, p, r_transform=r_transform) - logsf(left + 1, r, p, r_transform=r_transform)
        lp = logprob(x, r, p, r_transform=r_transform) - jnp.log1p(-jnp.exp(logprob(jnp.arange(0, left + 1), r, p, r_transform)).sum())
        return jnp.where(x <= left, -jnp.inf, lp)
    
    @staticmethod
    def logprob_recurrent(x, r, p, left, max_sz, r_transform=None):
        lp = MCNB.logprob_recurrent(x, r, p, max_sz, r_transform=r_transform)
        sm = jnp.log1p(-jnp.exp(lp.at[..., :left + 1].get()).sum(axis=-1, keepdims=True))
        lp = lp - sm
        lp = lp.at[..., :left].set(-float('inf'))
        return lp

    @staticmethod
    def long_logprob(x, r, p, left) -> list:
        raise NotImplementedError

    @staticmethod
    def long_cdf(x, r, p, left, r_transform=None):
        s = MCNB
        cdf = s.long_cdf
        sm = gmpy2.mpfr('1') - cdf(left, r, p, r_transform=r_transform)[0]
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdf = cdf(x, r, p, skip=left, ret_dict=True, r_transform=r_transform)
        res = list()
        precision_loss = False
        for x in x:
            if precision_loss:
                res.append(res[-1])
                continue
            r = cdf[x] / sm if x > left else 0.0
            while r >= 1:
                x -= 1
                r = cdf[x] / sm
                precision_loss = True
            res.append(r)
        return res 

    @staticmethod
    def mean(r, p, left, r_transform=None):
        m = MCNB.mean(r, p, r_transform=r_transform) 
        prob = jnp.exp(MCNB.logprob_recurrent(jnp.array([left]), jnp.array([r]), p, left + 1, r_transform=r_transform).flatten())
        sf = 1 - prob.sum()
        m -= jnp.sum(jnp.arange(0, left + 1) * prob)
        return m / sf
    
    @staticmethod
    def long_mean(r, p, left, return_long=False, r_transform=None):
        raise NotImplementedError

    @staticmethod
    def cdf(x, r, p, left, r_transform=None):
        sm = MCNB.cdf(left, r, p, r_transform=r_transform)
        t = (MCNB.cdf(x, r, p, r_transform=r_transform) - sm) / (1 - sm)
        return t

    @staticmethod
    def sf(x, r, p, left, r_transform=None):
        return 1 - LeftTruncatedMCNB.cdf(x - 1, r, p, left, r_transform=r_transform)

class _TruncatedNB(NB):
    @staticmethod
    def sample(r, p, left, right, size: int, r_transform=None):
        r_transform = NB.r_transform(r, p, r_transform)
        u = stats.uniform.rvs(size=size)
        nb = scipy_nb(p=p, n=r)
        cdf = nb.cdf
        a = cdf(left)
        b = cdf(right)
        return nb.ppf(a + u * (b - a))

    @staticmethod
    def logprob(x, r, p, left, right, r_transform=None):
        logprob = super(_TruncatedNB, _TruncatedNB).logprob
        cdf = lambda x: super(_TruncatedNB, _TruncatedNB).cdf(x, r, p, r_transform=r_transform)
        denom = cdf(right) - cdf(left)
        lp = logprob(x, r, p) - jnp.log(denom)
        return jnp.where((x <= left) | (x > right), -jnp.inf, lp)

class _TruncatedBinom(Binom):
    @staticmethod
    def sample(r, p, left, right, size: int, r_transform=None):
        u = stats.uniform.rvs(size=size)
        nb = scipy_binom(p=p, n=r)
        cdf = nb.cdf
        a = cdf(left)
        b = cdf(right)
        return nb.ppf(a + u * (b - a))

    @staticmethod
    def logprob(x, r, p, left, right, r_transform=None):
        logprob = super(_TruncatedBinom, _TruncatedBinom).logprob
        cdf = lambda x: super(_TruncatedBinom, _TruncatedBinom).cdf(x, r, p)
        denom = cdf(right) - cdf(left)
        lp = logprob(x, r, p) - jnp.log(denom)
        return jnp.where((x <= left) | (x > right), -jnp.inf, lp)   

class LeftTruncatedBetaMCNB(MCNB):

    @staticmethod
    def sample(mu, concentration, r, left, size: int):
        raise NotImplementedError

    @staticmethod
    def logprob(x, mu, concentration, r, left, r_transform=None):
        lp = BetaMCNB.logprob(x, mu, concentration, r, r_transform=r_transform)
        sm = jnp.log1p(-jnp.exp(lp.at[..., :left + 1].get()).sum(axis=-1, keepdims=True))
        lp = lp - sm
        lp = lp.at[..., :left].set(-float('inf'))
        return lp

    @staticmethod
    def logprob_recurrent(x, mu, concentration, r, left, max_sz, r_transform=None):
        lp = BetaMCNB.logprob_recurrent(x, mu, concentration, r, max_sz, r_transform=r_transform)
        sm = jnp.log1p(-jnp.exp(lp.at[..., :left + 1].get()).sum(axis=-1, keepdims=True))
        lp = lp - sm
        lp = lp.at[..., :left + 1].set(-float('inf'))
        return lp

    @staticmethod
    def long_logprob(x, r, p, left) -> list:
        raise NotImplementedError

    @staticmethod
    def long_cdf(x, r, p, left, r_transform=None):
        raise NotImplementedError 
        # TODO
        s = MCNB
        cdf = s.long_cdf
        sm = gmpy2.mpfr('1') - cdf(left, r, p, r_transform=r_transform)[0]
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdf = cdf(x, r, p, skip=left, ret_dict=True, r_transform=r_transform)
        res = list()
        precision_loss = False
        for x in x:
            if precision_loss:
                res.append(res[-1])
                continue
            r = cdf[x] / sm if x > left else 0.0
            while r >= 1:
                x -= 1
                r = cdf[x] / sm
                precision_loss = True
            res.append(r)
        return res 

    @staticmethod
    def mean(mu, concentration, r, left, r_transform=None):
        m = BetaMCNB.mean(mu, concentration, r,)
        probs = jnp.exp(BetaMCNB.logprob_recurrent(left, mu, concentration, r, left + 1)[:left + 1])
        m -= (probs * jnp.arange(0, left + 1)).sum()
        return m / (1 - probs.sum())
    
    @staticmethod
    def long_mean(r, p, left, return_long=False, r_transform=None):
        raise NotImplementedError

    @staticmethod
    def cdf(x, r, p, left, r_transform=None):
        raise NotImplementedError
        sm = MCNB.cdf(left, r, p, r_transform=r_transform)
        t = (MCNB.cdf(x, r, p, r_transform=r_transform) - sm) / (1 - sm)
        return t

    @staticmethod
    def sf(x, r, p, left, r_transform=None):
        return 1 - LeftTruncatedMCNB.cdf(x - 1, r, p, left, r_transform=r_transform)

class BetaNB(Distribution):
    @staticmethod
    def sample(mu, concentration, r, size: int, r_transform=None):
        b = mu * concentration
        a = (1.0 - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        p = beta.rvs(a, b, size=size)
        return scipy_nb.rvs(n=r, p=p)

    @staticmethod
    def logprob(x, mu, concentration, r, r_transform=None):
        b = mu * concentration
        a = (1.0 - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        return betaln(a + r, b + x) - betaln(a, b) + gammaln(r + x) -\
               gammaln(x + 1.0) - gammaln(r)

    @staticmethod
    def long_logprob(x, mu, concentration, r, r_transform=None) -> list:
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        res = list()
        b = mu * concentration
        a = (1.0 - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        betaln = BetaNB.long_betaln
        gammaln = gmpy2.lgamma
        for x in x:
            t = betaln(a + r, b + x) - betaln(a, b) + gammaln(r + x)[0] -\
                gammaln(x + 1.0)[0] - gammaln(r)[0]
            res.append(t)
        return res

    @staticmethod
    def mean(mu, concentration, r, r_transform=None):
        b = mu * concentration
        a = (1.0 - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        return r * b / (a - 1)
    
    @staticmethod
    def long_mean(mu, concentration, r, return_long=False, r_transform=None):
        mu = gmpy2.mpfr(str(mu))
        concentration = gmpy2.mpfr(str(concentration))
        r = gmpy2.mpfr(str(r))
        b = mu * concentration
        a = (gmpy2.mpfr(1) - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        mean = r * b / (a - 1)
        if return_long:
            return mean
        return float(mean)
    
    @staticmethod
    def cdf(x, mu, concentration, r, r_transform=None):
        return sum(jnp.exp(BetaNB.logprob(i, mu, concentration, r, r_transform=r_transform))
                   for i in range(x + 1))

    @staticmethod
    def sf(x, mu, concentration, r, r_transform=None):
        return 1.0 - BetaNB.cdf(x, mu, concentration, r, r_transform=r_transform)
    
    @staticmethod
    def long_prob(x, mu, concentration, r, skip=-1, r_transform=None):
        mu = gmpy2.mpq(str(mu)); concentration = gmpy2.mpfr(str(concentration))
        r = gmpy2.mpfr(str(r))
        b = mu * concentration
        a = (gmpy2.mpq('1') - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdfs = dict()
        m = max(x)
        nums = list(range(ceil(m)))
        nums.append(m)
        nums = [gmpy2.mpz(int(n)) for n in nums]
        base = gmpy2.mpfr(str(mpmath.gammaprod(list(map(str, [a + r, a + b])), 
                                                list(map(str, [a + r + b, a])))))
        if 0 > skip:
            s = base
        else:
            s = 0
        cdfs[0] = s
        frac = 1
        for v in nums[1:]:
            frac *= (v + r - 1) / (v + a + b + r - 1)  * ((v + b - 1) / v)
            cdfs[v] = frac * base
        return list(map(cdfs.get, x))
    
    @staticmethod
    def long_cdf(x, mu, concentration, r, skip=-1, ret_dict=False, r_transform=None):
        mu = gmpy2.mpq(str(mu)); concentration = gmpy2.mpfr(str(concentration))
        r = gmpy2.mpfr(str(r))
        b = mu * concentration
        a = (gmpy2.mpq('1') - mu) * concentration
        r = BetaNB.r_transform(r, a, b, mu, r_transform=r_transform)
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdfs = dict()
        m = max(x)
        nums = list(range(ceil(m)))
        nums.append(m)
        nums = [gmpy2.mpz(int(n)) for n in nums]
        base = gmpy2.mpfr(str(mpmath.gammaprod(list(map(str, [a + r, a + b])), 
                                                list(map(str, [a + r + b, a])))))
        if 0 > skip:
            s = base
        else:
            s = 0
        cdfs[0] = s
        last_cdf = s
        frac = gmpy2.mpfr('1') * base
        for v in nums[1:]:
            frac *= (v + r - 1) / (v + a + b + r - 1)  * ((v + b - 1) / v)
            if v > skip:
                s += frac
            if s < 1:
                last_cdf = s
            cdfs[v] = last_cdf
        if ret_dict:
            return cdfs
        return list(map(cdfs.get, x))


    @staticmethod
    def long_betaln(a, b):
       return gmpy2.lgamma(a)[0] + gmpy2.lgamma(b)[0] - gmpy2.lgamma(a + b)[0]
   
    @staticmethod
    def r_transform(r, a, b, mu, r_transform: str):
        if not r_transform:
            return r
        if r_transform == 'NB':
            return r * (a - 1) / b * (mu / (1 - mu))
        if r_transform == 'mean':
            return r * (a - 1) / b
        


class LeftTruncatedBetaNB(BetaNB):
    def __init__(self, r, mu, concentration, left, validate_args=None):
        self.left_vals = jnp.arange(0, left + 1)
        self.left = left
        super().__init__(r, mu, concentration, validate_args=validate_args)

    @staticmethod
    def sample(mu, concentration, r, left, size: int, r_transform=None):
        a = mu * concentration
        b = (1.0 - mu) * concentration
        p = beta.rvs(a, b, size=size)
        return LeftTruncatedNB.sample(r=r, p=p, left=left, size=size, r_transform=r_transform)

    @staticmethod
    def logprob(x, mu, concentration, r, left=4, r_transform=None):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        cdf = s.cdf
        logprob = s.logprob
        sm = -cdf(left, mu, concentration, r, r_transform=r_transform)
        lp = jnp.where(x <= left, -jnp.inf, logprob(x, mu, concentration, r, r_transform=r_transform))
        return lp - jnp.log1p(sm)

    @staticmethod
    def long_logprob(x, mu, concentration, r, left, r_transform=None) -> list:
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        cdf = BetaNB.long_cdf
        logprob = s.long_logprob(x, mu, concentration, r, r_transform=r_transform)
        sm = gmpy2.log1p(-cdf(left, mu, concentration, r, r_transform=r_transform)[0])
        return [lp - sm  if left < x else -np.inf for lp, x in zip(logprob, x)]

    @staticmethod
    def cdf(x, mu, concentration, r, left, r_transform=None):
        return sum(jnp.exp(LeftTruncatedBetaNB.logprob(i, mu, concentration, r,
                                                       left, r_transform=r_transform))
                   for i in range(x + 1))
    
    @staticmethod
    def long_cdf(x, mu, concentration, r, left, r_transform=None):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        cdf = s.long_cdf
        sm = gmpy2.mpfr('1') - cdf(left, mu, concentration, r, r_transform=r_transform)[0]
        if type(x) in (np.ndarray, list):
            x = list(x)
        else:
            x = [x]
        cdf = cdf(x, mu, concentration, r, skip=left, ret_dict=True, r_transform=r_transform)
        res = list()
        precision_loss = False
        for x in x:
            if precision_loss:
                res.append(res[-1])
                continue
            r = cdf[x] / sm if x > left else 0.0
            while r >= 1:
                x -= 1
                r = cdf[x] / sm
                precision_loss = True
            res.append(r)
        return res 

    @staticmethod
    def mean(mu, concentration, r, left, r_transform=None):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        m = s.mean(mu, concentration, r, r_transform=r_transform) 
        return (m - sum(i * jnp.exp(s.logprob(i, mu, concentration, r, r_transform=r_transform))
                       for i in range(1, left + 1))) / s.sf(left, mu,
                                                            concentration, r,
                                                            r_transform=r_transform)

    @staticmethod
    def long_mean(mu, concentration, r, left, return_long=False, r_transform=None):
        s = super(LeftTruncatedBetaNB, LeftTruncatedBetaNB)
        m = s.long_mean(mu, concentration, r, return_long=True, r_transform=r_transform) 
        mean = (m - sum(i * gmpy2.exp(s.long_logprob(i, mu, concentration, r, r_transform=r_transform)[0])
                        for i in range(1, left + 1))) / (gmpy2.mpfr('1') - s.long_cdf(left, mu,
                                                                                      concentration, r,
                                                                                      r_transform=r_transform)[0])
        if return_long:
            return mean
        return float(mean)
