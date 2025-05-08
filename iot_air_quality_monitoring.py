import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

class DataInfo:
    def __init__(self, df):
        self.df = df

    def summary(self):
        print("Shape:", self.df.shape)
        print("\nColumns:", self.df.columns.tolist())
        print("\nMissing values:\n", self.df.isnull().sum())
        print("\nData types:\n", self.df.dtypes)

    def head_stats(self):
        print("\nData Info:")
        print(self.df.info())
        print("\nData Summary:\n", self.df.describe())
        print("\nFirst Few Rows:\n", self.df.head())

class DataCleaner:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath, skiprows=3)

    def clean(self):
        self.df = self.df.drop(columns=["result", "table", "_start", "_stop", "_measurement", "host", "topic", "_time"], errors='ignore')

        self.df = self.df[self.df["_field"] == "co2_ppm"]

        self.df["_value"] = pd.to_numeric(self.df["_value"], errors='coerce')

        self.df = self.df.dropna(subset=["_value", "location"])

        indoor_values = self.df[self.df["location"] == "indoor"]["_value"].reset_index(drop=True)
        outdoor_values = self.df[self.df["location"] == "outdoor"]["_value"].reset_index(drop=True)

        merged_df = pd.DataFrame({
            "indoor": indoor_values,
            "outdoor": outdoor_values
        })

        return merged_df

class Visualizer:
    def __init__(self, df):
        self.df = df

    def plot_timeseries(self):
        plt.figure(figsize=(10, 5))
        if "indoor" in self.df.columns:
            sns.lineplot(data=self.df["indoor"], label="Indoor")
        if "outdoor" in self.df.columns:
            sns.lineplot(data=self.df["outdoor"], label="Outdoor")
        plt.title("Indoor vs Outdoor CO₂ ppm (Index-Based)")
        plt.xlabel("Index")
        plt.ylabel("CO₂ ppm")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def boxplot_comparison(self):
        plt.figure(figsize=(6, 5))
        melted = self.df[["indoor", "outdoor"]].melt(var_name="Location", value_name="CO₂ ppm")
        melted = melted.dropna()
        sns.boxplot(x="Location", y="CO₂ ppm", data=melted)
        plt.title("Indoor vs Outdoor CO₂ Distribution")
        plt.tight_layout()
        plt.show()
    
    def scatter_plot_indoor_vs_outdoor(self):
        plt.figure(figsize=(6, 5))

        sns.scatterplot(x=self.df.index, y=self.df["indoor"], label="Indoor", color="green", alpha=0.6)

        sns.scatterplot(x=self.df.index, y=self.df["outdoor"], label="Outdoor", color="blue", alpha=0.6)

        plt.title("Scatter Plot of Indoor and Outdoor CO₂ ppm Over Index")
        plt.xlabel("Index")
        plt.ylabel("CO₂ ppm")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def correlation_heatmap(self):
        plt.figure(figsize=(8, 4))
        sns.heatmap(self.df.corr(numeric_only=True), annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        plt.show()

    def label_distribution(self, labels):
        if labels is None or len(labels) == 0:
            print("No labels available to plot.")
            return
        plt.figure(figsize=(5, 4))
        sns.countplot(x=labels)
        plt.title("Air Quality Labels: 0=Good, 1=Poor")
        plt.xlabel("Label")
        plt.ylabel("Count")
        plt.show()

class AirQualityModel:
    def __init__(self, df):
        self.df = df.copy()

    def train_indoor_model(self):
        indoor_df = self.df[["indoor"]].dropna()

        if indoor_df.empty:
            print("No valid indoor data available for training.")
            return []

        indoor_df["label"] = (indoor_df["indoor"] > 2.0).astype(int)

        indoor_df["index"] = indoor_df.index
        indoor_df["hour"] = (indoor_df["index"] % 24).astype(int)
        indoor_df["minute"] = (indoor_df["index"] % 60).astype(int)

        X = indoor_df[["indoor", "hour", "minute"]]
        y = indoor_df["label"]

        if len(X) < 5:
            print("Not enough indoor data for training (need at least 5 rows).")
            return []

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        print("Indoor Air Quality Model Results:")
        print("Classification Report:\n", classification_report(y_test, y_pred))
        print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

        return y_pred

    def train_outdoor_model(self):
        outdoor_df = self.df[["outdoor"]].dropna()

        if outdoor_df.empty:
            print("No valid indoor data available for training.")
            return []

        outdoor_df["label"] = (outdoor_df["outdoor"] > 2.0).astype(int)

        outdoor_df["index"] = outdoor_df.index
        outdoor_df["hour"] = (outdoor_df["index"] % 24).astype(int)
        outdoor_df["minute"] = (outdoor_df["index"] % 60).astype(int)

        X = outdoor_df[["outdoor", "hour", "minute"]]
        y = outdoor_df["label"]

        if len(X) < 5:
            print("Not enough indoor data for training (need at least 5 rows).")
            return []

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        print("Outdoor Air Quality Model Results:")
        print("Classification Report:\n", classification_report(y_test, y_pred))
        print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

        return y_pred

if __name__ == '__main__':
    cleaner = DataCleaner("influxdb_data.csv")
    cleaned_df = cleaner.clean()

    info = DataInfo(cleaned_df)
    info.summary()
    info.head_stats()

    viz = Visualizer(cleaned_df)
    viz.plot_timeseries()
    viz.boxplot_comparison()
    viz.scatter_plot_indoor_vs_outdoor()
    viz.correlation_heatmap()

    ml = AirQualityModel(cleaned_df)
    indoort_labels = ml.train_indoor_model()
    outdoort_labels = ml.train_outdoor_model()
    labels = [max(i, j) for i, j in zip(indoort_labels, outdoort_labels)]
    print("Combined Labels:", labels)
    viz.label_distribution(labels)
