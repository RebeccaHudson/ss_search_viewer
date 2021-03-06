//Clones the node containing the plot to be added to the ZIP. 
//adds definitions for the Arrowhead markers.
//sets up an HTML <canvas> element, including appropriate width,
//serizlizes the SVG copy into a string of XML.
function setupBulkPlotDownload(svg){
   //console.log("bulk download for svg selector: " + svg );
   svg = svg.cloneNode(true); //makes a deep copy.
   svg.setAttribute("id", "tempSVG");
   var defs = d3.select(svg).insert("defs", ":first-child").append("marker")
                             .attr("id","Triangle")
                             .attr("markerWidth","5")
                             .attr("markerHeight","3")
                             .attr("stroke", "blue")
                             .attr("orient", "auto")
                             .attr("viewBox", "0 0 10 10")
                             .attr("refX", "1")
                             .attr("refY", "5")
                             .append("path").attr("d", "M 0 0 L 10 5 L 0 10 z");
    svg.setAttribute('style', 'display:inline;'); //unhide, or images will be BLANK!
    var data = (new XMLSerializer()).serializeToString(svg);
    return data;
}

function checkedRowPlotDownload(){
    //factor out into function that just appends the spinner.
    var images = [];
    var counter = 0;
    var targets = $('svg[id^="target"].target');
    checkedTargets = []; 
    for (var i = 1; i < targets.length; i++){ //skip over the skeleton, target-0
       //the following depends on the structure of the data table.           
       var idToUse = targets[i].id.replace('target-', '').replace(/\:/g, '\\:');;
       var checky = $("input#" + idToUse); 
       checky = checky[0]; 
       if ( checky.checked == true ){
          checkedTargets.push(targets[i]); 
       }
    }
    if (checkedTargets.length == 0){
        alert("No plots are checked. No download will be created.");
    }else{
        show_or_hide_spinner(true);
    }
 
    for (var i = 0; i < checkedTargets.length; i++) {
       convertImgToBase64URL(checkedTargets[i], function (base64Img, fname_for_plot) {
         var dataForOnePlot = base64Img.replace("data:image/png;base64,", '');
         images.push({
           data: dataForOnePlot,
            tag: fname_for_plot
         });
         counter++;
         if (counter == (checkedTargets.length)) {
           createArchive(images);
         }
       });
     }

}      
//working answer for this tough problem (above) adapted from:
//http://stackoverflow.com/questions/31384408/
//     how-to-get-multiple-files-via-ajax-and-download-them-as-a-zip-file-via-javascrip 


//true to check all boxes; false to uncheck all boxes.
function hitAllPlotCheckboxes(trueOrFalse){
   var checkboxes = $('input[type="checkbox"]').prop('checked', trueOrFalse);   
}

// based on the same example cited for bulkPlotDownload()
function convertImgToBase64URL(svgSelector, callback){
    var img = new Image();
    var fname_for_plot = svgSelector.getAttribute("id");
    fname_for_plot = fname_for_plot.replace("target-", "");
    var xml = setupBulkPlotDownload(svgSelector);
    img.onload = function(){
      var canvas = document.createElement('canvas'),
      ctx = canvas.getContext('2d'), dataURL;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      canvas.height = this.height;
      canvas.width = this.width;
      ctx.drawImage(img, 0, 0);
      dataURL = canvas.toDataURL('image/png');
      callback(dataURL, fname_for_plot);
    };
    img.src = 'data:image/svg+xml;base64,' + window.btoa(xml);
}

//gets used
function createArchive(images){
    // Use jszip
    var zip = new JSZip();
    var pix = zip.folder('plots');
    for (var i=0; i < images.length; i++) {
      var  fname =  images[i].tag + '.png';
      pix.file(fname, images[i].data, {base64: true});  
    }
    zip.generateAsync({type:"blob"})
       .then(function(blob){
       saveAs(blob, "images.zip");
       show_or_hide_spinner(false);
    });
}
//end code for bulk downloads
