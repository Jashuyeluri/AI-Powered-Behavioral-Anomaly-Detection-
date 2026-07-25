# AI-Powered Behavioral Anomaly Detection for Cybersecurity

A machine learning system that models "normal" access and connection behaviour for users, service accounts, and devices, detects intrusions or compromised-credential activity in near real-time, and classifies the anomaly type — with an explainable risk score for SOC analysts.

## 🔗 Live Demo

**[Try the dashboard here](https://jashuyeluri-ai-powered-behavioral-anomaly-detection--app-bp90fn.streamlit.app/)**

*Note: the app may take ~20-30 seconds to wake up if it's been idle.*

## Problem

Traditional signature-based security fails against novel, slow, or low-and-slow intrusions. Every login, API call, or device connection leaves a behavioural trail — timing, location, access patterns, command sequences — that rule-based systems ignore. This project takes a behavioural anomaly detection approach instead: learn what "normal" looks like per entity, then flag deviations from that baseline.

## What it does

- **Synthetic data generator** — simulates realistic access-log sessions with 8 injected attack patterns (brute force, credential stuffing, lateral movement, impossible travel, device spoofing, low-and-slow exfiltration, insider drift) plus normal baseline traffic
- **Baseline profiling** — per-entity statistical behaviour models, with peer-group fallback for cold-start entities with no history
- **Detection model** — Isolation Forest scoring each session against engineered behavioural features (geo-velocity, hour deviation, resource novelty, auth failures)
- **Anomaly classification** — Random Forest predicts the specific attack category a flagged session resembles, not just "anomalous"
- **Explainability layer** — every alert includes a plain-language explanation (e.g. *"Flagged due to unfamiliar geo-location + new device fingerprint"*)
- **Analyst dashboard** — Streamlit app with a ranked alert queue, entity history lookup, live risk-score trend charts, and a simulated real-time streaming mode

## Tech stack

Python · pandas · NumPy · scikit-learn (Isolation Forest, Random Forest) · Streamlit · Faker

## Results

| Metric | Score |
|---|---|
| ROC-AUC | 0.999 |
| Precision @ top 1% alert budget | 100% |
| Anomaly type classification accuracy | 95% |

## Known limitations

- `device_spoofing` had only 4 injected sessions — too few for reliable classifier metrics at this scale
- Detection uses engineered features rather than true sequence modeling; an LSTM/GRU autoencoder would better capture temporal order for subtler attacks
- Cold-start peer-group fallback is implemented but not exercised in this synthetic run, since every entity had some session history
- Live feed is a simulated replay of historical data; production deployment would use a real streaming pipeline (Kafka/Kinesis) for live ingestion

## Run locally

```bash
git clone https://github.com/Jashuyeluri/AI-Powered-Behavioral-Anomaly-Detection-.git
cd AI-Powered-Behavioral-Anomaly-Detection-
pip install -r requirements.txt
streamlit run app.py
```

## Author

**Yeluri Venkata Jaswanth Kumar**
Vellore Institute of Technology, Amaravati
