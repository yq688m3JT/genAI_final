# Project Plan: SynthAML

## 1. Project Title
**SynthAML**: Cross-Border AML "Zero-Day Typology" Synthetic Transaction Data Generation Engine

## 2. Target User, Workflow, and Business Value
*   **Target User:** Anti-Money Laundering (AML) algorithm engineers and compliance data scientists at cross-border payment firms (e.g., Airwallex, Payoneer) or mid-sized multinational banks.
*   **Workflow:** 
    1.  **Start:** User uploads a "New Typology Warning Report" (PDF) from regulatory bodies like FATF (e.g., "Using shell companies to launder money via fake solar panel exports").
    2.  **Process:** The system automatically extracts complex criminal logic and features from the text.
    3.  **End:** The system generates 10,000 structured, highly realistic synthetic transaction records (including SWIFT narratives, amounts, and temporal spacing) to be used for fine-tuning existing risk models (e.g., XGBoost or Graph Neural Networks).
*   **Business Value:** Addresses the "Zero-Day" gap in AML. When a new laundering method is discovered, banks have no historical data to train models. Waiting for real cases to occur takes months, exposing banks to massive fines. SynthAML reduces this defensive lag from months to days.

## 3. Problem Statement and GenAI Fit
*   **Problem Statement:** Existing risk detection models suffer from a "cold start" problem when facing novel financial crime patterns due to a total lack of negative samples.
*   **GenAI Fit:** 
    *   **Contextual Translation:** Traditional algorithms cannot "read" a PDF story. GenAI possesses the deep world knowledge and reasoning required to translate natural language rules into complex, multi-node business data flows.
    *   **Reasoning:** Only GenAI can maintain the logical consistency of a multi-step money laundering chain while simulating realistic noise.
*   **Why a simpler tool fails:** Manual data synthesis by experts is slow and cannot maintain mathematical consistency (e.g., FX rates, fees) at scale. Simple rule-based generators produce "perfect" patterns that are too easy for models to learn, failing to simulate the stealthiness of real fraud.

## 4. Planned System Design and Baseline
*   **System Design:** A lightweight web dashboard where users upload reports and configure generation parameters (e.g., "Complexity Level").
*   **Course Concepts Integrated:**
    *   **RAG (Retrieval-Augmented Generation):** The system chunks and embeds the uploaded PDF. During generation, the agent retrieves specific constraints (e.g., "Funds are typically split and sent on Friday afternoons") to ensure the synthetic data strictly matches the latest typology.
    *   **Multi-step/Multi-agent Orchestration:** A dual-agent architecture. **Agent A (Noise Generator)** simulates legitimate e-commerce traffic, while **Agent B (Signal Generator)** acts as the laundering syndicate, strategically splitting and injecting illicit funds into the legitimate stream based on RAG insights.
*   **Baseline Comparison:** We will compare SynthAML's data against "Rule-based Synthetic Data" (e.g., simple IF-THEN logic based on amount thresholds). We will measure the F1-Score of an Isolation Forest model trained on both datasets when tested against a hidden ground-truth set.
*   **App Experience:** A "Data Factory" UI showing real-time logs of the "Synthetic Crime Network" construction, statistical distribution charts, and a one-click CSV export.

## 5. Evaluation Plan
*   **Success Metrics:** 
    1.  **Downstream Model Uplift:** The increase in Recall for a traditional ML model when fine-tuned with synthetic data compared to being trained on legitimate data only.
    2.  **Data Realism:** Statistical tests (e.g., Benford's Law for amounts) to ensure synthetic data mimics real-world financial distributions.
*   **Test Set:** A manually curated "Ground Truth" set of 100 entities and 500 transactions containing 5 hidden novel laundering networks to test the detection capabilities of the baseline vs. the system.

## 6. Example Inputs and Failure Cases
*   **Example Inputs:**
    1.  *Input:* FATF report on "Money Laundering through Virtual Assets and Online Gaming."
    2.  *Expected Output:* Transactions showing frequent small-value "top-ups" followed by late-night consolidations into offshore accounts.
*   **Failure Cases:**
    1.  **Violation of Conservation of Funds:** The model might generate a chain where an account sends more money than it received (requires a post-processing logic layer).
    2.  **Over-regularization:** Laundering patterns that are too precise (e.g., exactly $10,000 every time), which leads to overfitting and poor generalization in the real world.

## 7. Risks and Governance
*   **Risks:** Generated typologies could theoretically be reversed to "teach" actual criminals how to avoid detection.
*   **Governance:** 
    *   **Deployment:** Strictly intended for on-premise/VPC deployment for licensed financial institutions only.
    *   **Privacy:** High privacy compliance; as the data is entirely synthetic, it contains no real customer PII (Personally Identifiable Information).
    *   **Human-in-the-loop:** Compliance experts must review a sample of the generated logic before full-scale export.

## 8. Plan for the Week 6 Check-in
*   **Working App:** A functional UI that accepts text prompts and uses Structured Outputs to generate 50 logically coherent SWIFT transaction records.
*   **Evaluation:** A Python script to validate basic financial logic (fund conservation and temporal sequence) of the generated records.
*   **Baseline:** A demo showing the 50 records being successfully loaded and used to train a Scikit-learn anomaly detection model.
