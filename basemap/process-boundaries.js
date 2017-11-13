'use strict'

const csvParse = require('csv-parse')
const fs = require('fs')
const baseData = require('./tmp/ne50.json')

csvParse(fs.readFileSync('../source/meta/admin_areas.csv'), {columns:true}, function(err, metaCsv) {
  // Map the Natural Earth GeoJSON and modify the properties
  var finalFeatures = baseData.features.map(f => {
    // Check if the feature is a Climatescope country
    let aaMatch = metaCsv
      .filter(f => f.type === 'country')
      .find(o => o.iso.toLowerCase() === f.properties.ISO_A2.toLowerCase())

    if (aaMatch) {
      f.properties = {
        'cs': 1,
        'iso': f.properties.ISO_A2.toLowerCase(),
        'region': aaMatch.region
      }
    } else {
      f.properties = {
        'cs': 0,
        'iso': f.properties.ISO_A2.toLowerCase(),
        'region': null
      } 
    }
    return f
  })

  var finalData = {
    "type": "FeatureCollection",
    "features": finalFeatures
  }

  fs.writeFileSync('./climatescope-admin0-polygons.json', JSON.stringify(finalData))
})
