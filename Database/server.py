"""
truongle - Mar 29, 2023
truonglm.spk@gmail.com
gunicorn 'server:main("hydra.verbose=True")'\
  --bind 0.0.0.0:8030\
  --workers 1 --worker-class uvicorn.workers.UvicornWorker
"""
import os
from app import create_app
from hydra.core.hydra_config import HydraConfig
from hydra.core.utils import configure_log
from hydra import compose, initialize


def main(args=None):
    overrides = args.split(" ") if args is not None else []
    # Cfg app
    print("overrides: ", overrides)
    initialize(config_path="cfg", version_base="1.2")
    cfg = compose(config_name="config", return_hydra_config=True, overrides=overrides)
    HydraConfig.instance().set_config(cfg)
    run_dir = HydraConfig.get().run.dir
    os.makedirs(run_dir, exist_ok=True)
    configure_log(cfg.hydra.job_logging, cfg.hydra.verbose)

    app = create_app(cfg.data_api)
    return app
