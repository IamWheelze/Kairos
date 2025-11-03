# filepath: Kairos/scripts/evaluate.py

import argparse
import os
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
from src.kairos.training.trainer import load_model, preprocess_data

def evaluate_model(model_path, test_data_path):
    model = load_model(model_path)
    X_test, y_test = preprocess_data(test_data_path)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print(f"Model Accuracy: {accuracy:.2f}")
    print("Classification Report:")
    print(report)

def main():
    parser = argparse.ArgumentParser(description="Evaluate the performance of the trained model.")
    parser.add_argument('--model', type=str, required=True, help='Path to the trained model file.')
    parser.add_argument('--test_data', type=str, required=True, help='Path to the test data file.')

    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"Model file not found: {args.model}")
        return

    if not os.path.exists(args.test_data):
        print(f"Test data file not found: {args.test_data}")
        return

    evaluate_model(args.model, args.test_data)

if __name__ == "__main__":
    main()