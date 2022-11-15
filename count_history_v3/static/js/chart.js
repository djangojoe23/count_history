function GetChartData(){
    $("#chartTitlesDiv").load('/chart/get-titles/?dataset='+datasetLabel+'&chart='+chartType+'&count='+counting+'&filter='+JSON.stringify(paramValuesDict), function() {
        $('#chartTitle').html(JSON.parse($('#jsChartTitle').text()))
        $('#chartSubtitle').html(JSON.parse($('#jsChartSubtitle').text()))
        if($("#chartVisual").html().length > 0 && chartRoot != null){
            chartRoot.dispose()
            chartRoot = null
        }

        if(datasetLabel && counting){
            if (chartType === "line"){
                GenerateLineChart()
            }
            else if(chartType === "map"){
                GenerateMapChart()
            }
        }
    })
}
