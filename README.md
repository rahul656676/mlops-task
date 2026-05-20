# MLOps Technical Assessment

## Local Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Docker Build

```bash
docker build -t mlops-task .
```

## Docker Run

```bash
docker run --rm mlops-task
```

## Example metrics.json

```json
{
  "version": "v1",
  "rows_processed": 6,
  "metric": "signal_rate",
  "value": 0.3333,
  "latency_ms": 12,
  "seed": 42,
  "status": "success"
}
```
