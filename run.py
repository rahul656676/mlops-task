import argparse
import json
import logging
import os
import sys
import time

import numpy as np
import pandas as pd
import yaml


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def write_error_metrics(output_path, version, error_message):
    metrics = {
        "version": version,
        "status": "error",
        "error_message": error_message,
    }

    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))


def validate_config(config):
    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()

    version = "unknown"

    setup_logging(args.log_file)

    start_time = time.time()

    logging.info("Job started")

    try:
        if not os.path.exists(args.config):
            raise FileNotFoundError("Config file not found")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Invalid config structure")

        validate_config(config)

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)

        logging.info(
            f"Config validated | seed={seed}, window={window}, version={version}"
        )

        if not os.path.exists(args.input):
            raise FileNotFoundError("Input CSV file not found")

        try:
            df = pd.read_csv(args.input)
        except Exception:
            raise ValueError("Invalid CSV format")

        if df.empty:
            raise ValueError("CSV file is empty")

        if "close" not in df.columns:
            raise ValueError("Missing required column: close")

        logging.info(f"Rows loaded: {len(df)}")

        logging.info("Computing rolling mean")

        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        logging.info("Generating signals")

        df["signal"] = np.where(
            df["close"] > df["rolling_mean"],
            1,
            0,
        )

        signal_rate = float(df["signal"].mean())

        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": int(len(df)),
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success",
        }

        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=2)

        logging.info(f"Metrics summary: {metrics}")
        logging.info("Job completed successfully")

        print(json.dumps(metrics, indent=2))

    except Exception as e:
        logging.exception("Job failed")

        write_error_metrics(
            args.output,
            version,
            str(e),
        )

        sys.exit(1)


if __name__ == "__main__":
    main()