import importlib
import os
import sys

from feynmodel.coupling import Coupling
from feynmodel.coupling_order import CouplingOrder
from feynmodel.decay import Decay
from feynmodel.feyn_model import FeynModel
from feynmodel.function import Function
from feynmodel.lorentz import Lorentz
from feynmodel.parameter import Parameter
from feynmodel.particle import Particle
from feynmodel.ufo_base_class import UFOBaseClass
from feynmodel.vertex import Vertex


def ufo_to_fm_particle(ufo_object, model):
    return model.get_particle(name=ufo_object.name, pdg_code=ufo_object.pdg_code)


def ufo_to_fm_parameter(ufo_object, model):
    return model.get_parameter(name=ufo_object.name)


def ufo_to_fm_lorentz(ufo_object, model):
    return model.get_lorentz(name=ufo_object.name)


def ufo_to_fm_couplings(ufo_object, model):
    return model.get_coupling(name=ufo_object.name)


def ufo_object_to_dict(ufo_object, model=None):
    """Convert an UFO object to a dictionary"""
    if isinstance(ufo_object, UFOBaseClass):
        # We have to replace all instances of the UFO particle class with the FeynModel particle class

        # Fix particle
        if "mass" in ufo_object.require_args:
            ufo_object.mass = ufo_to_fm_parameter(ufo_object.mass, model)
        if "width" in ufo_object.require_args:
            ufo_object.width = ufo_to_fm_parameter(ufo_object.width, model)

        # Fix vertex
        if "particles" in ufo_object.require_args:
            np = [ufo_to_fm_particle(p, model) for p in ufo_object.particles]
            ufo_object.particles = np
        # Fix decay
        if "lorentz" in ufo_object.require_args:  # ufo_object.__dict__:
            ufo_object.lorentz = ufo_to_fm_lorentz(ufo_object.lorentz, model)
        if "couplings" in ufo_object.require_args:  # ufo_object.__dict__:
            for k, v in ufo_object.partial_widths.items():
                ufo_object.couplings[k] = ufo_to_fm_couplings(v, model)
        # Fix decay
        if "particle" in ufo_object.require_args:  # ufo_object.__dict__:
            ufo_object.particle = ufo_to_fm_particle(ufo_object.particle, model)
        if "partial_widths" in ufo_object.require_args:  # ufo_object.__dict__:
            for k, v in ufo_object.partial_widths.items():
                ufo_object.partial_widths[
                    (ufo_to_fm_particle(k[0], model), ufo_to_fm_particle(k[2], model))
                ] = v
        return {key: ufo_object.__dict__[key] for key in ufo_object.require_args}
    else:
        return ufo_object.__dict__

    # return ufo_object.__dict__


def import_ufo_model(model_path, model_name="imported_ufo_model"):
    # Add the model path to the PYTHONPATH
    # This fixes the imports in the UFO model
    sys.path.append(os.path.abspath(model_path))
    # Madgraph workaround
    # os.environ["PYTHONPATH"] += os.pathsep + os.path.dirname(model_path)
    # Load the UFO model
    spec = importlib.util.spec_from_file_location(
        model_name, os.path.abspath(model_path) + "/" + "__init__.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    model = module
    return model


def ufo_to_feynmodel(model, model_object=None, model_class=FeynModel):
    # Convert the UFO model to a FeynModel object
    if model_object is not None:
        if not isinstance(model_object, model_class):
            raise ValueError(
                f"model_object must be a {model_class} object. Use general FeynModel in case of doubt."
            )
        feynmodel = model_object
    elif model_class is not None:
        feynmodel = model_class()
    else:
        raise ValueError("model_object or model_class must be specified")

    # Dict all_names to feynmodel objects
    # Ordered by depencencym for replacing the UFO objects with the FeynModel objects
    mapped_names = {
        "all_lorentz": Lorentz,
        "all_couplings": Coupling,
        "all_orders": CouplingOrder,
        "all_functions": Function,
        "all_parameters": Parameter,
        "all_particles": Particle,
        "all_decays": Decay,
        "all_vertices": Vertex,
    }

    for name, cls in mapped_names.items():
        if hasattr(model, name):
            for ufo_object in getattr(model, name):
                # print(f"Adding {ufo_object} to {feynmodel} as {cls}")
                feynmodel.add_object(
                    cls(**ufo_object_to_dict(ufo_object, model=feynmodel))
                )
    return feynmodel


# Load a UFO model and convert it to a FeynModel object
def load_ufo_model(model_path, model_name="imported_ufo_model", model_class=FeynModel):
    """Load a UFO model and convert it to a FeynModel object"""
    # check if model_path is a directory
    model = None
    if os.path.isdir(model_path):
        model = import_ufo_model(model_path, model_name)
    else:
        # Test if a modulename is passed like ufo_sm or ufo_mssm
        try:
            model = importlib.import_module(model_path)
        except ImportError:
            raise ValueError(
                f"Could not load UFO model from {model_path}. Make sure the path is correct."
            )
    return ufo_to_feynmodel(model, model_class=model_class)
