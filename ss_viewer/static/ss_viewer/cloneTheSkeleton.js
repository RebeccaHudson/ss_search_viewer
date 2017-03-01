//d3 and jquery should already be included and available.

//plottingData
function cloneSVGSkeleton(plottingData){
    var nPlots = plottingData.length;
    var nodeToClone = $("svg.target").parent().first();
    //add a half-plot nodeToClone
    var halfPlotToCloneRefHalf = $("svg#target-refhalf-0").parent().first(); 
    var halfPlotToCloneSnpHalf = $("svg#target-snphalf-0").parent().first(); 
    //
    //start the count at 1, there's already 1 plot on the page.
    for ( i = 0 ; i < nPlots; i++){
        var cloned = nodeToClone.clone(true); 
        //true for 'deep' copy of child elements
        //
        var clonedRefHalf =  halfPlotToCloneRefHalf.clone(true);
        var clonedSnpHalf =  halfPlotToCloneSnpHalf.clone(true);
        //
        var plot_id_to_use = plottingData[i].plot_id_str;
        //console.log("creating an empty plot for " + plot_id_to_use);
        //cloned.children().first().attr("id","target-"+i);
        cloned.children().first().attr("id", "target-"+plot_id_to_use);
        clonedRefHalf.children().first().attr("id", 
                                              "target-refhalf-"+plot_id_to_use);
        clonedSnpHalf.children().first().attr("id",
                                              "target-snphalf-"+plot_id_to_use);
        //console.log("cloned element " + cloned);   
        //put all of the plots into the same placeholder stack for now.
        //TODO: consider appending these to the correct place in the table
        //      of search results to begin with; they don't have to be 
        //      hidden/shown given these new requirements.
        cloned.appendTo(d3.select("div#plots"));
        clonedRefHalf.appendTo(d3.select("div#plots"));
        clonedSnpHalf.appendTo(d3.select("div#plots"));
    }
}
