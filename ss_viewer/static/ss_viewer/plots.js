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
    context.drawImage(image, 0, 0);

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
   $("div.plotting_data" ).each(function() {
       var data_for_one_plot = this.textContent;
       onePlotData = jQuery.parseJSON(data_for_one_plot);
       plottingData.push(onePlotData);
       console.log("added one bit of plotting data.. ");
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

function downloadSinglePlot(e){
   //get a reference to this row's plot. 
   /*console.log("called downloadSinglePlot");
   console.log("following, is e: ");
   console.log(e);
   console.log("following, is e.target: ");
   console.log(e.target);

   */

   console.log("following, is $(e.target).attr('id'): ");
   console.log($(e.target).attr('id'));
   var target_id = $(e.target).attr('id').replace('download-plot', 'target');
   console.log("target_id" + target_id); 
   var svg = document.querySelector('svg#' + target_id);
   //var svg = document.querySelector('svg#target-0');
   svg = svg.cloneNode(true); //the true parameter specifies a deep copy
   svg.setAttribute('id', 'tempSVG');
   var defs = d3.select(svg).insert("defs", ":first-child").append("marker")
                                   .attr("id","Triangle")
                                   .attr("markerWidth","5")
                                   .attr("markerHeight","3")
                                   .attr("stroke", "#08519c")
                                   .attr("orient", "auto")
                                   .attr("viewBox", "0 0 10 10")
                                   .attr('refX', '1')
                                   .attr('refY', '5')
                                   .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z");
          
   var canvas = document.getElementById('canvas');
   canvas.setAttribute('width',  $("#target-0").attr('width'));

   var ctx = canvas.getContext('2d');

   // Reset the canvas to remove any plots drawn before this one 
  //           //taken from :http://www.html5canvastutorials.com/advanced/html5-clear-canvas/ 
   ctx.clearRect(0, 0, canvas.width, canvas.height);
   var xmlData = (new XMLSerializer()).serializeToString(svg);
   var image = new Image();
   image.src = 'data:image/svg+xml;base64,' + window.btoa(xmlData);
   image.onload = function() {
       var canvas = document.createElement('canvas');
       canvas.width = image.width;
       canvas.height = image.height;
       var context = canvas.getContext('2d');
        /*context.drawImage(image, 0, -30);*/
       context.drawImage(image, 0, 0);  /* add 50*/
       //var fname = "{{ id_str }}";
       var fname = target_id;
       console.log('name of saved plot file: ' + fname);
       var a = document.createElement('a');
       a.download = fname + ".png";
       a.href = canvas.toDataURL('image/png');
       document.body.appendChild(a);
       a.click();
  }

}


