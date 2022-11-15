function GenerateLineChart(){
    am5.ready(function() {
        chartRoot = am5.Root.new("chartVisual");
        let xAxisLabel = JSON.parse($('#jsChartXtitle').text())
        let yAxisLabel = JSON.parse($('#jsChartYtitle').text())

        chartRoot.setThemes([
            am5themes_Animated.new(chartRoot),
            am5themes_Material.new(chartRoot)
        ]);

        let chart = chartRoot.container.children.push(am5xy.XYChart.new(chartRoot, {
            panX: true,
            panY: true,
            wheelY: "zoomXY",
            layout: chartRoot.verticalLayout,
            pinchZoomX:true
        }));

        let yAxis = chart.yAxes.push(am5xy.ValueAxis.new(chartRoot, {
            maxDeviation: 0.5,
            extraMax: 0.05,
            extraMin: 0.05,
            renderer: am5xy.AxisRendererY.new(chartRoot, {}),
        }));
        yAxis.children.moveValue(am5.Label.new(chartRoot, {fontSize: "1.5em", text: yAxisLabel, rotation: -90, y: am5.p50, centerX: am5.p50 }), 0);

        let xAxis = chart.xAxes.push(am5xy.DateAxis.new(chartRoot, {
            maxDeviation: 0.5,
            baseInterval: {
              timeUnit:  xAxisLabel.toLowerCase(),
              count: 1
            },
            extraMax: 0.1,
            extraMin: 0.1,
            renderer: am5xy.AxisRendererX.new(chartRoot, {}),
            tooltip: am5.Tooltip.new(chartRoot, {

            })
        }));
        xAxis.children.push(am5.Label.new(chartRoot, { fontSize: "1.5em", text: xAxisLabel, x: am5.p50, centerX: am5.p50 }));


        // Create modal for a "no data" note
        let modal = am5.Modal.new(chartRoot, {
            content: "No data for " + yAxisLabel.toLowerCase() + " "  + $("#chartSubtitle").text().toLowerCase() + "."
        })


        chart.set("scrollbarX", am5.Scrollbar.new(chartRoot, {
            orientation: "horizontal"
        }));

        chart.set("scrollbarY", am5.Scrollbar.new(chartRoot, {
            orientation: "vertical",
        }));

        let legend = chart.children.push(am5.Legend.new(chartRoot, {
            centerX: am5.p100,
            x: am5.p100,
            clickTarget: "none",
            useDefaultMarker: true
        }))

        legend.itemContainers.template.events.on("pointerover", function(e) {
            let itemContainer = e.target;

            // As series list is data of a legend, dataContext is series
            let series = itemContainer.dataItem.dataContext;

            chart.series.each(function(chartSeries) {
                if (chartSeries !== series) {
                    chartSeries.bulletsContainer.hide()
                    chartSeries.strokes.template.setAll({
                        strokeOpacity: 0.15,
                        stroke: am5.color(0x000000)
                    });
                } else {
                    chartSeries.strokes.template.setAll({
                        strokeWidth: 3
                    });
                }
            })
        })

        // When legend item container is unhovered, make all series as they are
        legend.itemContainers.template.events.on("pointerout", function(e) {
            chart.series.each(function(chartSeries) {
                chartSeries.bulletsContainer.show()
                chartSeries.strokes.template.setAll({
                  strokeOpacity: 1,
                  strokeWidth: 1,
                  stroke: chartSeries.get("fill")
                });
            });
        })

        let cd = null
        am5.net.load('/chart/get-data/?dataset='+datasetLabel+'&chart='+chartType+'&count='+counting+'&filter='+JSON.stringify(paramValuesDict)).then(function(result) {
            cd = am5.JSONParser.parse(result.response)
            let allXValues = []
            for (let x=0; x<Object.keys(cd).length; x++) {
                allXValues.push(parseInt(Object.keys(cd)[x]))
            }
            allXValues.sort(function(a, b){return a-b})

            let chartData = []
            // Set data
            if (xAxisLabel === "Year"){
                let dateObj = null
                let pointDict = {}
                for (let i=0; i<allXValues.length; i++){
                    pointDict = {}
                    dateObj = new Date(allXValues[i], 0, 1)
                    dateObj.setFullYear(allXValues[i])
                    pointDict["year"] = dateObj.getTime()
                    for (let [series, value] of Object.entries(cd[allXValues[i]])) {
                        pointDict[series] = value
                    }
                    chartData.push(pointDict)
                }
            }

            createStackedSeries(chart, legend, chartData, xAxis, yAxis, modal, "Births", "births")
            createStackedSeries(chart, legend, chartData, xAxis, yAxis, modal, "Deaths", "deaths")
        })

        chart.appear(1000, 100);
    });
}

function createStackedSeries(chart, legend, chartData, xAxis, yAxis, modal, seriesName, seriesField){
    let series = chart.series.push(am5xy.LineSeries.new(chartRoot, {
        name: seriesName,
        xAxis: xAxis,
        yAxis: yAxis,
        valueYField: seriesField,
        valueXField: "year",
        legendValueText: "{valueY}",
        tooltip: am5.Tooltip.new(chartRoot, {
          pointerOrientation: "horizontal",
          labelText: "[bold]{name}[/]\n{categoryX}: {valueY}"
        })
    }));

    series.strokes.template.setAll({
        strokeWidth: 1,
    });

    series.events.on("datavalidated", function(ev) {
      let series = ev.target;
      if (ev.target.data.length < 1) {
        // Show modal
        modal.open();
      }
      else {
        // Hide modal
        modal.close();
      }
    })

    series.bullets.push(function() {
        let circle = am5.Circle.new(chartRoot, {
            radius: 4,
            fill: series.get("fill"),
            //stroke: root.interfaceColors.get("background"),
            strokeWidth: 3
        });

        return am5.Bullet.new(chartRoot, {
            sprite: circle
        });
    });

    let cursor = chart.set("cursor", am5xy.XYCursor.new(chartRoot, {
        xAxis: xAxis,
        yAxis: yAxis,
        behavior: "none",
        snapToSeries: [series]
    }));
    cursor.lineY.set("visible", false);

    series.data.setAll(chartData);
    series.appear(1000);

    legend.data.push(series)
}

function UpdateLegend(){
    console.log("i made it this far")
}
