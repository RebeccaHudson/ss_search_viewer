//d3 and jquery should already be included and available.

//plottingData
function cloneSVGSkeleton(plottingData){
    var nPlots = plottingData.length;
    var nodeToClone = $("svg.target").parent().first();
    //start the count at 1, there's already 1 plot on the page.
    for ( i = 0 ; i < nPlots; i++){
        var cloned = nodeToClone.clone(true); 
        //true for 'deep' copy of child elements
        var plot_id_to_use = plottingData[i].plot_id_str;
        //console.log("creating an empty plot for " + plot_id_to_use);
        //cloned.children().first().attr("id","target-"+i);
        cloned.children().first().attr("id", "target-"+plot_id_to_use);
        //console.log("cloned element " + cloned);   
        cloned.appendTo(d3.select("div#plots"));
    }
}
