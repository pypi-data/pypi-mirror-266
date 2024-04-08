from typing import List

import sympy


def get(incoming: List[int], outgoing: List[int], model="ufo_sm"):
    # TODO check if we have it cached
    # TODO check if ML
    # TODO check if grid
    raise NotImplementedError("Not implemented yet")


def compute(pdg_incoming: List[int], pdg_outgoing: List[int], model="ufo_sm"):
    # Import only conditionally to avoid loading the whole package
    try:
        from feynamp.form import compute_squared
        from feynml.interface.qgraf import style
        from feynmodel.interface.qgraf import feynmodel_to_qgraf, pdg_id_to_qgraf_name
        from feynmodel.interface.ufo import load_ufo_model
        from pyfeyn2.feynmandiagram import FeynML
        from pyqgraf import qgraf
        from xsdata.formats.dataclass.parsers import XmlParser
    except ImportError:
        raise ImportError("Please install the feynamp packages")

    # Load the model
    fm = load_ufo_model(model)
    # make it qgraf ready
    qfm = feynmodel_to_qgraf(fm, True, False)
    # make sure qgraf is installed
    qgraf.install()

    momentum_index = 0
    incoming = []
    outgoing = []
    for pdg in pdg_incoming:
        str_pdg = pdg_id_to_qgraf_name(fm, pdg, True)
        incoming.append(f"{str_pdg}[p{momentum_index}]")
        momentum_index += 1
    for pdg in pdg_outgoing:
        str_pdg = pdg_id_to_qgraf_name(fm, pdg, False)
        outgoing.append(f"{str_pdg}[p{momentum_index}]")
        momentum_index += 1
    # run it
    xml_string = qgraf.run(
        ", ".join(incoming),
        ", ".join(outgoing),
        loops=0,
        loop_momentum="l",
        model=qfm,
        style=style,
    )
    parser = XmlParser()
    fml = parser.from_string(xml_string, FeynML)
    fds = fml.diagrams

    ret = compute_squared(fds, fm)
    # res = sympy.simplify(ret.subs({"s": "-u-t", "Nc": 3, "Cf": "4/3", "ee": 1, "G": 1}))
    return ret
