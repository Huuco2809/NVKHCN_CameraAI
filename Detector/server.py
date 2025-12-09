"""
truongle - Mar 29, 2023
python3.10 server.py hydra.job.chdir=True hydra.verbose=True
"""
import os
import sys
import uvicorn
from app import create_app
from hydra.core.hydra_config import HydraConfig
from hydra.core.utils import configure_log
from hydra import compose, initialize

# Cfg app
initialize(config_path="cfg", version_base="1.2")
cfg = compose(config_name="config", return_hydra_config=True, overrides=sys.argv[1:])
HydraConfig.instance().set_config(cfg)
run_dir = HydraConfig.get().run.dir
os.makedirs(run_dir, exist_ok=True)
configure_log(cfg.hydra.job_logging, cfg.hydra.verbose)

app = create_app(cfg)


if __name__ == '__main__':
    uvi_log_config = uvicorn.config.LOGGING_CONFIG
    uvi_log_config["formatters"]["access"]["fmt"] = '%(asctime)s %(name)-25s %(levelname)-8s - %(message)s'

    uvicorn.run(
        "__main__:app",
        host=cfg.server.host,
        port=cfg.server.port,
        workers=cfg.server.workers,
        root_path=cfg.server.root_path,
        log_config=uvi_log_config,
    )

