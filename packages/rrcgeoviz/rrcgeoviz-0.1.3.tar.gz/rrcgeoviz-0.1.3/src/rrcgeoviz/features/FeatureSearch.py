import pandas as pd
import matplotlib.pyplot as plt
import panel as pn
import seaborn as sns
from IPython.display import display

from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature


class FeatureSearch(ParentGeovizFeature):
    def getOptionName(self):
        return "search_columns"

    def getRequiredColumns(self):
        return []

    def getHeaderText(self):
        return "Search Key Terms in Columns"

    def _generateComponent(self):
        # Define the search bar widgets
        column_dropdown = pn.widgets.Select(
            options=list(self.df.columns), name="Column"
        )

        search_dropdown = pn.widgets.Select(
            value="Choose Term",
            options=self.df[column_dropdown.value].value_counts().index.tolist(),
        )

        search_textbox = pn.widgets.AutocompleteInput(
            name="Search Term",
            restrict=False,
            options=self.df[column_dropdown.value].value_counts().index.tolist(),
            case_sensitive=False,
            search_strategy="includes",
        )

        def update_options(event):
            column_name = column_dropdown.value
            unique_values = self.df[column_name].value_counts().index.tolist()
            unique_values = [
                str(val) if pd.notna(val) else "NaN" for val in unique_values
            ]
            search_textbox.options = unique_values
            search_dropdown.options = unique_values

        column_dropdown.param.watch(update_options, "value")

        # Register the update function with the widgets
        plot = pn.bind(
            self._update_search,
            column=column_dropdown,
            search_term=search_textbox,
        )
        search = pn.Column(column_dropdown, search_textbox, plot)
        # search = pn.Column(column_dropdown, search_textbox, search_dropdown, plot)

        return search

    def get_unique_values(self, column):
        return self.df[column].unique().tolist()

    # Define the search function
    def search_data(self, column, search_term):
        filtered_df = self.df[
            self.df[column].str.contains(search_term, case=False, na=False)
        ]
        return filtered_df

    # Define the update function
    def _update_search(self, column, search_term=""):
        if search_term == "":
            return pn.Column(pn.pane.Matplotlib(sizing_mode="stretch_width"))
        filtered_df = self.search_data(column, search_term)

        num_columns = len(filtered_df[column].value_counts())
        height = max(6, num_columns * 0.5)
        # Plot the results
        fig, ax = plt.subplots(figsize=(12, height))
        sns.countplot(
            y=column,
            data=filtered_df,
            order=filtered_df[column].value_counts().index,
            ax=ax,
        )
        for p in ax.patches:
            ax.annotate(
                p.get_width(),
                (p.get_x() + p.get_width() + 20, p.get_y() + 0.4),
                ha="left",
                va="center",
            )
        ax.set_title("Occurrences of " + search_term + " in column: " + column)
        ax.set_xlabel("Count")
        ax.set_ylabel(column)

        plt.tight_layout()

        # Display the plot
        return pn.Column(pn.pane.Matplotlib(fig, sizing_mode="stretch_width"))
