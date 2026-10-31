import pandas as pd
import os
import json
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load dataset
df = pd.read_csv("dataset.csv")

# Assume last column is label
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model
os.makedirs("model", exist_ok=True)
os.makedirs("static", exist_ok=True)

joblib.dump(model, "model/model.pkl")

# Save feature names
with open("model/feature_names.json", "w") as f:
    json.dump(list(X.columns), f)

# Save accuracy
with open("model/metrics.json", "w") as f:
    json.dump({"accuracy": accuracy}, f)

# Confusion Matrix Graph
cm = confusion_matrix(y_test, y_pred)
plt.figure()
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig("static/confusion_matrix.png")
plt.close()

# Dataset Distribution Graph
plt.figure()
df.iloc[:, -1].value_counts().plot(kind='bar')
plt.title("Dataset Class Distribution")
plt.savefig("static/class_distribution.png")
plt.close()

print("Model and evaluation graphs saved successfully!")
