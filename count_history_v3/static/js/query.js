$(document).ready(function() {

    // Initialize the select dropdowns for both the dataset and the chart type
    $("#datasetSelect, #chartSelect, #countSelect").select2({
        theme: "bootstrap-5",
        placeholder: $(this).data('placeholder'),
        width: '100%',
        minimumResultsForSearch: Infinity,
        selectionCssClass: 'select2--small',
        dropdownCssClass: 'select2--small',
    })
    $('#datasetSelect, #chartSelect, #countSelect').on('select2:select', function(e){
        // What happens when the dataset, chart type, or count is selected by user?
        //UpdateURLandVariables(e.target.id)
    })


    // If there is a valid dataset in the URL, then select it in the dropdown.
    let datasetSelectObj = $('#datasetSelect')
    // If not, make sure no dataset is selected.
    datasetSelectObj.val(datasetLabel).trigger('change')

    datasetSelectObj.on('change', function () {
        // What happens when the dataset is changed?
        let chartSelectObj = $('#chartSelect')
        chartSelectObj.prop('disabled', false)
        let datasetSelectData = $('#datasetSelect').select2('data')
        if (datasetSelectData.length > 0){
            datasetLabel = datasetSelectData[0].id
        }
        else{
            datasetLabel = null
        }
        $('#queryParameters').empty()
        chartSelectObj.load('/query/chart-options/?dataset='+datasetLabel, function(){
            if (chartSelectObj.find("option[value='" + chartType + "']").length){
                chartSelectObj.val(chartType).trigger('change')
            }
            else{
                chartSelectObj.val('').trigger('change')
            }
        })
    });

    // If there is a valid chart in the URL (and valid dataset), then select it in the dropdown.
    let chartSelectObj = $('#chartSelect')
    // If not, make sure no chart is selected.
    chartSelectObj.val(chartType).trigger('change')

    chartSelectObj.on('change', function () {
        // What happens when the chart type is changed?
        let chartSelectData = $('#chartSelect').select2('data')
        if (chartSelectData.length > 0){
            chartType = chartSelectData[0].id
        }
        else{
            chartType = null
        }
        $('#queryParameters').empty()
        let countSelectObj = $('#countSelect')
        countSelectObj.prop('disabled', false)
        countSelectObj.load('/query/count-options/?dataset='+datasetLabel+'&chart='+chartType, function(){
            countSelectObj.val('').trigger('change')
            $('#addParameterButton').prop('disabled', true)
        })
    });

    // If there is a valid count option in the URL (and valid dataset and chart), then select it in the dropdown.
    let countSelectObj = $('#countSelect')
    // If not, make sure no count is selected.
    countSelectObj.val(counting).trigger('change')

    countSelectObj.on('change', function () {
        // What happens when the count option is changed?
        let countSelectData = $('#countSelect').select2('data')
        if (countSelectData.length > 0){
            counting = countSelectData[0].id
            $('#addParameterButton').prop('disabled', false)
        }
        else{
            counting = null
            $('#addParameterButton').prop('disabled', true)
        }
        UpdateURLandVariables("count select changed")
    });

    //If there are valid parameters and associated values in the URL, create dropdown and multi-selects for them
    let allSelectTwos= $(".select-two")
    let paramIndex = 0
    let paramCounts = {}
    for (let p=0; p<paramOrder.length; p++){
        paramCounts[paramOrder[p]] = 0
    }
    for(let s=0; s<allSelectTwos.length; s++) {
        let selectTwoObj = $(allSelectTwos[s])
        let selectTwoID = selectTwoObj.attr('id')
        if(!selectTwoObj.hasClass("select2-hidden-accessible")){
            if (selectTwoID.includes("ValueSelect")) {
                initializeValueSelect(selectTwoObj, paramValuesDict[paramOrder[paramIndex]][paramCounts[paramOrder[paramIndex]]])
                paramCounts[paramOrder[paramIndex]]++
                paramIndex++
            }else if(selectTwoID.includes("ParameterSelect")){
                initializeParameterSelect(selectTwoObj, paramOrder[paramIndex])
            }
        }
    }

    // What happens when the "Add Parameter" button is clicked?
    $('#addParameterButton').click(function(){
        let parameterHTML = null
        $.get('/query/parameter-filter/?dataset='+datasetLabel+'&chart='+chartType, function(data){
            parameterHTML = data
            $('#queryParameters').prepend(parameterHTML)
            let allSelectTwos= $(".select-two")
            for(let s=0; s<allSelectTwos.length; s++) {
                let selectTwoObj = $(allSelectTwos[s])
                let selectTwoID = selectTwoObj.attr('id')
                if(!selectTwoObj.hasClass("select2-hidden-accessible")){
                    if (selectTwoID.includes("ValueSelect")) {
                        initializeValueSelect(selectTwoObj, [])
                    }else if(selectTwoID.includes("ParameterSelect")){
                        initializeParameterSelect(selectTwoObj, '')
                    }
                }
            }
        })
    })

    UpdateURLandVariables("initial page load")
})

function initializeParameterSelect(selectObj, val){
    let selectID = selectObj.attr('id')
    let baseIDEnd = selectID.search("ParameterSelect")
    let baseID = selectID.substring(0, baseIDEnd)
    let valueSelectObj = $("#"+baseID+"ValueSelect")
    selectObj.select2({
        theme: 'bootstrap-5',
        width: 'element',
        placeholder: $(this).data('placeholder'),
        selectionCssClass: 'select2--small',
        dropdownCssClass: 'select2--small',
    })
    selectObj.on('change', function(){
        // What happens when a parameter select is changed?
        valueSelectObj.prop('disabled', false)
        valueSelectObj.val('').trigger('change')
    })
    selectObj.on('select2:select', function(){
        // What happens when a parameter select is selected by a user?
        //UpdateURLandVariables()
        if (valueSelectObj.select2('data').length > 0){
            UpdateURLandVariables("parameter selected")
        }
    })

    $("#"+baseID+"ParameterRemove").click(function(){
        // What happens when a parameter is removed from the filter?
        $("#"+baseID).remove()
        UpdateURLandVariables("remove parameter")
    })

    selectObj.val(val).trigger('change')
}

function initializeValueSelect(selectObj, vals){
    let selectID = selectObj.attr('id')
    let baseIDEnd = selectID.search("ValueSelect")
    let baseID = selectID.substring(0, baseIDEnd)
    selectObj.select2({
        theme: 'bootstrap-5',
        width: '100%',
        selectionCssClass: 'select2--small',
        dropdownCssClass: 'select2--small',
        closeOnSelect: true,
        allowClear: true,
        ajax:{
            delay: 100,
            url: '/query/parameter-values/',
            dataType: 'json',
            data:function(params){
                return {
                    dataset: datasetLabel,
                    parameter: $('#'+baseID+'ParameterSelect').val(),
                    search: params.term
                }
            },
            processResults: function(data){
                let searchResults = []
                $.each(data, function(index, item){
                    searchResults.push({
                        'id': item.id,
                        'text': item.text
                    })
                })
                return{
                    results: searchResults
                }
            }
        }
    })
    selectObj.on('change', function(){
        // What happens when a parameter value is changed?
    })
    selectObj.on('select2:select', function(){
        // What happens when a parameter value is selected?
        UpdateURLandVariables("parameter value select")
    })
    selectObj.on('select2:unselect', function(){
        // What happens when a parameter value is de-selected?
        UpdateURLandVariables("parameter value deselect")
    })

    if (vals.length > 0){
        selectObj.val(vals).trigger('change')
    }
    else{
        selectObj.prop("disabled", true)
    }

    $("#"+baseID+"ValueSeriesCheck").on("click", function(){
        console.log($(this).attr('id'))
        console.log("update data")
        console.log("update legend")
        console.log("update url with new query parameter (will also need to update initial page load code to react to this query parameter)")
    })
}

function UpdateURLandVariables(fromWho){
    console.log("Update URL from " + fromWho)

    let newURL
    if(window.location.host.search("counthistory") === -1){
        // Local development url
        newURL = new URL("http://"+window.location.host + window.location.pathname)
    }
    else{
        // Deployed url
        newURL = new URL("https://"+window.location.host + window.location.pathname)
    }

    //get dataset
    let currentSelection = $("#datasetSelect").select2('data')
    if (currentSelection.length > 0){
        datasetLabel = currentSelection[0].id
        newURL.searchParams.set("dataset", datasetLabel)
    }
    else{
        datasetLabel = null
    }

    //get chart
    currentSelection = $("#chartSelect").select2('data')
    if(currentSelection.length > 0){
        chartType = currentSelection[0].id
        newURL.searchParams.set("chart", chartType)
    }
    else{
        chartType = null
    }

    //get count
    currentSelection = $("#countSelect").select2('data')
    if(currentSelection.length > 0){
        counting = currentSelection[0].id
        newURL.searchParams.set("count", counting)
    }
    else{
        counting = null
    }

    //UPDATE CHART PREFERENCE OPTIONS BASED ON VARIABLES AND WHAT IS IN THE URL

    paramOrder = []
    paramValuesDict = {}
    let allParamFilters= $(".paramArticle")
    for(let a=0; a<allParamFilters.length; a++) {
        let baseID = $(allParamFilters[a]).attr('id')
        let paramSelectData = $('#'+baseID+'ParameterSelect').select2('data')
        let valueSelectData = $('#'+baseID+'ValueSelect').select2('data')
        $("#"+baseID+"ValueSeriesCheck").prop("disabled", counting.includes('|'))
        if (counting.includes('|') && $("#"+baseID+"ValueSeriesCheck").prop("checked")){
            $("#"+baseID+"ValueSeriesCheck").prop("checked", false)
        }

        if (paramSelectData.length > 0 && valueSelectData.length > 0) {
            paramOrder.push(paramSelectData[0].id)
            if (!(paramSelectData[0].id in paramValuesDict)) {
                paramValuesDict[paramSelectData[0].id] = []
            } else {
                // do nothing
            }

            let valuesSelected = []
            for (let v = 0; v < valueSelectData.length; v++) {
                valuesSelected.push(parseInt(valueSelectData[v].id))
            }
            paramValuesDict[paramSelectData[0].id].push(valuesSelected)

            newURL.searchParams.append(paramSelectData[0].id, valuesSelected.join('|'))
        }
        else{
            // do nothing
        }
    }

    window.history.replaceState(null, null, newURL)

    GetChartData()
}
