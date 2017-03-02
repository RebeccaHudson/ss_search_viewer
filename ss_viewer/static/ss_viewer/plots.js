//Draws plots in-line inside the table of search results.
// this is called on document.ready()
//  consider changing name:    setupPlotsBeforeSearch
function drawPlotsInline(){
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
       //console.log("preparing for one plot.. " + data_for_one_plot ); 
   });
   cloneSVGSkeleton(plottingData);  
   //the only thing cloneSVGSkeleton does with plottingData is get its length.
 
   //hide all 3 of the original skeleton plots.
   $("svg#target-0").hide();
   $("svg#target-refhalf-0").hide();
   $("svg#target-snphalf-0").hide();
}

//adapted from: https://spin.atomicobject.com/2014/01/21/convert-svg-to-png/
function svgImage(xml) {
  var image = new Image();
  image.src = 'data:image/svg+xml;base64,' + window.btoa(xml);
  //window.btoa(unescape(encodeURIComponent(xml)))}
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
function setupPlotsForSearchResults(){
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
   });
   cloneSVGSkeleton(plottingData);
   for ( var n = 0; n < plottingData.length; n++){
       var targetSVGid = "target-" + plottingData[n].plot_id_str;
       var halfPlotId = 'target-refhalf-' +  plottingData[n].plot_id_str; //change to halfRefPlot
       var halfSnpPlotId = 'target-snphalf-' +  plottingData[n].plot_id_str;

       makeAPlot(plottingData[n], targetSVGid);
       makeAHalfPlot(plottingData[n], halfPlotId );
       makeAHalfPlotSNP(plottingData[n], halfSnpPlotId );
       if ( n > 0 ){
         $("#"+targetSVGid).parent().addClass("hidden");
       }else {
         $("#save_plot").attr('style', 'display: inline;');
         $("#"+targetSVGid).parent().addClass("show-plot");
       } 

       //try: not moving the main plot into an 'inline' position.
       //     see if checkedRow plot downloads can still be made to work.
       var halfPlotToMove = $("#" + halfPlotId).parent().detach();
       var halfSnpPlotToMove = $("#" + halfSnpPlotId).parent().detach();

       //how does the bulk download find this plot in order to download it?

       var idOfHalfPlotTarget = "#ref-plot-" + plottingData[n].plot_id_str;
       var idOfHalfSnpPlotTarget = "#snp-plot-" + plottingData[n].plot_id_str;

       var putHalfPlotHere = $(idOfHalfPlotTarget);
       var putHalfSnpPlotHere = $(idOfHalfSnpPlotTarget);

       halfPlotToMove.appendTo(putHalfPlotHere);
       halfSnpPlotToMove.appendTo(putHalfSnpPlotHere);

       halfPlotToMove.find('svg').show();
       halfSnpPlotToMove.find('svg').show();
   } 
   console.log("completed plotting!");
  }
