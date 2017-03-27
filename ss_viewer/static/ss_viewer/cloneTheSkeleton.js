//d3 and jquery should already be included and available.

//TODO: plottingData is only passed in here to get at its length
//      change this such that only its length needs to be passed.
function cloneSVGSkeleton(plottingData){
    var nPlots = plottingData.length;
    var nodeToClone = $("svg.target").parent().first();

    //var halfPlotToCloneRefHalf = $("svg#target-refhalf-0").parent().first(); 
    //var halfPlotToCloneSnpHalf = $("svg#target-snphalf-0").parent().first(); 
    
    var fixedWidthStackToClone = $("svg#target-stacked-plot-0").parent().first();  //coming up blank
    for ( i = 0 ; i < nPlots; i++){
        //clone argument of "true" is for 'deep' copy of child elements
        var cloned = nodeToClone.clone(true); 
        
        //var clonedRefHalf =  halfPlotToCloneRefHalf.clone(true);
        //var clonedSnpHalf =  halfPlotToCloneSnpHalf.clone(true);
        var clonedFullScaled = fixedWidthStackToClone.clone(true);
 
        var plot_id_to_use = plottingData[i].plot_id_str;
        //console.log("creating an empty plot for " + plot_id_to_use);
        cloned.children().first().attr("id", "target-"+plot_id_to_use);//for the downloads
        //clonedRefHalf.children().first().attr("id", 
        //                                      "target-refhalf-"+plot_id_to_use);
        //clonedSnpHalf.children().first().attr("id",
        //                                      "target-snphalf-"+plot_id_to_use);
        clonedFullScaled.children().first().attr("id",
                                                 "target-stacked-plot-"+plot_id_to_use);
        //put all of the plots into the same placeholder stack for now.
        //TODO: consider appending these to the correct place in the table
        //      of search results to begin with; they don't have to be 
        //      hidden/shown given these new requirements.
        cloned.appendTo(d3.select("div#plots"));
        //clonedRefHalf.appendTo(d3.select("div#plots"));
        //clonedSnpHalf.appendTo(d3.select("div#plots"));
        clonedFullScaled.appendTo(d3.select("div#plots"));
    }
}
