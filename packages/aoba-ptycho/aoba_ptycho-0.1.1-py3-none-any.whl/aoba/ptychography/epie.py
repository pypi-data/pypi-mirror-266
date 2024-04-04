import math
import os

import nlcpy as np


_VE_LIB_PATH = os.path.join(os.path.dirname(__file__), "jit/kernel.so")
_lib = np.jit.CustomVELibrary(path=_VE_LIB_PATH)

_core = _lib.get_function(
    "core",
    args_type=(
        np.ve_types.int32,  # N_it
        np.ve_types.int32,  # xscanSize
        np.ve_types.int32,  # yscanSize
        np.ve_types.float64,  # resolutionX
        np.ve_types.float64,  # resolutionY
        np.ve_types.int32,  # Xsize
        np.ve_types.int32,  # Ysize
        np.ve_types.int32,  # objArraySizeX
        np.ve_types.int32,  # objArraySizeY
        np.ve_types.int32,  # prbArraySizeX
        np.ve_types.int32,  # prbArraySizeY
        np.ve_types.uint64,  # Xw
        np.ve_types.uint64,  # Yw
        np.ve_types.uint64,  # xList
        np.ve_types.uint64,  # yList
        np.ve_types.float64,  # alpha
        np.ve_types.float64,  # beta
        np.ve_types.uint64,  # object
        np.ve_types.uint64,  # probe
        np.ve_types.uint64,  # CDIstack
        np.ve_types.uint64,  # rfactors
        np.ve_types.int32,  # Xa
        np.ve_types.int32,  # Xb
        np.ve_types.int32,  # Ya
        np.ve_types.int32,  # Yb
    ),
    ret_type=np.ve_types.void,
)


def ePIE_worker(
    CDIstack_E,
    object_E,
    probe_E,
    it,
    N_it,
    En,
    pyStr,
    ePIEstr,
    xlist_E,
    ylist_E,
    Xw,
    Yw,
    alpha,
    beta,
    singlefloat,
    firstIG,
):
    Xsize = pyStr["arraySizeX"]
    Ysize = pyStr["arraySizeY"]
    numLayer = ePIEstr["numLayer"]
    numProbe = ePIEstr["numProbe"]

    Xa = math.floor(pyStr["prbArraySizeX"] / 2) - math.floor(Xsize / 2)
    Xb = Xa + Xsize
    Ya = math.floor(pyStr["prbArraySizeY"] / 2) - math.floor(Ysize / 2)
    Yb = Ya + Ysize

    CDIstack_E = np.fft.fftshift(CDIstack_E[:, :, Xa:Xb, Ya:Yb], axes=(2, 3))

    dataTypeC = np.complex64 if singlefloat else np.complex128

    INwave = np.zeros((numLayer, numProbe, Xsize, Ysize), dataTypeC)
    INwave_org = np.zeros((numLayer, numProbe, Xsize, Ysize), dataTypeC)
    OUTwave = np.zeros((numLayer, numProbe, Xsize, Ysize), dataTypeC)
    OUTwave_org = np.zeros((numLayer, numProbe, Xsize, Ysize), dataTypeC)

    INwave[0, 0, 0:Xsize, 0:Ysize] = probe_E[Xa:Xb, Ya:Yb]

    R_factor_E = np.zeros(N_it)

    # Begin configuration check
    if ePIEstr["IG"] == 1:
        raise RuntimeError("IG == 1 is unsupported")
    if ePIEstr["scanmode"] == 5:
        raise RuntimeError("scanmode == 5 is unsupported")
    if ePIEstr["subPixShift"]:
        raise RuntimeError("subPixShift is unsupported")
    for Ln in range(ePIEstr["numLayer"]):
        if Ln < ePIEstr["numLayer"] - 1:
            raise RuntimeError("numLayer > 1 is unsupported")
    # TODO: ISCmode is hard-coded to zero
    ISCmode = 0
    if ISCmode != 0:
        raise RuntimeError("ISCmode !=0 is unsupported")
    for Ln in range(ePIEstr["numLayer"] - 1, -1, -1):
        if Ln > 0:
            raise RuntimeError("numLayer > 1 is unsupported")
    if ePIEstr["WPOA"]:
        raise RuntimeError("WPOA is unsupported")
    # End configuration check

    _core(
        N_it,
        pyStr["xscanSize"],
        pyStr["yscanSize"],
        pyStr["resolutionX"],
        pyStr["resolutionY"],
        Xsize,
        Ysize,
        pyStr["objArraySizeX"],
        pyStr["objArraySizeY"],
        pyStr["prbArraySizeX"],
        pyStr["prbArraySizeY"],
        Xw.ve_adr,
        Yw.ve_adr,
        xlist_E.ve_adr,
        ylist_E.ve_adr,
        float(alpha[0, 0]),
        float(beta[0, 0]),
        object_E.ve_adr,
        probe_E.ve_adr,
        CDIstack_E.ve_adr,
        R_factor_E.ve_adr,
        Xa,
        Xb,
        Ya,
        Yb,
        sync=True,
    )

    return object_E, probe_E, xlist_E, ylist_E, R_factor_E
