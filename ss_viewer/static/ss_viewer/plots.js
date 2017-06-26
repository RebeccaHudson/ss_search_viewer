//Draws plots in-line inside the table of search results.
// this is called on document.ready()
//  consider changing name:    setupPlotsBeforeSearch
function drawPlotsInline(){
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
   });
   cloneSVGSkeleton(plottingData);  
   //the only thing cloneSVGSkeleton does with plottingData is get its length.
   //hide all 3 of the original skeleton plots.
   $("svg#target-0").hide();
   $("svg#target-stacked-plot-0").hide();
}

//adapted from: https://spin.atomicobject.com/2014/01/21/convert-svg-to-png/
function svgImage(xml) {
  var image = new Image();
  image.src = 'data:image/svg+xml;base64,' + window.btoa(xml);
  image.onload = function() {
    var canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    var context = canvas.getContext('2d');

    //400 - 30 = 370
    context.drawImage(image, 0, -30);

    var fname = $('div.show-plot svg').attr('id').replace('target-', '');
    var a = document.createElement('a');
    a.download = fname + ".png";
    a.href = canvas.toDataURL('image/png');
    document.body.appendChild(a);
    a.click();
  }
}

//this happens when search results are returned.
//this should recieve 'plottingData' as a parameter to make it more testable.
function setupPlotsForSearchResults(){
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
   });
   cloneSVGSkeleton(plottingData);
   //how many SVGs got cloned?  
   var stackedPlotClones = $('#target-stacked-plot-');
   //there should be matches for target-stacked-plot at this point.
   for ( var n = 0; n < plottingData.length; n++){
       var id_str = plottingData[n].plot_id_str.replace(/\:/g, '\\:');
       var targetSVGid = "target-" + id_str;                  
       var fullStackPlotId = 'target-stacked-plot-' + id_str; 

       makeAPlot(plottingData[n], targetSVGid);
       drawFixedWidthCompositePlot(plottingData[n], fullStackPlotId);
       
       if ( n > 0 ){
         $("#"+targetSVGid).parent().addClass("hidden");
       }else {
         $("#save_plot").attr('style', 'display: inline;');
         $("#"+targetSVGid).parent().addClass("show-plot");
       } 

       //try: not moving the main plot into an 'inline' position.
       //     see if checkedRow plot downloads can still be made to work.
       var fullStackPlotToMove = $("#" + fullStackPlotId).parent().detach();
       //how does the bulk download find this plot in order to download it?

       var idOfFullStackPlotTarget = "#stacked-plot-" + id_str;
       var putFullStackPlotHere = $(idOfFullStackPlotTarget);

       fullStackPlotToMove.appendTo(putFullStackPlotHere);
       fullStackPlotToMove.find('svg').show();
   } 
  }
