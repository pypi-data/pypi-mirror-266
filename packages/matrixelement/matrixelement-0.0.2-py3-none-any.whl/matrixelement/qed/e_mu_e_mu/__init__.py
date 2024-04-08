import jax
import sympy
import sympy2jax
from sympy import Symbol

from matrixelement.matrixelement import MatrixElement


class e_mu_e_mu(MatrixElement):
    Mass_MM = Symbol("Mass_MM")
    Mass_Me = Symbol("Mass_Me")
    ee = Symbol("ee")
    t = Symbol("t")
    s = Symbol("s")
    u = Symbol("u")

    @classmethod
    def _sympy(cls):
        Mass_MM = cls.Mass_MM
        Mass_Me = cls.Mass_Me
        ee = cls.ee
        t = cls.t
        s = cls.s
        u = cls.u
        e = (
            16 * Mass_MM**4 * Mass_Me**4 * ee**4 / t**2
            - 8 * Mass_MM**4 * Mass_Me**2 * ee**4 / t**2
            + 4 * Mass_MM**4 * ee**4 / t
            + 4 * Mass_MM**4 * ee**4 / t**2
            - 8 * Mass_MM**2 * Mass_Me**4 * ee**4 / t**2
            + 8 * Mass_MM**2 * Mass_Me**2 * ee**4 / t**2
            - 4 * Mass_MM**2 * ee**4 * s / t**2
            - 4 * Mass_MM**2 * ee**4 * u / t**2
            + 4 * Mass_Me**4 * ee**4 / t
            + 4 * Mass_Me**4 * ee**4 / t**2
            - 4 * Mass_Me**2 * ee**4 * s / t**2
            - 4 * Mass_Me**2 * ee**4 * u / t**2
            + 2 * ee**4 * s**2 / t**2
            + 2 * ee**4 * u**2 / t**2
        )
        return e

    @classmethod
    def _compute(cls):
        try:
            from feynamp.form import compute_squared
            from feynml.interface.qgraf import style
            from feynmodel.interface.qgraf import (
                feynmodel_to_qgraf,
                pdg_id_to_qgraf_name,
            )
            from feynmodel.interface.ufo import load_ufo_model
            from pyfeyn2.feynmandiagram import FeynML
            from pyqgraf import qgraf
            from xsdata.formats.dataclass.parsers import XmlParser
        except ImportError:
            raise ImportError("Please install the feynamp packages")

        fm = load_ufo_model("ufo_sm")
        fm.remove_object(fm.get_particle("G0"))
        fm.remove_object(fm.get_particle("Z"))
        fm.remove_object(fm.get_particle("H"))
        qfm = feynmodel_to_qgraf(fm, True, False)
        qgraf.install()
        xml_string = qgraf.run(
            "e_minus[p1], mu_minus[p2]",
            "e_minus[p3], mu_minus[p4]",
            loops=0,
            loop_momentum="l",
            model=qfm,
            style=style,
        )
        parser = XmlParser()
        fml = parser.from_string(xml_string, FeynML)
        fds = fml.diagrams

        ret = compute_squared(fds, fm)
        return ret
