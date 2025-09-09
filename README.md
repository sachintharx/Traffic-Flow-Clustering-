# Traffic Flow Clustering 🚦📊
## 📌 Overview

An intelligent traffic flow clustering system designed to analyze urban vehicle density patterns and categorize road segments into Low, Medium, and High flow levels.
The project leverages Convolutional Autoencoders, Clustering Algorithms, and MLOps practices to extract insights from simulated traffic data and present them through an interactive dashboard with AI-powered explanations.

🔗 YouTube Demo: https://www.youtube.com/watch?v=6jiOc9sTZJ4&feature=youtu.be 

🔗 GitHub Repository: https://github.com/sachintharx/Traffic-Flow-Clustering-

## 🚀 Features

- SUMO-based traffic simulation and data collection

- Convolutional Autoencoder for latent feature extraction

- Unsupervised clustering of traffic flow patterns

- MLflow & Optuna for experiment tracking and hyperparameter optimization

- FastAPI REST API for automated report generation

- Streamlit Dashboard with real-time filtering, visualization, and GPT-powered chatbot

## 🔍 Project Structure

- Data Gathering → Vehicle density collection using SUMO & TraCI API

- Data Preprocessing → Normalization, reshaping, sequence preparation

- Autoencoder Training → Conv1D-based model with latent space representation

- Clustering → Assigning segments to Low, Medium, High flow categories

- MLflow Integration → Experiment logging and parameter optimization

- REST API → Report generation and integration with dashboard

- Dashboard → Interactive traffic analysis with AI chatbot explanations

## 🛠️ Technologies Used

- Simulation & Data: SUMO, TraCI, Python

- Libraries: Pandas, NumPy, Scikit-learn, Matplotlib

- Deep Learning: TensorFlow, Keras

- Optimization & MLOps: Optuna, MLflow

- Deployment: FastAPI, Streamlit

- AI Assistant: Gemini-powered conversational interface

## 📊 Data Preprocessing

- Vehicle counts collected across timesteps per road segment

- Dataset converted into a segment × timestep matrix

- Normalized with StandardScaler

- Reshaped into 3D tensors for Conv1D-based Autoencoder training

## 🧠 Autoencoder Architecture

- Encoder → Conv1D + MaxPooling layers for compression

- Latent Space → Compact feature representation of traffic flow

- Decoder → Conv1D + UpSampling layers for reconstruction

- Loss Function: Mean Squared Error (MSE)

- Optimizer: Adam

- Early stopping applied to prevent overfitting

## ⚙️ Model Development & Training

- Trained on preprocessed sequences with tuned hyperparameters

- Optuna for hyperparameter optimization

- MLflow for tracking validation loss, experiments, and model configs

- Best-performing model parameters exported to YAML for reproducibility

## 📈 Performance Evaluation

- Evaluated using validation loss

- Clustering verified by categorization into Low / Medium / High flow

- Latent space visualizations confirm meaningful feature extraction

## 🌐 REST API Development

- Built with FastAPI for end-to-end automation  

- `/get_report` endpoint returns:  
  - Road segment IDs  
  - Cluster IDs  
  - Assigned flow categories  

- Outputs downloadable CSV reports
  
## 📊 Dashboard & Gemini Integration  

- Built with Streamlit for interactive analysis  

- Core Features:  
  - KPI cards (Low/Medium/High segment counts)  
  - Multi-filters (cluster, category, segment search, traffic range)  
  - Distribution charts, box plots, histograms, geo scatter maps  
  - Styled tables with CSV download  

- AI Assistant (Gemini):  
  - Answers natural language questions about clusters  
  - Provides explanations grounded in dataset facts  


## ⚡ Challenges & Future Work
### Challenges

- Balancing Conv1D vs LSTM Autoencoders (speed vs accuracy)

- Limited real-world validation due to simulated dataset

- Computational resource constraints for LSTM models

### Future Enhancements

- Integrating real-world traffic sensor data

- Adding external clustering evaluation metrics

- Optimizing for real-time prediction

- Experimenting with LSTM/Transformer-based Autoencoders

- Extending dashboard with predictive analytics & scenario simulations
