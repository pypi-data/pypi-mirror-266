import matplotlib

matplotlib.use("Agg")
import panel as pn
from io import BytesIO
from ydata_profiling import ProfileReport
from rrcgeoviz.arguments import Arguments


def gen_profile_report(args: Arguments):
    loading_spinner = pn.indicators.LoadingSpinner(
        value=False, visible=False, size=50, color="primary", bgcolor="dark"
    )

    def generate_profile_report():
        df = args.getData()
        loading_spinner.value = True
        loading_spinner.visible = True
        # Generate a Pandas Profiling report
        profile_report = ProfileReport(df)
        html_content = profile_report.to_html().encode()
        html_bytesio = BytesIO(html_content)
        loading_spinner.visible = False
        loading_spinner.value = False
        return html_bytesio

    download_pandas_button = pn.widgets.FileDownload(
        label="Download Pandas Report",
        callback=generate_profile_report,
        filename="Pandas_Profiling.html",
    )

    def generate_new_csv():
        df = args.getData()
        loading_spinner.value = True
        loading_spinner.visible = True
        csv_data = df.to_csv(index=False).encode()
        csv_bytesio = BytesIO(csv_data)
        loading_spinner.visible = False
        loading_spinner.value = False
        return csv_bytesio

    download_csv_button = pn.widgets.FileDownload(
        label="Download New Dataframe",
        callback=generate_new_csv,
        filename=f"rrcgeoviz_{args.getDataFileName()}.csv",
    )

    return pn.Column(download_pandas_button, download_csv_button, loading_spinner)
