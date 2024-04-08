import jax
import sympy
import sympy2jax
from sympy import Symbol

from matrixelement.qed.e_mu_e_mu import e_mu_e_mu


class e_mu_e_mu_massless(e_mu_e_mu):
    @classmethod
    def sympy_wrap(cls, expr):
        # We substitute the masses with 0
        return expr.subs(
            {
                e_mu_e_mu.Mass_MM: 0,
                e_mu_e_mu.Mass_Me: 0,
            }
        ).simplify()
