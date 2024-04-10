from copy import deepcopy
from datetime import datetime
from pathlib import Path
import random
import sys
from typing import List, Union

from omegaconf import OmegaConf, DictConfig, ListConfig


from sumo_pipelines.config import PipelineConfig
from sumo_pipelines.optimization.config import OptimizationConfig
from sumo_pipelines.pipe_handlers import load_function


import re

# Kept outside simple_eval() just for performance
_re_simple_eval = re.compile(rb"d([\x00-\xFF]+)S\x00")


def simple_eval(expr):
    try:
        c = compile(expr, "userinput", "eval")
    except SyntaxError as e:
        raise ValueError(f"Malformed expression: {expr}") from e
    m = _re_simple_eval.fullmatch(c.co_code)
    if not m:
        raise ValueError(f"Not a simple algebraic expression: {expr}")
    try:
        return c.co_consts[int.from_bytes(m.group(1), sys.byteorder)]
    except IndexError as exc:
        raise ValueError(f"Expression not evaluated as constant: {expr}") from exc


def update_parent_from_yaml(p, *, _parent_: DictConfig):
    c = OmegaConf.load(p)
    _parent_.update(c)

    # specian key to load a yaml
    del _parent_["yaml"]

def standard_conf(p: str, *,  _parent_: DictConfig):
    # get the path to the standard config
    root = Path(__file__).parent.parent

    # split the dot path
    file_path = "/".join(p.split(".")) + ".yaml"

    path = (root / 'configurations' / 'standard' ).joinpath(file_path)

    c = OmegaConf.load(path)    

    # pop the top level
    _parent_.config = c[list(c.keys())[0]]


def create_custom_resolvers():
    try:
        OmegaConf.register_new_resolver(
            "import", lambda x: load_function(x), use_cache=True
        )
        OmegaConf.register_new_resolver(
            "datetime.now",
            lambda x: datetime.now().strftime(x or "%m.%d.%Y_%H.%M.%S"),
            use_cache=True,
        )
        OmegaConf.register_new_resolver(
            "datetime.parse", lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
        )

        OmegaConf.register_new_resolver(
            "randint",
            lambda x, y: random.randint(x, y),
            use_cache=True,
        )

        OmegaConf.register_new_resolver(
            "uniform",
            lambda x, y: random.uniform(x, y),
            use_cache=True,
        )

        OmegaConf.register_new_resolver(
            "math",
            lambda x: simple_eval(x),  # this is dangerous. How to make it safe?
        )

        OmegaConf.register_new_resolver(
            "call",
            lambda f, *x: f(*x),
        )

        OmegaConf.register_new_resolver(
            "int",
            lambda x: int(x),
        )

        OmegaConf.register_new_resolver(
            "standard_conf",
            standard_conf,
            # use_cache=True
        )

    except Exception as e:
        if "already registered" in str(e):
            pass
        else:
            raise e


def to_yaml(
    path: Path, config: Union[PipelineConfig, OptimizationConfig], resolve: bool
) -> None:
    """Save a config file"""
    write_config = OmegaConf.to_container(deepcopy(config), resolve=resolve)
    with open(path, "w") as f:
        # check if the dataclass field are None
        keys = list(write_config["Blocks"].keys())
        for k in keys:
            if write_config["Blocks"].get(k, None) is None:
                del write_config["Blocks"][k]

        f.write(OmegaConf.to_yaml(OmegaConf.create(write_config), resolve=resolve))


def open_config(
    path: Path,
    structured: OmegaConf = None,
) -> Union[PipelineConfig, OptimizationConfig]:
    """Open a config file and return a DictConfig object"""
    create_custom_resolvers()

    # time_ = datetime.now().strftime("%m.%d.%Y_%H.%M.%S")

    s = OmegaConf.structured(PipelineConfig) if structured is None else structured
    c = OmegaConf.load(
        path,
    )

    merged = OmegaConf.merge(s, c)

    # handle the output directory
    # merged.Metadata.output = str(Path(merged.Metadata.output).joinpath(time_))
    # create the output directory
    Path(merged.Metadata.output).mkdir(parents=True, exist_ok=True)
    # save the config file at the top level. Don't resolve the config file
    to_yaml(Path(merged.Metadata.output).joinpath("config.yaml"), merged, False)

    print("Config file saved at: ", merged.Metadata.output)

    return merged


def open_completed_config(
    path: Path, validate: bool = True
) -> Union[PipelineConfig, OptimizationConfig]:
    """Open a config file and return a DictConfig object"""
    try:
        create_custom_resolvers()
    except Exception:
        pass

    with open(path, "r") as f:
        c = OmegaConf.load(
            f,
        )
    if not validate:
        return c

    s = OmegaConf.structured(PipelineConfig)
    return OmegaConf.merge(s, c)


def resolve_yaml_imports(
    cfg: DictConfig,
):
    # if OmegaConf.has_resolver(cfg, "yaml.update"):
    try:
        OmegaConf.resolve(cfg)
    except Exception:
        pass


def walk_config(cfg: DictConfig, func):
    """Walk the config and apply a function to each node"""
    if isinstance(cfg, DictConfig):
        for k in cfg.keys():
            try:
                walk_config(cfg[k], func)
            except Exception:
                pass
    elif isinstance(cfg, ListConfig):
        for i in range(len(cfg)):
            try:
                walk_config(cfg[i], func)
            except Exception:
                pass
    else:
        func(cfg)


def open_config_structured(
    path: Union[Path, List[Path]],
    resolve_output: bool = False,
) -> Union[PipelineConfig, OptimizationConfig]:
    """
    Open a config file and return the underlying dataclass representation.

    This allows for the config to contain functions
    """

    try:
        OmegaConf.register_new_resolver(
            "yaml.update",
            update_parent_from_yaml,
        )

    except Exception as e:
        if "already registered" not in str(e):
            raise e

    if isinstance(path, list):
        all_confs = [OmegaConf.load(p) for p in path]
        # special merge behavior for Blocks.SimulationConfig.addiational_files & Blocks.SimulationConfig.additional_sim_params
        all_additional_files = []
        additional_sim_params = []
        for conf in all_confs:
            if conf.get("Blocks", {}).get("SimulationConfig", None) is not None:
                # this is some tom fuckery to get the additional files
                if (
                    conf.Blocks.SimulationConfig.get("additional_files", None)
                    is not None
                ):
                    all_additional_files.extend(
                        list(
                            map(
                                str,
                                conf.Blocks.SimulationConfig._get_node(
                                    "additional_files", validate_access=False
                                )._content,
                            )
                        )
                    )
                if (
                    conf.Blocks.SimulationConfig.get("additional_sim_params", None)
                    is not None
                ):
                    additional_sim_params.extend(
                        list(
                            map(
                                str,
                                conf.Blocks.SimulationConfig._get_node(
                                    "additional_sim_params", validate_access=False
                                )._content,
                            )
                        )
                    )
        # reduce but keep the order
        additional_sim_params = list(dict.fromkeys(additional_sim_params))
        all_additional_files = list(dict.fromkeys(all_additional_files))

        # merge the configs
        c = OmegaConf.merge(*all_confs)

        if len(all_additional_files) > 0:
            c.Blocks.SimulationConfig.additional_files = all_additional_files
        if len(additional_sim_params) > 0:
            c.Blocks.SimulationConfig.additional_sim_params = additional_sim_params
    else:
        c = OmegaConf.load(
            path,
        )

    random.seed(c.Metadata.random_seed)

    # resolve what I can
    walk_config(c, resolve_yaml_imports)

    # register the other resolvers
    create_custom_resolvers()

    if c.get("Optimization", None) is not None:
        s = OmegaConf.structured(OptimizationConfig)
    else:
        s = OmegaConf.structured(
            PipelineConfig,
        )
    # merge the structured config with the loaded config
    try:
        c = OmegaConf.merge(s, c)
    except Exception as e:
        # try to merge the sub configs at this point
        from sumo_pipelines.config import Pipeline, Blocks, MetaData

        for k in c.keys():
            if k in ["Pipeline", "Blocks", "MetaData"]:
                try:
                    c[k] = OmegaConf.merge(
                        OmegaConf.structured(
                            eval(k),
                        ),
                        c[k],
                    )
                except Exception as e:
                    print("Failed to merge: ", k, ". Continiung...")



    # if resolve metadata
    if resolve_output:
        c.Metadata.output = str(c.Metadata.output)

    return c
