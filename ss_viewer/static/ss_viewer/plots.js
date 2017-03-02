//Draws plots in-line inside the table of search results.
function drawPlotsInline(){
   /* plotting data from each of the searched items.*/
   //moved into a function for calling when AJAX results are returned.
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
       //console.log("preparing for one plot.. " + data_for_one_plot ); 
   });
   cloneSVGSkeleton(plottingData);
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


function setupPlotsForSearchResults(){
   //the two blocks below can be factored together.
   var plottingData = [];
   $("td.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
   });
   cloneSVGSkeleton(plottingData);
   $("svg#target-0").hide();
   $("svg#target-refhalf-0").hide();
   $("svg#target-snphalf-0").hide();
   for ( var n = 0; n < plottingData.length; n++){
       var targetSVGid = "target-" + plottingData[n].plot_id_str;
       var halfPlotId = 'target-refhalf-' +  plottingData[n].plot_id_str; //change to halfRefPlot
       var halfSnpPlotId = 'target-snphalf-' +  plottingData[n].plot_id_str;

       //console.log("creating plot for id : " + targetSVGid);
       makeAPlot(plottingData[n], targetSVGid);
       makeAHalfPlot(plottingData[n], halfPlotId );
       makeAHalfPlotSNP(plottingData[n], halfSnpPlotId );
       if ( n > 0 ){
         //console.log("adding hidden class to " + targetSVGid);
         $("#"+targetSVGid).parent().addClass("hidden");
       }else {
         $("#save_plot").attr('style', 'display: inline;');
         $("#"+targetSVGid).parent().addClass("show-plot");
       } 
       var plotToMove = $("#"+targetSVGid).parent().detach();
       var halfPlotToMove = $("#" + halfPlotId).parent().detach();
       var halfSnpPlotToMove = $("#" + halfSnpPlotId).parent().detach();

       var idOfPlotTarget = "#" + targetSVGid.replace('target-', 'show_plot_');
       var idOfHalfPlotTarget = "#ref-plot-" + plottingData[n].plot_id_str;
       var idOfHalfSnpPlotTarget = "#snp-plot-" + plottingData[n].plot_id_str;

       var putPlotHere = $(idOfPlotTarget).parent();
       var putHalfPlotHere = $(idOfHalfPlotTarget);
       var putHalfSnpPlotHere = $(idOfHalfSnpPlotTarget);

       //console.log("trying to put half-plot " + putHalfPlotHere);
       console.log(putHalfPlotHere);
       plotToMove.appendTo(putPlotHere);

       halfPlotToMove.appendTo(putHalfPlotHere);
       halfSnpPlotToMove.appendTo(putHalfSnpPlotHere);

       halfPlotToMove.find('svg').show();
       halfSnpPlotToMove.find('svg').show();
   } 
   console.log("completed plotting!");
  }
