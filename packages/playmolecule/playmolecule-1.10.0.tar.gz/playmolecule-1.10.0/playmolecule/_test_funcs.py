from pathlib import Path


def _test_func(
    outdir: Path,
    pdb: Path,
    simtime: float = 0.5,
    equiltimes: list[float] = None,
    randomize: list[bool] = [True],
    no_prep: bool = False,
    forcefield: str = "CHARMM",
    **kwargs,
):
    """TestFunc

    Test function

    Parameters
    ----------
    outdir : Path
        Output directory
    pdb : Path
        Input file
    simtime : float
        Simulation time
    equiltimes : list[float]
        List of equilibration times
    randomize : list[bool]
        List of booleans
    no_prep : bool
        No preparation
    forcefield : str, choices=("CHARMM", "AMBER")
        The simulation forcefield
    """
    print("Running test function with args:", locals())
