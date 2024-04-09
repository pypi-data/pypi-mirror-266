import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.calibration import calibration_curve

import flippers

binary_datasets = [
    "imdb",
    "yelp",
    "youtube",
    "sms",
    "spouse",
    "cdr",
    "commercial",
    "tennis",
    "basketball",
    "census",
]

dataset_to_metric = {
    "imdb": "Accuracy",
    "yelp": "Accuracy",
    "youtube": "Accuracy",
    "sms": "F1",
    "agnews": "Accuracy",
    "trec": "Accuracy",
    "spouse": "F1",
    "cdr": "F1",
    "semeval": "Accuracy",
    "chemprot": "Accuracy",
    "commercial": "F1",
    "tennis": "F1",
    "basketball": "F1",
    "census": "F1",
}

datasets = list(dataset_to_metric.keys())


# This helper loads any dataset in the wrench benchmarks
# and creates monopolar label matrices from their multipolar data
def load_wrench_dataset(dataset):
    dataset = "datasets/" + f"{dataset}" + "/{}.json"
    train = pd.read_json(dataset.format("train")).T
    dev = pd.read_json(dataset.format("valid")).T
    test = pd.read_json(dataset.format("test")).T

    L_train, polarities, polarities_mapping = flippers.multipolar_to_monopolar(
        train["weak_labels"].apply(pd.Series)
    )
    L_dev, _, _ = flippers.multipolar_to_monopolar(
        dev["weak_labels"].apply(pd.Series), polarities_mapping
    )
    L_test, _, _ = flippers.multipolar_to_monopolar(
        test["weak_labels"].apply(pd.Series), polarities_mapping
    )

    return (train, dev, test), (L_train, L_dev, L_test), polarities


class MetricsMaker:
    def __init__(self, y_true, L=None):
        self.L = L
        self.y_true = y_true
        self.n_classes = len(np.unique(y_true))
        self.metrics = {}

    def score(
        self,
        model=None,
        name="",
        y_pred=None,
        plots=True,
        fill_proba=False,
        predict_proba_args={},
    ):
        if y_pred is None:
            y_pred = model.predict_proba(self.L, **predict_proba_args)

        if fill_proba:

            def fill_proba(proba):
                proba = proba.copy()
                proba[self.L.sum(axis=1) == 0] = 0
                return proba

            y_pred = fill_proba(y_pred)
        if self.n_classes == 2:
            if y_pred.ndim == 2:
                y_pred = y_pred[:, 1]
            AP = metrics.average_precision_score(self.y_true, y_pred)
            F1 = metrics.f1_score(self.y_true, y_pred.round())
            AUC = metrics.roc_auc_score(self.y_true, y_pred)
            Accuracy = metrics.accuracy_score(self.y_true, y_pred.round())
            Balanced_Accuracy = metrics.balanced_accuracy_score(
                self.y_true, y_pred.round()
            )
            M = {
                "F1": F1,
                "Average_Precision": AP,
                "AUC": AUC,
                "Accuracy": Accuracy,
                "Balanced_Accuracy": Balanced_Accuracy,
            }
        else:
            M = {}
            # for average in ["macro"]:
            #     precision, recall, fscore, _ = precision_recall_fscore_support(
            #         self.y_true, y_pred.argmax(axis=1), average=average
            #     )
            #     M[f"Precision_{average}"] = precision
            #     M[f"Recall_{average}"] = recall
            #     M[f"F1_{average}"] = fscore
            M["Accuracy"] = metrics.accuracy_score(self.y_true, y_pred.argmax(axis=1))
            M["Balanced_Accuracy"] = metrics.balanced_accuracy_score(
                self.y_true, y_pred.argmax(axis=1)
            )

        for key in M:
            M[key] = round(M[key], 3)

        if plots and self.n_classes == 2:
            fig, axs = plt.subplots(1, 2, figsize=(9, 4))
            plt.title(name)

            # Plot the distribution of y_pred grouped by ground truth
            pd.DataFrame({"y_pred": y_pred, "y_true": self.y_true}).boxplot(
                by="y_true", ax=axs[0]
            )
            axs[0].set_title("Predicted probabilities grouped by ground truth")
            axs[0].set_ylim([0, 1])
            axs[0].get_figure().suptitle("")
            axs[1].set_ylabel("y_pred")

            # Plot the distribution of y_pred
            y_pred = pd.Series(y_pred)
            y_pred.plot.hist(
                ax=axs[1],
                bins=21,
                weights=np.ones_like(y_pred.index) / len(y_pred.index),
            )
            axs[1].set_title("Predicted probabilties")
            #  axs[1].set_ylim([0, 1])
            axs[1].scatter(
                [self.y_true.mean()],
                [0.1],
                color="g",
                marker="o",
                s=100,
                alpha=0.5,
                label="Mean of y_true",
            )

            # Add a cross indicating the mean of y_pred
            mean_y_pred = pd.Series(y_pred).mean()
            axs[1].scatter(
                [mean_y_pred],
                [0.1],
                marker="+",
                color="r",
                s=200,
                label="Mean of y_pred",
            )

            ## Calibration curve
            # Compute the calibration curve
            fraction_of_positives, mean_predicted_value = calibration_curve(
                self.y_true, y_pred, n_bins=20
            )

            # Plot the calibration curve
            axs[1].set_title("Calibration Curve")
            axs[1].plot(
                mean_predicted_value,
                fraction_of_positives,
                "s-",
                label="Fraction of positives",
                alpha=0.5,
            )
            axs[1].plot([0, 1], [0, 1], "--", color="gray")
            axs[1].set_xlabel("Predicted Value")
            # axs[1].set_ylabel("Fraction of Positives")
            axs[1].set_xlabel("y_pred")
            axs[1].legend()

            plt.tight_layout()
            plt.show()

        if name:
            self.metrics[name] = M

        return M
