
from sdmetrics.reports.utils import get_column_pair_plot
from sdmetrics.reports.single_table import QualityReport
import os
from sdmetrics.reports.utils import get_column_plot
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
def closest_factors(n):
    closest_difference = n
    factor1 = 1
    factor2 = n

    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            current_factor1 = i
            current_factor2 = n // i
            difference = abs(current_factor1 - current_factor2)

            if difference < closest_difference:
                factor1 = current_factor1
                factor2 = current_factor2
                closest_difference = difference

    return factor1, factor2

def plot_all_column_shapes(figures, save_path):
    height_per_subplot = 300
    width_per_subplot = 300




    num_plots = len(figures)
    rows, cols = closest_factors(num_plots)

    # Compute total height and width based on the number of rows and columns
    total_height = rows * height_per_subplot
    total_width = cols * width_per_subplot

    subplot_titles = [f"Plot {i+1}" for i in range(num_plots)]
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles)

    for i, figure in enumerate(figures):
        row = i // cols + 1
        col = i % cols + 1
        for trace in figure.data:
            fig.add_trace(trace, row=row, col=col)
    fig.update_layout(height=total_height, width=total_width)
    pio.write_image(fig, save_path, format='png')




def generate_quality_report(real_data, synthetic_data, metadata, save_directory, save_name):


    base_report_folder =os.path.join(save_directory, save_name)
    if not os.path.exists(base_report_folder):
        # If it doesn't exist, create it
        os.makedirs(base_report_folder)


    report = QualityReport()
    report.generate(real_data, synthetic_data, metadata)
    #column shapes
    column_shapes=report.get_visualization(property_name='Column Shapes')
    column_shapes_details=report.get_details(property_name='Column Shapes')
    best_column=column_shapes_details.iloc[-1].to_dict()
    worst_column=column_shapes_details.iloc[0].to_dict()

    #columns pair trends
    column_pair_trends=report.get_visualization(property_name='Column Pair Trends')
    column_pair_trends_details=report.get_details(property_name='Column Pair Trends').sort_values(by='Quality Score', ascending=True)
    best_column_pair=column_pair_trends_details.iloc[-1].to_dict()
    worst_column_pair=column_pair_trends_details.iloc[0].to_dict()

    if save_directory is not None and save_name != "":
        report.save(filepath=os.path.join(base_report_folder,'sd_quality.pkl'))
        column_shapes.write_image(file=os.path.join(base_report_folder,"column_shapes.png"), format="png", scale=3)
        best_column_fig = get_column_plot(
            real_data=real_data,
            synthetic_data=synthetic_data,
            metadata=metadata,
            column_name=best_column['Column'])

        pio.write_image(best_column_fig, os.path.join(base_report_folder,"best_column_shape.png"), format='png', width=800, height=600)


        worst_column_fig = get_column_plot(
            real_data=real_data,
            synthetic_data=synthetic_data,
            metadata=metadata,
            column_name=worst_column['Column'])

        pio.write_image(worst_column_fig, os.path.join(base_report_folder, "worst_column_shape.png"), format='png', width=800,
                        height=600)

        column_figures=[]
        for column in real_data.columns:
            try:
                column_figures.append(get_column_plot(
                real_data=real_data,
                synthetic_data=synthetic_data,
                metadata=metadata,
                column_name=column))
            except:
                pass

        plot_all_column_shapes(column_figures, os.path.join(base_report_folder, "all_columns_shapes.png"))
#        for column in
        column_pair_trends.write_image(file=os.path.join(base_report_folder, "column_pair_trends.png"), format='png')



        best_column_pair_fig = get_column_pair_plot(
            real_data=real_data,
            synthetic_data=synthetic_data,
            metadata=metadata,
        column_names = [best_column_pair['Column 1'], best_column_pair['Column 2']])

        pio.write_image(best_column_pair_fig, os.path.join(base_report_folder, "best_column_pair_fig.png"), format='png',
                        width=800,
                        height=600)


        worst_column_pair_fig = get_column_pair_plot(
            real_data=real_data,
            synthetic_data=synthetic_data,
            metadata=metadata,
        column_names = [worst_column_pair['Column 1'], worst_column_pair['Column 2']])

        pio.write_image(worst_column_pair_fig, os.path.join(base_report_folder, "worst_column_pair_fig.png"), format='png',
                        width=800,
                        height=600)



def generate_quality_report_benchmark(datasets, synthetizes, repo):
    out = []
    from sdmetrics.reports.single_table import QualityReport
    for dataset in datasets:
        for fn in synthetizes:
            print(dataset, fn)
            print(f'{repo}/original_data/{dataset}_train.csv')
            print(f'{repo}/{dataset}_{fn}.csv.gz')
            trn = pd.read_csv(f'{repo}/original_data/{dataset}_train.csv')
            syn = pd.read_csv(f'{repo}/synthetic_data/{fn}_{dataset}.csv')
            metadata = {
                "columns": {c: {"sdtype": "categorical" if trn[c].dtype == 'object' else 'numerical'} for c in trn}}
            my_report = QualityReport()
            my_report.generate(trn, syn, metadata)
            out += [pd.DataFrame({
                'dataset': [dataset],
                'synthesizer': [fn],
                'Column Shapes': [my_report.get_details("Column Shapes")["Quality Score"].mean()],
                'Column Pair Trends': [my_report.get_details("Column Pair Trends")["Quality Score"].mean()],
            })]
    sdv = pd.concat(out).reset_index(drop=True)

    return sdv