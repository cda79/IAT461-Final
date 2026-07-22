# Dataset Documentation: `workplace_accommodation_synthetic.csv`

## Overview

This dataset contains **260 synthetic accommodation request records** generated for the **Job Accommodation Network (JAN)** project proposal. The data simulates real-world workplace accommodation inquiries, tracking employee background attributes, functional request severities, estimated costs, assigned HR reviewers, approval decisions, fulfillment delays, and 6-month retention outcomes.

- **File Name:** `workplace_accommodation_synthetic.csv`
- **Row Count:** 260 rows
- **Column Count:** 16 columns
- **Primary Task:** Supervised Learning (Classification & Regression) / Bias Analysis

---

## Data Dictionary

| Column Name              | Data Type            | Missing Values | Description & Allowed Values                                                                                                                                               |
| :----------------------- | :------------------- | :------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `request_id`             | String               | None           | Unique alphanumeric identifier for each request (e.g., `REQ-1000`).                                                                                                        |
| `disability_category`    | String (Categorical) | None           | Primary health classification (`Mental Health`, `Chronic Medical`, `Cognitive/Neurological`, `Sensory`, `Physical/Mobility`).                                              |
| `accommodation_category` | String (Categorical) | None           | Type of workplace adjustment requested (`Schedule modification`, `Assistive technology`, `Physical workspace`, `Policy modification`, `Communication aid`).                |
| `employee_tenure_years`  | Float                | None           | Length of time the requesting employee has been with the company, in years (e.g., `4.3`).                                                                                  |
| `hourly_wage_usd`        | Float                | None           | Hourly wage of the employee in USD (e.g., `22.46`).                                                                                                                        |
| `has_college_degree`     | Integer (Binary)     | None           | Highest education level indicator (`1` = Degree held, `0` = No degree).                                                                                                    |
| `is_cost_incurred`       | Integer (Binary)     | None           | Flag indicating if fulfilling the accommodation requires a direct financial expense (`1` = Direct cost, `0` = No cost).                                                    |
| `accommodation_cost_usd` | Float                | None           | Total estimated financial cost in USD (`0.00` if `is_cost_incurred = 0`). Acts as a key control variable to distinguish cost barriers from systemic bias.                  |
| `request_severity_level` | String (Ordinal)     | None           | Self-reported functional impact and urgency of the request (`Low`, `Medium`, `High`).                                                                                      |
| `remote_work_status`     | String (Categorical) | None           | Primary work arrangement of the employee (`On-site`, `Hybrid`, `Remote`).                                                                                                  |
| `department`             | String (Categorical) | None           | Employer business unit (`Sales`, `Engineering`, `Operations`, `Customer Support`, `Finance`).                                                                              |
| `hr_reviewer_id`         | String (Categorical) | None           | Anonymized identifier of the assigned HR representative (`HR-101` through `HR-110`). Used to test for individual reviewer bias and inter-rater variance.                   |
| `approval_status`        | String (Categorical) | None           | **Primary Target Variable 1:** Outcome decision (`Approved`, `Partially Approved`, `Denied`).                                                                              |
| `denial_reason`          | String (Categorical) | 191 missing    | Primary rationale given if the request was denied (`Undue Hardship`, `Lack of Documentation`, `Ineligible`, `Alternative Offered`). Missing (`NaN`) for approved requests. |
| `days_to_implement`      | Float / Integer      | 69 missing     | **Primary Target Variable 2:** Calendar days elapsed from request submission to full implementation. Missing (`NaN`) for denied requests.                                  |
| `retained_6mo`           | Integer (Binary)     | None           | Long-term outcome: whether the employee remained employed 6 months after the request was evaluated (`1` = Retained, `0` = Resigned/Terminated).                            |

---

## Data Quality & Handling Notes

1. **Logical Missing Data (`NaN`):**
   - `denial_reason` contains missing values (`NaN`) for all requests with `approval_status == 'Approved'`.
   - `days_to_implement` contains missing values (`NaN`) for all requests with `approval_status == 'Denied'`.
   - _Data preparation strategies must preserve these logical relationships rather than naively dropping rows._

2. **Categorical Encoding:**
   - `request_severity_level` is **Ordinal** (`Low` < `Medium` < `High`).
   - `disability_category`, `accommodation_category`, `remote_work_status`, `department`, and `hr_reviewer_id` are **Nominal** categories.

3. **Target Features for Machine Learning:**
   - **Multi-class Classification:** Predict `approval_status` (`Approved`, `Partially Approved`, `Denied`).
   - **Regression:** Predict `days_to_implement` for approved requests to detect administrative delay bias.
   - **Binary Classification (Downstream Outcome):** Predict `retained_6mo` based on request approval and delay friction.
