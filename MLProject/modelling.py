import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import argparse
import warnings

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    # Argparse untuk ambil parameter dari MLflow Project
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", type=str, default="./liver_cancer_preprocessing/train_liver.csv")
    parser.add_argument("--test_path", type=str, default="./liver_cancer_preprocessing/test_liver.csv")
    parser.add_argument("--n_estimators", type=int, default=505)
    parser.add_argument("--max_depth", type=int, default=37)
    args = parser.parse_args()

    # Baca dataset
    train_data = pd.read_csv(args.train_path)
    test_data = pd.read_csv(args.test_path)

    X_train = train_data.drop('liver_cancer', axis=1)
    y_train = train_data['liver_cancer']
    X_test = test_data.drop('liver_cancer', axis=1)
    y_test = test_data['liver_cancer']

    # Aktifkan autolog
    mlflow.sklearn.autolog()

    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=42
        )
        model.fit(X_train, y_train)
        acc = model.score(X_test, y_test)
        print(f"Accuracy: {acc}")
        mlflow.log_metric("accuracy", acc)
