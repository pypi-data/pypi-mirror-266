from matplotlib import pyplot as plt
import panel as pn
import seaborn as sns
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature


class FeatureHeatmap(ParentGeovizFeature):
    def getOptionName(self):
        return "month_year_heatmap"

    def getRequiredColumns(self):
        return ["time_column"]

    def getHeaderText(self):
        return "Year/Month Heatmap"

    def _generateComponent(self):
        pivot_df = self.df.pivot_table(
            index="Year", columns="Month", aggfunc="size", fill_value=0
        )
        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        sns.set(font_scale=0.4)
        sns.heatmap(pivot_df, cmap="inferno", annot=True, fmt="d", linewidths=0.5)
        plt.title("Monthly Incident Counts Over Different Years", fontsize=12)

        heatmap_app = pn.Column(pn.pane.Matplotlib(plt.gcf()))
        # Show the Panel app
        return heatmap_app
