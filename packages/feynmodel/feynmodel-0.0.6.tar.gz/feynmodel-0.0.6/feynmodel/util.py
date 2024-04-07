from particle import PDGID, Particle
from particle.converters.bimap import DirectionalMaps

PDG2LaTeXNameMap, LaTeX2PDGNameMap = DirectionalMaps(
    "PDGID", "LaTexName", converters=(PDGID, str)
)

PDG2Name2IDMap, PDGID2NameMap = DirectionalMaps(
    "PDGName", "PDGID", converters=(str, PDGID)
)


def get_name(pid: int, fallback_name=None) -> str:
    """
    Get programmatic name of a particle.

    Args:
        pid (int) : PDG Monte Carlo identifier for the particle.

    Returns:
        str: programmatic name.

    Examples:
        >>> get_name(21)
        'g'
    """
    try:
        p = Particle.from_pdgid(pid)
        return p.programmatic_name
    except Exception as e:
        if fallback_name is not None:
            return fallback_name
        raise e
