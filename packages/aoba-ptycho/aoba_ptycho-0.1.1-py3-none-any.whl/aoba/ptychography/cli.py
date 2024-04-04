from argparse import ArgumentParser
from pprint import pprint

import nlcpy as np
import hdf5storage
import h5py
from pytictoc import TicToc
import matplotlib.pyplot as plt

from . import __version__
from .epie import ePIE_worker

# Raster scan wave
def raster_scan(Xsize, Ysize):
    Xw = np.zeros((8, Xsize * Ysize), dtype="int32")
    Yw = np.zeros((8, Xsize * Ysize), dtype="int32")

    n = 0
    for k in range(Ysize):
        for m in range(Xsize):
            Xw[0, n] = m
            Yw[0, n] = k
            Xw[1, n] = Xsize - m - 1
            Yw[1, n] = Ysize - k - 1
            Xw[4, n] = m
            Yw[4, n] = Ysize - k - 1
            Xw[5, n] = Xsize - m - 1
            Yw[5, n] = k
            n = n + 1

    n = 0
    for m in range(Xsize):
        for k in range(Ysize):
            Xw[2, n] = m
            Yw[2, n] = k
            Xw[3, n] = Xsize - m - 1
            Yw[3, n] = Ysize - k - 1
            Xw[6, n] = m
            Yw[6, n] = Ysize - k - 1
            Xw[7, n] = Xsize - m - 1
            Yw[7, n] = k
            n = n + 1

    return Xw, Yw


def generate_plots(object_E, R_factor_E):
    plt.figure(figsize=(8, 8))
    plt.imshow(np.angle(object_E))
    plt.colorbar()
    plt.savefig("object.png")

    plt.figure(figsize=(8, 6))
    plt.plot(R_factor_E)
    plt.xlabel("Iterations")
    plt.ylabel("Rfactor")
    plt.savefig("r_factor.png")


def main():
    parser = ArgumentParser(
        prog="aoba-ptycho", description="Ptychography tool for AOBA"
    )
    parser.add_argument("input", help="Input MATLAB file (v7.3)")
    parser.add_argument("output", help="Output MATLAB file (v7.3)")
    parser.add_argument("--iter", help="override number of ePIE iterations")
    parser.add_argument("--plot", action="store_true", help="generate plots")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    t = TicToc()

    input = h5py.File(args.input, "r")

    t.tic()
    CDIstack = np.array(input["CDIstack"][:])
    t.toc("Read CDIstack in")

    t.tic()
    object_ini = np.array(input["object_ini"][:].view(np.complex128))
    t.toc("Read object_ini in")

    t.tic()
    probe_ini = np.array(input["probe_ini"][:].view(np.complex128))
    t.toc("Read probe_ini in")

    object = object_ini
    probe = probe_ini
    it = int(input["it"][()])

    pyStr = {
        "Energy": np.array(input["pyStr"]["Energy"]),
        "xscanSize": int(input["pyStr"]["xscanSize"][()]),
        "yscanSize": int(input["pyStr"]["yscanSize"][()]),
        "xscanOffset": int(input["pyStr"]["xscanOffset"][()]),
        "yscanOffset": int(input["pyStr"]["yscanOffset"][()]),
        "xList": np.array(input["pyStr"]["xList"]),
        "yList": np.array(input["pyStr"]["yList"]),
        "arraySizeX": int(input["pyStr"]["arraySizeX"][()]),
        "arraySizeY": int(input["pyStr"]["arraySizeY"][()]),
        "prbArraySizeX": int(input["pyStr"]["prbArraySizeX"][()]),
        "prbArraySizeY": int(input["pyStr"]["prbArraySizeY"][()]),
        "objArraySizeX": int(input["pyStr"]["objArraySizeX"][()]),
        "objArraySizeY": int(input["pyStr"]["objArraySizeY"][()]),
        "resolutionX": input["pyStr"]["resolutionX"][()],
        "resolutionY": input["pyStr"]["resolutionY"][()],
    }

    # ePIE/3PIE condition
    if "ePIEstr" not in input:
        ePIEstr = {
            "IterN": 1000,
            "paraIterN": 50,
            "numProbe": 1,
            "numLayer": 1,
            "dL": np.array([2.570]),
            "alpha": np.array([1]),  # update factor of object function
            "beta": np.array([0.1, 0.1]),  # update factor of probe fruction
            "Eoffset": 0,
            "Esize": pyStr["Energy"].shape[0],
            "probeDiagFreq": np.array([50, 0]),
            "probeNormFreq": np.array([100, 0]),
            "KKRfreq": np.array([100, 100, 100]),  # [freq,offset_It,start_It]
            "dE": 0.1,
            "Eext": 10,
            "xyShiftCorrFreq": np.array([200, 200]),
            "phaseOnlyShiftCorrFreq": np.array([50, 50]),
            "refEn": 10,  # ref En of phase only shift correction
            "maskSize": 400,
            # raster:1, snake:2, swirl from outside: 3, swirl from inside:4
            "scanmode": 3,
            # calculate R-factor 1:on, 0:off
            "calcRfactor": 1,
            "calcRfactorFreq": 50,
            # sub-pixel shift 1:on, 0:off
            "subPixShift": 0,
            # weak phase object approximation
            "WPOA": 0,
        }
    else:
        ePIEstr = {
            "IterN": int(input["ePIEstr"]["IterN"][()]),
            "paraIterN": int(input["ePIEstr"]["paraIterN"][()]),
            "numProbe": int(input["ePIEstr"]["numProbe"][()]),
            "numLayer": int(input["ePIEstr"]["numLayer"][()]),
            "dL": np.array(input["ePIEstr"]["dL"]),
            "alpha": np.array(
                input["ePIEstr"]["alpha"]
            ),  # update factor of object function
            "beta": np.array(
                input["ePIEstr"]["beta"]
            ),  # update factor of probe fruction
            "Eoffset": int(input["ePIEstr"]["Eoffset"][()]),
            "Esize": pyStr["Energy"].shape[0],
            "probeDiagFreq": np.array(input["ePIEstr"]["probeDiagFreq"]),
            "probeNormFreq": np.array(input["ePIEstr"]["probeNormFreq"], dtype=int),
            "KKRfreq": np.array(np.array(input["ePIEstr"]["KKRfreq"]), dtype=int),
            "dE": input["ePIEstr"]["dE"][()],
            "Eext": input["ePIEstr"]["Eext"][()],
            "xyShiftCorrFreq": np.array(input["ePIEstr"]["xyShiftCorrFreq"], dtype=int),
            "phaseOnlyShiftCorrFreq": np.array(
                input["ePIEstr"]["phaseOnlyShiftCorrFreq"], dtype=int
            ),
            "refEn": input["ePIEstr"]["refEn"][
                ()
            ],  # ref En of phase only shift correction
            "maskSize": input["ePIEstr"]["maskSize"][()],
            # raster:1, snake:2, swirl from outside: 3, swirl from inside:4
            "scanmode": int(input["ePIEstr"]["scanmode"][()]),
            # calculate R-factor 1:on, 0:off
            "calcRfactor": int(input["ePIEstr"]["calcRfactor"][()]),
            "calcRfactorFreq": int(input["ePIEstr"]["calcRfactorFreq"][()]),
            # sub-pixel shift 1:on, 0:off
            "subPixShift": int(input["ePIEstr"]["subPixShift"][()]),
            # weak phase object approximation
            "WPOA": input["ePIEstr"]["WPOA"][()],
        }

    if "ePIEstr" not in input:
        ePIEstr["IG"] = 0
        ePIEstr["IGlambda"] = 0.01
        ePIEstr["IGiterN"] = 1
    else:
        if "IG" not in input["ePIEstr"]:
            ePIEstr["IG"] = 0
        else:
            ePIEstr["IG"] = int(input["ePIEstr"]["IG"][()])
        if "IGlambda" not in input["ePIEstr"]:
            ePIEstr["IGlambda"] = 0.01
        else:
            ePIEstr["IGlambda"] = input["ePIEstr"]["IGlambda"][()]
        if "IGiterN" not in input["ePIEstr"]:
            ePIEstr["IGiterN"] = 1
        else:
            ePIEstr["IGiterN"] = input["ePIEstr"]["IGiterN"][()]

    # set alpha/beta
    if ePIEstr["alpha"].shape[0] != ePIEstr["numLayer"]:
        raise RuntimeError("size(alpha) != numLayer  is unsupported")
    else:
        alpha = ePIEstr["alpha"]

    if ePIEstr["beta"].shape[0] != ePIEstr["numLayer"]:
        raise RuntimeError("size(beta) != numLayer  is unsupported")
    else:
        beta = ePIEstr["beta"]

    # scanmode
    if ePIEstr["scanmode"] == 1:
        Xw, Yw = raster_scan(pyStr["xscanSize"], pyStr["yscanSize"])
    else:
        raise RuntimeError("scanmode != 1 is unsupported")

    singlefloat = 0

    if ePIEstr["calcRfactor"]:
        raise RuntimeError("calcRfactor is unsupported")

    if args.iter:
        ePIEstr["IterN"] = int(args.iter)

    np.set_printoptions(threshold=10)
    pprint(ePIEstr)
    pprint(pyStr)

    tstart = t.tic()
    for it1 in range(1, ePIEstr["IterN"], ePIEstr["paraIterN"] + 1):
        # probe peak shift correction
        if (
            it % ePIEstr["xyShiftCorrFreq"][0, 0] == ePIEstr["xyShiftCorrFreq"][1, 0]
            and it > 0
        ):
            raise RuntimeError("Probe peak shift correction is unsupported")

        # phase only shift correction
        if (
            ePIEstr["Esize"] > 1
            and it % ePIEstr["phaseOnlyShiftCorrFreq"][0, 0]
            == ePIEstr["phaseOnlyShiftCorrFreq"][1, 0]
            and it > 0
        ):
            raise RuntimeError("Phase only shift correction is unsupported")
        else:
            posCorr = 0

        if (
            ePIEstr["Esize"] > 1
            and it % ePIEstr["KKRfreq"][0, 0] == ePIEstr["KKRfreq"][1, 0]
            and it > ePIEstr["KKRfreq"][2, 0]
            and it > 0
        ):
            raise RuntimeError("KKR constraint is unsupported")
        else:
            firstIG = 0

        if ePIEstr["Esize"] > 1 and ePIEstr["IG"] == 2 and it > 0:
            raise RuntimeError("IG correction is unsupported")

        N_it = min((ePIEstr["IterN"] - it1 + 1), ePIEstr["paraIterN"])
        for En in range(ePIEstr["Eoffset"], ePIEstr["Eoffset"] + ePIEstr["Esize"]):
            if En > 1:
                raise RuntimeError("En > 1 is unsupported")
            CDIstack_E = CDIstack[
                pyStr["yscanOffset"] : pyStr["yscanSize"],
                pyStr["xscanOffset"] : pyStr["xscanSize"],
                :,
                :,
            ]
            object_E = object
            probe_E = probe
            xlist_E = pyStr["xList"]
            ylist_E = pyStr["yList"]
            object_E, probe_E, xlist_E, ylist_E, R_factor_E = ePIE_worker(
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
            )
            # TODO: Now "foo_E"'s are so called pointers and energy levels are only one (En=0).
            # So, copy-back is not necessary.
            # object[En,:,:] = object_E
            # probe[En,:,:] = probe_E
            # pyStr['xList'][En,:,:] = xlist_E
            # pyStr['yList'][En,:,:] = ylist_E
            if ePIEstr["calcRfactor"]:
                raise RuntimeError("calcRfactor is unsupported")

        it = it + N_it
        # post process
        # probe diagonize
        if (
            ePIEstr["numProbe"] > 1
            and it % ePIEstr["probeDiagFreq"][0, 0] == ePIEstr["probeDiagFreq"][1, 0]
            and it > 0
        ):
            raise RuntimeError("Probe diagonalization is unsupported")

        # probe normalization
        if (
            it % ePIEstr["probeNormFreq"][0, 0] == ePIEstr["probeNormFreq"][1, 0]
            and it > 0
        ):
            raise RuntimeError("Probe normalization is unsupported")

        if ePIEstr["IG"] >= 1 or posCorr == 1:
            raise RuntimeError("IG correction is unsupported")

        if ePIEstr["calcRfactor"] and it % ePIEstr["calcRfactorFreq"] == 1:
            raise RuntimeError("calcRfactor is unsupported")

        t.toc("Executed ePIE algorithm in")

    if ePIEstr["calcRfactor"]:
        raise RuntimeError("calcRfactor is unsupported")

    t.tic()
    hdf5storage.savemat(
        args.output,
        {"object": object_E.get(), "R_factor": R_factor_E.get()},
        format="7.3",
    )
    t.toc("Wrote output in")

    if args.plot:
        generate_plots(object_E, R_factor_E)


if __name__ == "__main__":
    main()
