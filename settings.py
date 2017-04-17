# Settings - Climatescope
# -*- coding: latin-1 -*-

# The main settings to process the Climatescope data
import cs_auxiliary

# Directory structure
src_dir = 'source/'
export_dir = 'data/'
tmp_dir = 'tmp/'

# Source - filenames / dirs
src_core = src_dir + 'cs-core/'
src_auxiliary = src_dir + 'cs-auxiliary/'

src_meta_aa = src_dir + 'meta/admin_areas.csv'
src_meta_index = src_dir + 'meta/index.csv'

# Export filenames
exp_core_csv = export_dir + 'cs-core.csv'
exp_full_csv = export_dir + '{lang}/download/data/climatescope-full.csv'
exp_current_csv = export_dir + '{lang}/download/data/climatescope-{yr}.csv'
exp_aa_csv = export_dir + '{lang}/download/data/countries/climatescope-{aa}.csv'
exp_region_csv = export_dir + '{lang}/download/data/regions/climatescope-{yr}-{region}.csv'
exp_params_csv =  export_dir + '{lang}/download/data/parameters/climatescope-{p}.csv'

exp_core = export_dir + '{lang}/api/countries.json'
exp_aa = export_dir + '{lang}/api/countries/{aa}.json'
exp_region = export_dir + '{lang}/api/regions/{region}.json'
exp_params = export_dir + '{lang}/api/parameters/{p}.json'
exp_stats = export_dir + '{lang}/api/stats.json'
exp_aux_json = export_dir + '{lang}/api/auxiliary/{indicator}/{aa}.json'

# Source structure
core_data_sheets = ['score', 'param', 'ind']
core_data_cols = ['id', 'iso', 'score', 'data']

# Languages
langs = ['en']

# The current edition
current_edition = 2016

# Auxiliary data - Years we have want data for
yrs = [2010,2011,2012,2013,2014,2015]

# The indicators for the auxiliary data
charts = [
  {
    "id": 102,
    "function": cs_auxiliary.default_chart,
    "export": 'power-sector-1',
    "title": {
      "en": 'Power sector structure',
      "es": 'Estructura del sector energético'
    },
    "labelx": {
      "en": ['Yes', 'Somewhat', 'No'],
      "es": ['Si', 'Algo', 'No']
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": True,
    "series": [
      {
        "id": 'q1',
        "source-id": 'q1',
        "level": "country",
        "name": {
          "en": 'The power sector has been unbundled (whether privatized or not) into distinct actors for generation, transmission, distribution and retail',
          "es": 'The power sector has been unbundled (whether privatized or not) into distinct actors for generation, transmission, distribution and retail',
        }
      },
      {
        "id": 'q2',
        "source-id": 'q2',
        "level": "country",
        "name": {
          "en": 'There are legally separate private companies at each segment of the power system pre-retail ',
          "es": 'There are legally separate private companies at each segment of the power system pre-retail ',
        }
      },
      {
        "id": 'q3',
        "source-id": 'q3',
        "level": "country",
        "name": {
          "en": 'There is an independent transmission system that dispatches according to market dynamics and is not susceptible to state interference',
          "es": 'There is an independent transmission system that dispatches according to market dynamics and is not susceptible to state interference',
        }
      },
      {
        "id": 'q4',
        "source-id": 'q4',
        "level": "country",
        "name": {
          "en": 'Retail electricity prices aren\'t distorted by subsidies ',
          "es": 'Retail electricity prices aren\'t distorted by subsidies ',
        }
      },
      {
        "id": 'q5',
        "source-id": 'q5',
        "level": "country",
        "name": {
          "en": 'There aren\'t significant barriers to private sector participation in generation',
          "es": 'There aren\'t significant barriers to private sector participation in generation',
        }
      },
      {
        "id": 'q6',
        "source-id": 'q6',
        "level": "country",
        "name": {
          "en": 'Consumers can choose retail suppliers or third-party power marketers in the retail power market',
          "es": 'Consumers can choose retail suppliers or third-party power marketers in the retail power market',
        }
      },
      {
        "id": 'q7',
        "source-id": 'q7',
        "level": "country",
        "name": {
          "en": 'There is a functioning competitive wholesale generation market',
          "es": 'There is a functioning competitive wholesale generation market',
        }
      },
      {
        "id": 'q8',
        "source-id": 'q8',
        "level": "country",
        "name": {
          "en": 'The generation market has many different actors and is not concentrated in the hands of a few players',
          "es": 'The generation market has many different actors and is not concentrated in the hands of a few players',
        }
      },
      {
        "id": 'q9',
        "source-id": 'q9',
        "level": "country",
        "name": {
          "en": 'The supply market has many different actors and is not concentrated in the hands of a few players',
          "es": 'The supply market has many different actors and is not concentrated in the hands of a few players',
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 102,
    "function": cs_auxiliary.default_chart,
    "export": 'power-sector-2',
    "title": {
      "en": 'Power sector structure',
      "es": 'Estructura del sector energético'
    },
    "labelx": {
      "en": ['Low', 'Regular', 'High', 'Very high'],
      "es": ['Low', 'Regular', 'High', 'Very high']
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": True,
    "series": [
      {
        "id": 'q10',
        "source-id": 'q10',
        "level": "country",
        "name": {
          "en": 'Power outages - frequency',
          "es": 'Power outages - frequency',
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 102,
    "function": cs_auxiliary.default_chart,
    "export": 'power-sector-3',
    "title": {
      "en": 'Power sector structure',
      "es": 'Estructura del sector energético'
    },
    "labelx": {
      "en": ['Short', 'Regular', 'Very regular', 'Long', 'Very long'],
      "es": ['Short', 'Regular', 'Very regular', 'Long', 'Very long']
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": True,
    "series": [
      {
        "id": 'q11',
        "source-id": 'q11',
        "level": "country",
        "name": {
          "en": 'Power outages - duration',
          "es": 'Power outages - duration',
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 102,
    "function": cs_auxiliary.default_chart,
    "export": 'power-sector-4',
    "title": {
      "en": 'Power sector structure',
      "es": 'Estructura del sector energético'
    },
    "labelx": {
      "en": ['Very low risk', 'Low risk', 'Neutral', 'Risky', 'Very risky'],
      "es": ['Very low risk', 'Low risk', 'Neutral', 'Risky', 'Very risky']
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": True,
    "series": [
      {
        "id": 'q12',
        "source-id": 'q12',
        "level": "country",
        "name": {
          "en": 'Power offtake risk for independent generators',
          "es": 'Power offtake risk for independent generators',
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 107, # The source file contains an indication of the id
    "function": cs_auxiliary.default_chart,
    "export": 'installed-capacity', # Folder for the exported data
    "title": { # Title of the chart
      "en": 'Installed capacity',
      "es": 'Capacidad instalada'
    },
    "labelx": { # Label of the x-axis
      "en": 'year',
      "es": 'año'
    },
    "labely": { # Label of the y-axis
      "en": 'MW',
      "es": 'MW'
    },
    "note": False,
    "series": [
      {
        "id": 'non-clean-energy', # The id used in the export
        "source-id": 'Non-clean Energy', # The id in the source CSV
        "level": "country", # Data on country level. When 'regional' or 'global' is used, averages are calculated
        "name": {
          "en": 'Non-clean Energy',
          "es": 'Energía no limpia'
        }
      },
      {
        "id": 'clean-energy', # The id used in the export
        "source-id": 'Clean Energy', # The id in the source CSV
        "level": "country",
        "name": {
          "en": 'Clean Energy',
          "es": 'Energía limpia'
        }
      }
    ],
    "years": yrs # List with years to process
  },
  {
    "id": 903,
    "function": cs_auxiliary.default_chart,
    "global_average": True,
    "export": 'price-attractiveness-electricity',
    "title": {
      "en": 'Price attractiveness',
      "es": 'Atractivo del precio'
    },
    "labelx": {
      "en": 'USD/MWh',
      "es": 'USD/MWh'
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": False,
    "series": [
      {
        "id": 'spot_electricity',
        "source-id": "Average electricity spot prices ($/MWh)",
        "level": "country",
        "name": {
          "en": 'Spot',
          "es": 'Spot'
        }
      },
      {
        "id": 'retail_electricity',
        "source-id": "Average retail electricity prices ($/MWh)",
        "level": "country",
        "name": {
          "en": 'Retail Avg',
          "es": 'Al por menor'
        }
      },
      {
        "id": 'residential_electricity',
        "source-id": "Average residential electricity prices ($/MWh)",
        "level": "country",
        "name": {
          "en": 'Residential',
          "es": 'Residencial'
        }
      },
      {
        "id": 'commercial_electricity',
        "source-id": "Average commercial  electricity prices ($/MWh)",
        "level": "country",
        "name": {
          "en": 'Commercial',
          "es": 'Comercial'
        }
      },
      {
        "id": 'industrial_electricity',
        "source-id": "Average industrial electricity prices ($/MWh)",
        "level": "country",
        "name": {
          "en": 'Industrial',
          "es": 'Industrial'
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 903,
    "function": cs_auxiliary.default_chart,
    "export": 'price-attractiveness-fuel',
    "title": {
      "en": 'Price attractiveness',
      "es": 'Atractivo del precio'
    },
    "labelx": {
      "en": 'USD/Liter',
      "es": 'USD/Litro'
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": False,
    "series": [
      {
        "id": 'diesel',
        "source-id": "Average diesel prices ($/l)",
        "level": "country",
        "name": {
          "en": 'Diesel',
          "es": 'Diesel'
        }
      },
      {
        "id": 'kerosene',
        "source-id": "Average kerosene prices ($/l)",
        "level": "country",
        "name": {
          "en": 'Kerosene',
          "es": 'Queroseno'
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 201,
    "function": cs_auxiliary.default_chart,
    "export": 'clean-energy-investments',
    "global_average": True,
    "title": {
      "en": 'Clean energy investments',
      "es": 'Inversiones en energías limpias'
    },
    "labelx": {
      "en": 'year',
      "es": 'año'
    },
    "labely": {
      "en": 'USDm',
      "es": 'USDm'
    },
    "note": False,
    "series": [
      {
        "id": 'country',
        "source-id": "Clean energy investments",
        "level": "country",
      }
    ],
    "years": [2010, 2011, 2012, 2013, 2014, 2015]
  },
  {
    "id": 401,
    "function": cs_auxiliary.default_chart,
    "export": 'carbon-offset-projects',
    "title": {
      "en": 'Carbon offset projects by sector',
      "es": 'Compensaciones de carbono por sector'
    },
    "labelx": {
      "en": 'category',
      "es": 'categoria'
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": False,
    "series": [
      {
        "id": 'power-generation',
        "source-id": "Power generation",
        "level": "country",
        "name": {
          "en": 'Power generation',
          "es": 'Generación eléctrica'
        }
      },
      {
        "id": 'methane',
        "source-id": "Methane",
        "level": "country",
        "name": {
          "en": 'Methane',
          "es": 'Metano'
        }
      },
      # {
      #   "id": 'forestry',
      #   "source-id": "Forestry",
      #   "level": "country",
      #   "name": {
      #     "en": 'Forestry',
      #     "es": 'Silvicultura'
      #   }
      # },
      {
        "id": 'waste',
        "source-id": "Waste",
        "level": "country",
        "name": {
          "en": 'Waste',
          "es": 'Residuos'
        }
      },
      {
        "id": 'energy-efficiency',
        "source-id": "Energy efficiency",
        "level": "country",
        "name": {
          "en": 'Energy efficiency',
          "es": 'Eficiencia energética'
        }
      }
    ],
    "years": [2015]
  },
  {
    "id": 910,
    "function": cs_auxiliary.value_chains,
    "export": 'value-chains',
    "title": {
      "en": 'Value chains',
      "es": 'Cadenas de valor'
    },
    "labelx": {
      "en": '',
      "es": ''
    },
    "labely": {
      "en": '',
      "es": ''
    },
    "note": False,
    "series": [
      {
        "id": 'biofuels',
        "source-id": "Biofuels",
        "name": {
          "en": 'Biofuels',
          "es": 'Biocombustible'
        },
        "subchains": [
          { "source-id": "Biofuels - Distribution and Blending",
            "name": {
              "en": 'Distribution and Blending',
              "es": 'Distribución y Mezcla'
            }
          },
          { "source-id": "Biofuels - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Biofuels - Equipment Manufacturing",
            "name": {
              "en": 'Equipment Manufacturing',
              "es": 'Manufactura de equipos'
            }
          },
          { "source-id": "Biofuels - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Biofuels - Producers",
            "name": {
              "en": 'Producers',
              "es": 'Productores'
            }
          }
        ]
      },
      {
        "id": 'biomass',
        "source-id": "Biomass",
        "level": "country",
        "name": {
          "en": 'Biomass',
          "es": 'Biomasa y Resíduos'
        },
        "subchains": [
          { "source-id": "Biomass & Waste - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Biomass & Waste - Equipment Manufacturing",
            "name": {
              "en": 'Equipment manufacturing',
              "es": 'Manufactura de equipos'
            }
          },
          { "source-id": "Biomass & Waste - Feedstock Supply",
            "name": {
              "en": 'Feedstock supply',
              "es": 'Abastecimiento de materia prima'
            }
          },
          { "source-id": "Biomass & Waste - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Biomass & Waste - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          }
        ]
      },
      {
        "id": 'geothermal',
        "source-id": "Geothermal",
        "level": "country",
        "name": {
          "en": 'Geothermal',
          "es": 'Geotérmia'
        },
        "subchains": [
          { "source-id": "Geothermal - Balance of Plant",
            "name": {
              "en": 'Balance of plant',
              "es": 'Balance de planta'
            }
          },
          { "source-id": "Geothermal - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Geothermal - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Geothermal - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          },
          { "source-id": "Geothermal - Resource Development",
            "name": {
              "en": 'Resource development',
              "es": 'Desarrollo de recursos'
            }
          },
          { "source-id": "Geothermal - Turbines",
            "name": {
              "en": 'Turbines',
              "es": 'Turbinas'
            }
          }
        ]
      },
      {
        "id": 'small-hydro',
        "source-id": "Small Hydro",
        "level": "country",
        "name": {
          "en": 'Small Hydro',
          "es": 'Pequeñas Centrales Hidroeléctricas'
        },
        "subchains": [
          { "source-id": "Small Hydro - Balance of Plant",
            "name": {
              "en": 'Balance of plant',
              "es": 'Balance de planta'
            }
          },
          { "source-id": "Small Hydro - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Small Hydro - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Small Hydro - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          },
          { "source-id": "Small Hydro - Turbines",
            "name": {
              "en": 'Turbines',
              "es": 'Turbinas'
            }
          }
        ]
      },
      {
        "id": 'solar',
        "source-id": "Solar",
        "level": "country",
        "name": {
          "en": 'Solar',
          "es": 'Solar'
        },
        "subchains": [
          { "source-id": "Solar - Balance of Plant",
            "name": {
              "en": 'Balance of plant',
              "es": 'Balance de planta'
            }
          },
          { "source-id": "Solar - Cells",
            "name": {
              "en": 'Cells',
              "es": 'Células'
            }
          },
          { "source-id": "Solar - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Solar - Inverters",
            "name": {
              "en": 'Inverters',
              "es": 'Inversores'
            }
          },
          { "source-id": "Solar - Modules",
            "name": {
              "en": 'Modules',
              "es": 'Módulos'
            }
          },
          { "source-id": "Solar - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Solar - Polysilicon/ingots",
            "name": {
              "en": 'Polysilicon/ingots',
              "es": 'Polisilicio/lingotes'
            }
          },
          { "source-id": "Solar - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          },
          { "source-id": "Solar - Wafers",
            "name": {
              "en": 'Wafers',
              "es": 'Obleas'
            }
          }
        ]
      },
      {
        "id": 'wind',
        "source-id": "Wind",
        "name": {
          "en": 'Wind',
          "es": 'Eólica'
        },
        "subchains": [
          { "source-id": "Wind - Balance of Plant",
            "name": {
              "en": 'Balance of plant',
              "es": 'Balance de planta'
            }
          },
          { "source-id": "Wind - Blades",
            "name": {
              "en": 'Blades',
              "es": 'Palas'
            }
          },
          { "source-id": "Wind - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Wind - Gearboxes",
            "name": {
              "en": 'Gearboxes',
              "es": 'Cajas de cambio'
            }
          },
          { "source-id": "Wind - O&M",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Wind - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          },
          { "source-id": "Wind - Towers",
            "name": {
              "en": 'Towers',
              "es": 'Torres'
            }
          },
          { "source-id": "Wind - Turbines",
            "name": {
              "en": 'Turbines',
              "es": 'Turbinas'
            }
          },
        ]
      },
    ],
    "years": [2015]
  }
]