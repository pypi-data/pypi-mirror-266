from matplotlib import pyplot as plt
import panel as pn
import seaborn as sns
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature


class FeatureAllMonths(ParentGeovizFeature):
    def getOptionName(self):
        return "all_months"

    def getRequiredColumns(self):
        return ["time_column"]

    def getHeaderText(self):
        return "Month-to-Month Frequency"

    def _generateComponent(self):
        fig, _ = plt.subplots(figsize=(8, 4))
        sns.set(style="whitegrid")
        sns.countplot(data=self.df, x="Month", palette="colorblind")
        plt.xlabel("Month")
        plt.ylabel("Frequency")
        plt.title("All Incidents by Month")
        plt.close(fig)

        fig, _ = plt.subplots(figsize=(5.5, 4.5))
        sns.set_theme(font_scale=0.4)
        sns.countplot(data=self.df, x="Month", palette="colorblind")
        plt.title("All Incidents by Month", fontsize=12)

        months_app = pn.Column(pn.pane.Matplotlib(plt.gcf()))

        # Show the Panel app
        return months_app
