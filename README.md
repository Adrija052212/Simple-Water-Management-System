# Smart Water Consumption Management System

A household-level smart water consumption management system designed to monitor, analyse, predict and optimize daily water usage. The system aims to encourage responsible water consumption through data-driven insights, machine learning predictions and optimization techniques.

## Features

### 1. Dashboard
- Displays household water consumption summaries.
- Provides consumption analytics and historical insights.
- Shows activity-wise water usage.

### 2. Consumption Tracker
- Records daily household water consumption.
- Tracks water usage across different activities.
- Stores consumption records in an SQLite database.

### 3. Water Consumption Prediction
- Uses a K-Nearest Neighbors (KNN) regression model.
- Predicts water requirements for individual household activities.
- Estimates consumption for bathroom, kitchen, laundry and gardening activities.

### 4. Water Consumption Optimization
- Uses Linear Programming through SciPy.
- Allocates available water across household activities.
- Considers activity priorities and minimum allocation constraints.
- Identifies potential reductions in water demand.

### 5. Conservation Recommendations
- Provides activity-specific water conservation suggestions.
- Uses predefined recommendation rules to encourage efficient water usage.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Routing | React Router |
| Charts | Recharts |
| Backend | Python, Flask |
| API Integration | Flask-CORS |
| Database | SQLite |
| Machine Learning | Scikit-learn, KNN Regression |
| Optimization | SciPy, Linear Programming |
| Data Processing | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn |
| Model Serialization | Joblib |

## Project Architecture

The application follows a frontend-backend architecture.

- **Frontend:** React-based user interface for entering consumption data and viewing analytics, predictions and optimization results.
- **Backend:** Flask REST API that handles application logic and data processing.
- **Database:** SQLite database for storing household information and consumption records.
- **Machine Learning:** KNN regression model for estimating activity-wise water consumption.
- **Optimization Engine:** Linear Programming for allocating water under a specified availability constraint.
- **Recommendation Engine:** Rule-based system for generating conservation suggestions.

## Dataset and Model Development

The project includes a synthetic household water consumption dataset generated using Python.

- Synthetic dataset: 100 households across 20 days, producing 2,000 records.
- Random seed: 42 for reproducibility.
- Activities include bathroom, kitchen, laundry and gardening.
- Data analysis and visualization outputs are available under `backend/data/Processed/eda/`.
- The KNN model is trained and evaluated using the synthetic dataset.

**Note:** The synthetic dataset is generated using simulation assumptions. Model performance on this dataset does not establish real-world prediction accuracy. Further validation using actual household water meter data would be required for practical deployment.

## Project Structure

```text
Smart Water Consumption Management System/
|
|-- backend/
|   |-- app.py
|   |-- requirements.txt
|   |-- data/
|   |-- database/
|   |-- models/
|   |-- optimization/
|   |-- recommendations/
|   |-- routes/
|   |-- utils/
|   |-- validation/
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- pages/
|   |   |-- services/
|   |-- package.json
|   |-- vite.config.js
|
|-- .gitignore
|-- README.md
