from src.library import process_data
import click

@click.command(name="normalize")
@click.option("--canonicals", "-c", required=True, help="Canonicals companies names separated by comma. (e.g 'MICROSOFT TECHNOLOGY LICENSING,MICRON TECHNOLOGY,DELTA TECHNOLOGY,ELTA TECHNOLOGY')")
@click.option("--input_filepath", "-i", required=True, help="Path to the Excel file that need to be processed.")
@click.option("--output_filepath", "-o", required=True, help="Path to save the processed Excel file.")
def main(canonicals: str, input_filepath: str, output_filepath: str):

    process_data(
       canonicals=canonicals.split(","),
       read_file_path=input_filepath,
       destination_path=output_filepath
    )
    print(f"File {input_filepath} was successfully normalized. \n Open the {output_filepath}output.xlsx to check the results.")
    
if __name__ == "__main__":
    main()