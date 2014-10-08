This script processes the data for the Global Climatescope and prepares it for use on the website. It works as a make file and will rebuild the full dataset on every run.

## Usage
A quick overview of the process:

1. Provide source data  
The source data is stored in the ```source``` folder.
2. Run script  
```python cs-core.py```
3. Move output to Jekyll site structure

## Source data
### Core CS data
The script expects the core Climatescope data to be provided in .xlsx format and stored in ```source/cs-core```. The data for each edition should be in separate files that are named after its year. For example: ```source/cs-core/2013.xlsx``` and ```source/cs-core/2014.xlsx```.

These files should contain the following sheets:

- score
- param
- ind

Each of these files, should have the following columns:

| column | description |
| --- | --- |
| id | Contains the id of the score, param or indicator |
| iso | The ISO 3166 code of the country, state or province |
| score | The score |

Any extra columns or sheets will be ignored by the script.

Notes:
- the header of the different sheets should not have filters enabled
- the structure of the files was proposed by BNEF for the first edition of the Global Climatescope

## Sources

Shapefiles: Natural Earth
Country and state capitals: Wikipedia