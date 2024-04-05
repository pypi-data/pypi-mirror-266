This is a temporary repo that hosts code which needs to be plugged into the liia-tools-pipeline.

The input data used in this process are the output files generated at the end of the 903 pipeline.

## Setup
1. Create a `.env` file whose content should be a copy of the `env.sample` file.
2. In your `.env` file, assign the input and output variables to directories you choose. Ensure that your path ends with `\`.
3. In the command line, do `poetry install` and then `poetry shell` to install dependencies.
4. Then `python -m sufficiency_data_transform` to run the tool and generate the output files.

Dummy input data can be gotten from [this location](https://socialfinanceltd.sharepoint.com/:f:/s/Digi/Elr6MmNuznVBm6M3YWSlXqIBWRTv6Pb19eVe2HI_FdTXjw?e=TbZQYL). Care should be taken so that it is **never pushed** on GitHub. 
You can create an empty directory to which the outputs should be sent.

In production, the goal will be to return the new output files to the same location where the input files were gotten from.