import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class MLService:
    feature_columns = [
        "Gender",
        "Married",
        "Dependents",
        "Self_Employed",
        "ApplicantIncome",
        "Credit_History",
        "Property_Area",
    ]

    def __init__(self, model_bundle_path, training_data_path):
        self.model_bundle_path = model_bundle_path
        self.training_data_path = training_data_path
        self.classifier = None
        self.regressor = None
        self._load_or_train()

    def _build_preprocessor(self):
        categorical = ["Gender", "Married", "Dependents", "Self_Employed", "Property_Area"]
        numeric = ["ApplicantIncome", "Credit_History"]
        return ColumnTransformer(
            transformers=[
                (
                    "cat",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    categorical,
                ),
                (
                    "num",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric,
                ),
            ]
        )

    def _load_or_train(self):
        if os.path.exists(self.model_bundle_path):
            bundle = joblib.load(self.model_bundle_path)
            self.classifier = bundle["classifier"]
            self.regressor = bundle["regressor"]
            return
        self.train_from_csv()

    def train_from_csv(self):
        df = pd.read_csv(self.training_data_path)
        df["LoanAmount"] = df["LoanAmount"].astype(str).str.replace("$", "", regex=False).astype(float)
        df["Dependents"] = df["Dependents"].fillna("0").replace("3+", "3")
        df["Loan_Status"] = df["Loan_Status"].map({"Y": 1, "N": 0})
        df["Credit_History"] = df["Credit_History"].fillna(0).astype(int)

        X = df[self.feature_columns].copy()
        y_cls = df["Loan_Status"]
        y_reg = df["LoanAmount"]

        classifier = Pipeline(
            [("prep", self._build_preprocessor()), ("model", LogisticRegression(max_iter=500))]
        )
        regressor = Pipeline([("prep", self._build_preprocessor()), ("model", LinearRegression())])

        classifier.fit(X, y_cls)
        regressor.fit(X, y_reg)

        self.classifier = classifier
        self.regressor = regressor
        joblib.dump({"classifier": classifier, "regressor": regressor}, self.model_bundle_path)

    def predict(self, payload):
        df = pd.DataFrame(
            [
                {
                    "Gender": payload["gender"],
                    "Married": payload["married"],
                    "Dependents": payload["dependents"].replace("3+", "3"),
                    "Self_Employed": payload["self_employed"],
                    "ApplicantIncome": float(payload["income"]),
                    "Credit_History": int(payload["credit_history"]),
                    "Property_Area": payload["property_area"],
                }
            ]
        )
        loan_status = int(self.classifier.predict(df)[0])
        loan_amount = float(self.regressor.predict(df)[0])
        return {"loan_status": loan_status, "loan_amount": max(0.0, round(loan_amount, 2))}
