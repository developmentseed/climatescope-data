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
langs = ['en','es']

# The current edition
current_edition = 2015



# Auxiliary data - Years we have want data for
yrs = [2006,2007,2008,2009,2010,2011,2012,2013,2014]

# The indicators for the auxiliary data
charts = [
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
          "en": 'Retail',
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
    "years": [2014]
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
    "years": [2014]
  },
  {
    "id": 201,
    "function": cs_auxiliary.default_chart,
    "export": 'clean-energy-investments',
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
    "series": [
      {
        "id": 'country',
        "source-id": "Clean energy investments",
        "level": "country",
      }
    ],
    "years": [2010, 2011, 2012, 2013, 2014]
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
      {
        "id": 'forestry',
        "source-id": "Forestry",
        "level": "country",
        "name": {
          "en": 'Forestry',
          "es": 'Silvicultura'
        }
      },
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
      },
      {
        "id": 'other',
        "source-id": "Other",
        "name": {
          "en": 'Other',
          "es": 'Otro'
        }
      },
    ],
    "years": [2014]
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
    "series": [
      {
        "id": 'biofuels',
        "source-id": "Biofuels",
        "name": {
          "en": 'Biofuels',
          "es": 'Biocombustible'
        },
        "subchains": [
          { "source-id": "Biofuels -Distribution and Blending ",
            "name": {
              "en": 'Distribution and Blending',
              "es": 'Distribución y Mezcla'
            }
          },
          { "source-id": "Biofuels - Engineering (Value)",
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
          { "source-id": "Biofuels - O&M (Value)",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Biofuels - Producers (Valeue)",
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
          { "source-id": "Small Hydro - Engineering ",
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
          { "source-id": "Solar - Balance of Plan",
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
          { "source-id": "Wind - Project Development",
            "name": {
              "en": 'Project development',
              "es": 'Desarrollo de proyectos'
            }
          },
          { "source-id": "Wind - Engineering",
            "name": {
              "en": 'Engineering',
              "es": 'Ingeniería'
            }
          },
          { "source-id": "Wind - O&M ",
            "name": {
              "en": 'O&M',
              "es": 'O&M'
            }
          },
          { "source-id": "Wind - Turbines",
            "name": {
              "en": 'Turbines',
              "es": 'Turbinas'
            }
          },
          { "source-id": "Wind - Blades",
            "name": {
              "en": 'Blades',
              "es": 'Palas'
            }
          },
          { "source-id": "Wind - Gearboxes ",
            "name": {
              "en": 'Gearboxes',
              "es": 'Cajas de cambio'
            }
          },
          { "source-id": "Wind - Towers ",
            "name": {
              "en": 'Towers',
              "es": 'Torres'
            }
          },
          { "source-id": "Wind - Balance of Plant",
            "name": {
              "en": 'Balance of plant',
              "es": 'Balance de planta'
            }
          }
        ]
      },
    ],
    "years": [2014]
  }
]