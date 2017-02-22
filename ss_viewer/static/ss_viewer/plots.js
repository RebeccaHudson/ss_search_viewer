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
       for ( var n = 0; n < plottingData.length; n++){
           var targetSVGid = "target-" + plottingData[n].plot_id_str;
           //console.log("creating plot for id : " + targetSVGid);
           makeAPlot(plottingData[n], targetSVGid);
           if ( n > 0 ){
             //console.log("adding hidden class to " + targetSVGid);
             $("#"+targetSVGid).parent().addClass("hidden");
           }else {
             //$("#save_plot").attr('style', 'display: inline;');
             $("#"+targetSVGid).parent().addClass("show-plot");
           } 
       } 
       console.log("completed plotting!");
    }

    //add this as an event listener for the inline plot downloads.
    //for the 'download plot' button that's inline.
    function handleInlinePlotDownload(){
         console.log("hit the function to  handleInlinePlotDownload");
         var svg = document.querySelector('div.show-plot > svg');
         svg = svg.cloneNode(true); //makes a deep copy.
         svg.setAttribute("id", "tempSVG");

         var defs = d3.select(svg).insert("defs", ":first-child").append("marker")
                                   .attr("id","Triangle")
                                   .attr("markerWidth","5")
                                   .attr("markerHeight","3")
                                   .attr("stroke", "blue")
                                   .attr("orient", "auto")
                                   .attr("viewBox", "0 0 10 10")
                                   .attr('refX', '1')
                                   .attr('refY', '5')
                                   .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z");
          
          var canvas = document.getElementById('canvas');
          canvas.setAttribute('width',  $("div.show-plot svg").attr('width'));

          var ctx = canvas.getContext('2d');

          // Reset the canvas to remove any plots drawn before this one 
          //taken from :http://www.html5canvastutorials.com/advanced/html5-clear-canvas/ 
          ctx.clearRect(0, 0, canvas.width, canvas.height);

     
          var data = (new XMLSerializer()).serializeToString(svg);
          svgImage(data);
    }//end of 'Download Plot' button click event listener.
    //end of the plot downloading code.


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
        $("td.show_plots > button[id^='show_plot']").click(function(e) {
            var plot_button_id = e.target.attributes.getNamedItem('id').value;
            var plot_str = plot_button_id.replace('show_plot_', '');
            console.log("plot_str: " + plot_str);
            /*  hiding the shown plot breaks if it's not there..*/
            var currently_shown_plot = $("div.show-plot");
            if (currently_shown_plot.length > 0){
                currently_shown_plot.removeClass('show-plot');
                currently_shown_plot.addClass('hidden'); 
                var download_button_to_hide = currently_shown_plot
                                             .parent()
                                             .find('button[id^="download_plot"]');
                download_button_to_hide.hide();
            }
            var id_of_plot_svg = 'target-'.concat(plot_str); 
            var plot_selector = 'svg#'.concat(id_of_plot_svg);
            console.log("show plot was clicked, id = " + id_of_plot_svg);
            var div_to_show_now = $(plot_selector).parent();
            console.log("div_to_show_now = ");
            console.log( div_to_show_now );
            var download_button =  div_to_show_now.parent().find('button[id^="download_plot"]');
            download_button.show();
            
            div_to_show_now.removeClass('hidden');
            div_to_show_now.addClass('show-plot');
            $(plot_selector).attr('style', 'display: inline;');
        }); 

        var download_plot_buttons = $("td.show_plots > button[id^='download_plot']");
        download_plot_buttons.click(function(e) {
                  handleInlinePlotDownload();
         }); 
        download_plot_buttons.hide(); //show when the corresponding 'show plot' is clicked.
        console.log("hiding the download buttons.");
 
       var plottingData = [];
       $("td.plotting_data" ).each(function() {
           var data_for_one_plot = this.textContent;
           onePlotData = jQuery.parseJSON(data_for_one_plot);
           plottingData.push(onePlotData);
       });
       cloneSVGSkeleton(plottingData);
       $("svg#target-0").hide();
       for ( var n = 0; n < plottingData.length; n++){
           var targetSVGid = "target-" + plottingData[n].plot_id_str;
           //console.log("creating plot for id : " + targetSVGid);
           makeAPlot(plottingData[n], targetSVGid);
           if ( n > 0 ){
             //console.log("adding hidden class to " + targetSVGid);
             $("#"+targetSVGid).parent().addClass("hidden");
           }else {
             $("#save_plot").attr('style', 'display: inline;');
             $("#"+targetSVGid).parent().addClass("show-plot");
           } 
           var plotToMove = $("#"+targetSVGid).parent().detach();
           var idOfPlotTarget = "#" + targetSVGid.replace('target-', 'show_plot_');
           var putPlotHere = $(idOfPlotTarget).parent();
           plotToMove.appendTo(putPlotHere);
       } 
       console.log("completed plotting!");
      }
