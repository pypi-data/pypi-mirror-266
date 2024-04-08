import sympy2jax


class MatrixElement:
    @classmethod
    def jax(cls):
        mod = sympy2jax.SymbolicModule(cls.sympy(), make_array=False)
        # jax.jit(mod)
        return mod

    @classmethod
    def sympy_wrap(cls, expr):
        """
        This function is used to wrap the sympy expressions from the _sympy() function or the _compute() function.
        """
        return expr

    @classmethod
    def _sympy(cls):
        raise NotImplementedError("MatrixElement.sympy() is not implemented")

    @classmethod
    def sympy(cls):
        return cls.sympy_wrap(cls._sympy())

    @classmethod
    def _compute(cls):
        # TODO compute generic case here
        raise NotImplementedError("MatrixElement.compute() is not implemented")

    @classmethod
    def compute(cls):
        return cls.sympy_wrap(cls._compute())
