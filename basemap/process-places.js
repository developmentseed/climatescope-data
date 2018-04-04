'use strict'

const csvParse = require('csv-parse')
const fs = require('fs')
const baseData = require('./tmp/ne50_places.json')

csvParse(fs.readFileSync('../source/meta/admin_areas.csv'), {columns:true}, function(err, output) {
  // Generate an array with iso codes of CS countries
  const csCountries = output
    .filter(f => f.type === 'country')
    .map(f => f.iso.toLowerCase())

  // Filter the capitals to those we are interested in
  var finalFeatures = baseData.features
    .filter(f => csCountries.indexOf(f.properties.iso_a2.toLowerCase()) !== -1)
    .filter(f => f.properties.featurecla === 'Admin-0 capital')
    .map(f => {
      f.properties = {
        'name': f.properties.name,
        'iso': f.properties.iso_a2.toLowerCase()
      }
      return f
    })

  var finalData = {
    "type": "FeatureCollection",
    "features": finalFeatures
  }

  fs.writeFileSync('./climatescope-admin0-capitals.json', JSON.stringify(finalData))
})
