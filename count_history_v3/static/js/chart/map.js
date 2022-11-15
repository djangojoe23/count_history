let regionalSeries = {}
let currentSeries
let mapChart
let drillOut
let yearSlider
let yearRange = [10000, -10000]
function GenerateMapChart(){
    am5.ready(function() {

        chartRoot = am5.Root.new("chartVisual");

        drillOut = chartRoot.tooltipContainer.children.push(am5.Button.new(chartRoot, {
          x: am5.p100,
          y: 0,
          centerX: am5.p100,
          centerY: 0,
          paddingTop: 18,
          paddingBottom: 18,
          paddingLeft: 12,
          paddingRight: 12,
          dx: -20,
          dy: 20,
          themeTags: ["zoom"],
          icon: am5.Graphics.new(chartRoot, {
            themeTags: ["button", "icon"],
            strokeOpacity: 0.7,
            draw: function(display) {
              display.moveTo(0, 0);
              display.lineTo(12, 0);
            }
          })
        }));
        drillOut.events.on("click", function() {
            currentSeries.hide();
            if (currentSeries) {
                if(currentSeries.data.values){
                    if (currentSeries.data.values[0].type === "subregion"){
                        mapChart.goHome();
                        drillOut.hide();
                        currentSeries = regionalSeries.series
                    }
                    else if(currentSeries.data.values[0].type === "place"){
                        let regionalDrillUp = regionalSeries[currentSeries.data.values[0].drillup].drillup
                        mapChart.zoomToGeoPoint({
                          latitude: regionalSeries[regionalDrillUp].geometry.coordinates[1],
                          longitude: regionalSeries[regionalDrillUp].geometry.coordinates[0]
                        }, 16, true)
                        currentSeries = regionalSeries[regionalDrillUp].series
                    }
                }
            }
            else{
                // not sure?
            }
            FilterSeriesByYear()
            currentSeries.show();
        })
        drillOut.hide();

        chartRoot.setThemes([
          am5themes_Animated.new(chartRoot)
        ]);


        mapChart = chartRoot.container.children.push(am5map.MapChart.new(chartRoot, {
            panX: "rotateX",
            panY: "translateY",
            projection: am5map.geoNaturalEarth1(),
            minZoomLevel: 1,
            maxZoomLevel: 256
        }));

        let mapGlobeSwitchContainer = mapChart.children.push(
          am5.Container.new(chartRoot, {
            layout: chartRoot.horizontalLayout,
            x: 20,
            y: 40
          })
        );

        // Add labels and controls
        mapGlobeSwitchContainer.children.push(
          am5.Label.new(chartRoot, {
            centerY: am5.p50,
            text: "Map"
          })
        );

        let switchButton = mapGlobeSwitchContainer.children.push(
          am5.Button.new(chartRoot, {
            themeTags: ["switch"],
            centerY: am5.p50,
            icon: am5.Circle.new(chartRoot, {
              themeTags: ["icon"]
            })
          })
        );

        switchButton.on("active", function () {
          if (!switchButton.get("active")) {
            mapChart.set("projection", am5map.geoNaturalEarth1());
            mapChart.set("panY", "translateY");
            mapChart.set("rotationY", 0);

            backgroundSeries.mapPolygons.template.set("fillOpacity", 0);
          } else {
            mapChart.set("projection", am5map.geoOrthographic());
            mapChart.set("panY", "rotateY");
            backgroundSeries.mapPolygons.template.set("fillOpacity", 0.1);
          }
        });

        mapGlobeSwitchContainer.children.push(
          am5.Label.new(chartRoot, {
            centerY: am5.p50,
            text: "Globe"
          })
        );

        let backgroundSeries = mapChart.series.push(am5map.MapPolygonSeries.new(chartRoot, {}));
        backgroundSeries.mapPolygons.template.setAll({
          fill: chartRoot.interfaceColors.get("alternativeBackground"),
          fillOpacity: 0,
          strokeOpacity: 0
        });

        backgroundSeries.data.push({
          geometry: am5map.getGeoRectangle(90, 180, -90, -180)
        });

        let polygonSeries = mapChart.series.push(
            am5map.MapPolygonSeries.new(chartRoot, {
                geoJSON: am5geodata_continentsHigh,
          })
        );
        polygonSeries.mapPolygons.template.setAll({
            fill: am5.color(0x6794dc),
            stroke: am5.color(0x6794dc),
            strokeWidth:0
        })

        let graticuleSeries = mapChart.series.push(
          am5map.GraticuleSeries.new(chartRoot, {})
        );
        graticuleSeries.mapLines.template.setAll({
          stroke: am5.color(0x000000),
          strokeOpacity: 0.1
        });

        let pointSeries = mapChart.series.push(am5map.MapPointSeries.new(chartRoot, {}));

        pointSeries.bullets.push(function () {
          let circle = am5.Circle.new(chartRoot, {
            radius: 4,
            tooltipY: 0,
            //fill: am5.color(0xffba00),
            stroke: chartRoot.interfaceColors.get("background"),
            strokeWidth: 2,
            tooltipText: "{title}"
          });

          return am5.Bullet.new(chartRoot, {
            sprite: circle
          });
        });

        am5.net.load('/chart/get-data/?dataset='+datasetLabel+'&chart='+chartType+'&count='+counting+'&filter='+JSON.stringify(paramValuesDict)).then(function(result){

            yearRange = [10000, -10000]

            let cd = am5.JSONParser.parse(result.response)

            regionalSeries ={
                markerData: [],
                series: createSeries("individuals")
            }

            currentSeries = regionalSeries.series
            let markerExists
            let regionalCoordinates
            let subregionalCoordinates
            let placeCoordinates
            am5.array.each(cd, function(dataItem){
                regionalCoordinates = [(Math.round(dataItem.longitude/10)*10).toFixed(0), (Math.round(dataItem.latitude/10)*10).toFixed(0)]
                subregionalCoordinates = [(Math.round(dataItem.longitude)).toFixed(1), (Math.round(dataItem.latitude)).toFixed(1)]
                placeCoordinates = [(Math.round(dataItem.longitude*10)/10).toFixed(2), (Math.round(dataItem.latitude*10)/10).toFixed(2)]

                if (dataItem.year < yearRange[0]){
                    yearRange[0] = dataItem.year
                }
                if (dataItem.year > yearRange[1]){
                    yearRange[1] = dataItem.year
                }

                if (regionalSeries[regionalCoordinates] === undefined){
                    regionalSeries[regionalCoordinates] = {
                        drillup: null,
                        target: regionalCoordinates,
                        type: "region",
                        individuals: 0,
                        markerData: [], //remember unique subregional coordinates within each region
                        geometry:{
                            type: "Point",
                            coordinates: regionalCoordinates
                        }
                    }
                    regionalSeries.markerData.push(regionalSeries[regionalCoordinates])
                }
                else{
                    //do nothing
                }

                if (regionalSeries[subregionalCoordinates] === undefined){
                    regionalSeries[subregionalCoordinates] = {
                        drillup: regionalCoordinates,
                        target: subregionalCoordinates,
                        type: "subregion",
                        individuals: 0,
                        markerData: [], //remember unique place coordinates within each subregion
                        geometry:{
                            type: "Point",
                            coordinates: subregionalCoordinates
                        }
                    }
                    regionalSeries[regionalCoordinates].markerData.push(regionalSeries[subregionalCoordinates])
                }
                else{
                    //do nothing
                }

                markerExists = false
                for(let p=0; p<regionalSeries[subregionalCoordinates].markerData.length; p++){
                    if (regionalSeries[subregionalCoordinates].markerData[p].geometry.coordinates.toString() === placeCoordinates.toString()){
                        regionalSeries[subregionalCoordinates].markerData[p].individualData.push(dataItem.year)
                        // regionalSeries[subregionalCoordinates].markerData[p].individuals = regionalSeries[subregionalCoordinates].markerData[p].individualData.length
                        markerExists = true
                        break
                    }
                }
                if(!markerExists){
                    regionalSeries[subregionalCoordinates].markerData.push({
                        drillup: subregionalCoordinates,
                        target: null,
                        type: "place",
                        individualData: [dataItem.year],
                        individuals: 0,
                        geometry: {
                          type: "Point",
                          coordinates: placeCoordinates
                        }
                    })
                }
            })
            regionalSeries.series.data.setAll(regionalSeries.markerData);

            //Must put the timeline slider stuff here so that it knows the year range of the data
            let yearSliderContainer = mapChart.children.push(am5.Container.new(chartRoot, {
              y: am5.p100,
              centerX: am5.p50,
              centerY: am5.p100,
              x: am5.p50,
              width: am5.percent(85),
              layout: chartRoot.horizontalLayout,
              paddingBottom: 10
            }));

            yearSlider = yearSliderContainer.children.push(am5.Scrollbar.new(chartRoot, {
                orientation: "horizontal"
            }))
            let startLabel = yearSlider.startGrip.children.push(am5.Label.new(chartRoot, {
              isMeasured: false,
              width: 100,
              fill: am5.color(0x000000),
              centerX: 50,
              centerY: 30,
              x: am5.p50,
              y: 0,
              textAlign: "center",
              populateText: true
            }))
            let endLabel = yearSlider.endGrip.children.push(am5.Label.new(chartRoot, {
              isMeasured: false,
              width: 100,
              fill: am5.color(0x000000),
              centerX: 50,
              centerY: 30,
              x: am5.p50,
              y: 0,
              textAlign: "center",
              populateText: true
            }))

            yearSlider.events.on("rangechanged", function () {
                let startYear = yearRange[0] + Math.round(yearSlider.get("start", 0) * (yearRange[1] - yearRange[0]))
                let startYearStr = startYear.toString()
                if(startYear < 0){
                    startYearStr = -1*startYear + " BC"
                }
                let endYear = yearRange[0] + Math.round(yearSlider.get("end", 0) * (yearRange[1] - yearRange[0]))
                let endYearStr = endYear.toString()
                if(endYear < 0){
                    endYearStr = -1*endYear + " BC"
                }

                startLabel.set("text", startYearStr);
                endLabel.set("text", endYearStr);

                let baseTitle = JSON.parse($("#jsChartTitle").html())
                let chartTitleObj = $("#chartTitle")
                if(yearSlider.get("start", 0) === 0 && yearSlider.get("end", 0) === 1){
                    chartTitleObj.text(baseTitle + " All Time")
                }
                else{
                    if(yearSlider.get("start", 0) === 0){
                        chartTitleObj.text(baseTitle + " Through " + endYearStr)
                    }
                    else if(yearSlider.get("end", 0) === 1){
                        chartTitleObj.text(baseTitle + " Since " + startYearStr)
                    }
                    else{
                        chartTitleObj.text(baseTitle + " From " + startYearStr + " to " + endYearStr)
                    }
                }
                FilterSeriesByYear()
            });
        })

        // Make stuff animate on load
        mapChart.appear(1000, 100);
    })
}

function createSeries(seriesName){
    // Create point series
    let pointSeries = mapChart.series.push(am5map.MapPointSeries.new(chartRoot, {
            valueField: seriesName,
            //calculateAggregates: true
        })
    );

    // Add marker
    let circleTemplate = am5.Template.new(chartRoot);
    pointSeries.bullets.push(function() {
        let container = am5.Container.new(chartRoot, {});

        let circle = container.children.push(am5.Circle.new(chartRoot, {
          radius: 10,
          fill: am5.color(0x68dc76),
          fillOpacity: 0.7,
          cursorOverStyle: "pointer",
          tooltipText: "({longitude}, {latitude}):\n[bold]{individuals} " + counting + "[\]"
        }, circleTemplate));

        circle.adapters.add("radius", function(radius, target) {
            if (target.dataItem.dataContext.individuals === 0) {
                return 0;
            }
            else {
                return 15*Math.log(target.dataItem.dataContext.individuals) + 5;
            }
        });

        let label = container.children.push(am5.Label.new(chartRoot, {
            text: "{individuals}",
            fill: am5.color(0xffffff),
            populateText: true,
            centerX: am5.p50,
            centerY: am5.p50,
            textAlign: "center",
        }));

        label.adapters.add("text", function(text, target) {
          if (target.dataItem.dataContext.individuals === 0) {
            return "";
          }
          else {
            return text;
          }
        });

        // Set up drill-down
        circle.events.on("click", function(ev) {
            // Determine what we've clicked on
            let data = ev.target.dataItem.dataContext

            let zoomLevel = 16
            if (data.type === "subregion"){
                zoomLevel = 128
            }

            //No target? Individual - nothing to drill down to further
            if (!data.target) {
                return;
            }

            // Create actual series if it hasn't been yet created
            if (!regionalSeries[data.target].series) {
                regionalSeries[data.target].series = createSeries("individuals");
                regionalSeries[data.target].series.data.setAll(data.markerData)
            }

            // Hide current series
            if (currentSeries) {
                currentSeries.hide();
            }

            mapChart.zoomToGeoPoint({
              latitude: data.geometry.coordinates[1],
              longitude: data.geometry.coordinates[0]
            }, zoomLevel, true)

            drillOut.show()

            // Show new target series
            currentSeries = regionalSeries[data.target].series;
            FilterSeriesByYear()
            currentSeries.show();
        });

        return am5.Bullet.new(chartRoot, {
            sprite: container,
            dynamic: true
        });
    });

    // Add heat rule for circles
    // pointSeries.set("heatRules", [{
    //     target: circleTemplate,
    //     dataField: "value",
    //     key: "radius",
    //     customFunction: function (sprite, min, max, value){
    //         if(value === 0){
    //             sprite.hide()
    //         }
    //         else{
    //             console.log(value + " " + 30*Math.log(value)+3 + " " + min + " " + max)
    //             sprite.set("radius", 30*Math.log(value)+3)
    //             sprite.show()
    //         }
    //     }
    // }])
    return pointSeries;
}

function FilterSeriesByYear(){

    let startYear = yearRange[0] + Math.round(yearSlider.get("start", 0) * (yearRange[1] - yearRange[0]))
    let endYear = yearRange[0] + Math.round(yearSlider.get("end", 0) * (yearRange[1] - yearRange[0]))

    Object.keys(regionalSeries).forEach(function(coords){
        if(regionalSeries[coords].type === "region"){
            regionalSeries[coords].individuals = 0
            for(let sub=0; sub<regionalSeries[coords].markerData.length; sub++) {
                regionalSeries[coords].markerData[sub].individuals = 0
                for (let p = 0; p < regionalSeries[coords].markerData[sub].markerData.length; p++){
                    regionalSeries[coords].markerData[sub].markerData[p].individuals = 0
                    for (let y = 0; y < regionalSeries[coords].markerData[sub].markerData[p].individualData.length; y++) {
                        let individualYear = regionalSeries[coords].markerData[sub].markerData[p].individualData[y]
                        if (startYear <= individualYear && individualYear <= endYear) {
                            regionalSeries[coords].markerData[sub].markerData[p].individuals++
                            regionalSeries[coords].markerData[sub].individuals++
                            regionalSeries[coords].individuals++
                        }
                    }
                }
                regionalSeries[coords].markerData[sub].geometry.coordinates = FindCenter(regionalSeries[coords].markerData[sub].markerData)
            }
            regionalSeries[coords].geometry.coordinates = FindCenter(regionalSeries[coords].markerData)
        }
    })

    for (let i=0; i<currentSeries.dataItems.length; i++){
        let iTarget
        if(currentSeries.dataItems[i].dataContext.target){
            iTarget = currentSeries.dataItems[i].dataContext.target
            currentSeries.data.setIndex(i, {
                geometry: regionalSeries[iTarget].geometry,
                individuals: regionalSeries[iTarget].individuals,
                markerData: regionalSeries[iTarget].markerData,
                target: iTarget,
                drillup: regionalSeries[iTarget].drillup,
                type: regionalSeries[iTarget].type
                }
            )
        }
        else{
            iTarget = currentSeries.dataItems[i].dataContext.drillup
            for (let m=0; m<regionalSeries[iTarget].markerData.length; m++){
                if (regionalSeries[iTarget].markerData[m].geometry.coordinates === currentSeries.dataItems[i].dataContext.geometry.coordinates){
                    currentSeries.data.setIndex(i, {
                        geometry: regionalSeries[iTarget].markerData[m].geometry,
                        individualData: regionalSeries[iTarget].markerData[m].individualData,
                        individuals: regionalSeries[iTarget].markerData[m].individuals,
                        markerData: regionalSeries[iTarget].markerData[m].markerData,
                        target: null,
                        drillup: regionalSeries[iTarget].markerData[m].drillup,
                        type: regionalSeries[iTarget].markerData[m].type
                        }
                    )
                }
            }
        }

    }
}

function FindCenter(points){
    let totalLon=0
    let totalLat=0
    let totalPoints = 0
    for(let p=0; p< points.length; p++){
        if (points[p].individuals > 0){
            totalLon += parseFloat(points[p].geometry.coordinates[0])
            totalLat += parseFloat(points[p].geometry.coordinates[1])
            totalPoints++
        }
    }
    return [totalLon/totalPoints, totalLat/totalPoints]
}
