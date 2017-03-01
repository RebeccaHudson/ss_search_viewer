
//start code for bulk downloads
//Clones the node containing the plot to be added to the ZIP. 
//adds definitions for the Arrowhead markers.
//sets up an HTML <canvas> element, including appropriate width,
//serizlizes the SVG copy into a string of XML.
function setupBulkPlotDownload(svg){
   console.log("bulk download for svg selector: " + svg );
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

//working answer for this tough problem adapted from:
//http://stackoverflow.com/questions/31384408/
//     how-to-get-multiple-files-via-ajax-and-download-them-as-a-zip-file-via-javascrip 
function bulkPlotDownload(){
       var images = [];
       var counter = 0;
       var targets = $('svg[id^="target"]');
       //starting at 1 excludes target-0, the SVG skeleton.
       for (var i = 1; i< targets.length; i++) {
          convertImgToBase64URL(targets[i], function (base64Img, fname_for_plot) {
            var dataForOnePlot = base64Img.replace("data:image/png;base64,", '');
            images.push({
              data: dataForOnePlot,
               tag: fname_for_plot
            });
            counter++;
            if (counter == (targets.length-1)) {
              createArchive(images);
            }
          });
        }
}      

//make another version of bulk_plot_download
function checkedRowPlotDownload(){
       var images = [];
       var counter = 0;
       var targets = $('svg[id^="target"].target');
       //add some logic that results in only checked rows being added. 
       //get the parent element of each target.
       // check that parent element for a checkbox; 
       // if that checkbox is checked; add it to the real list of 'targets'
       // elsewise, just continue on.
       // $("input[type=checkbox]")/
       //starting at 1 excludes target-0, the SVG skeleton.
       checkedTargets = []; 
       for (var i = 1; i < targets.length; i++){ //skip over the skeleton, target-0
          //the following depends on the structure of the data table.           
          var idToUse = targets[i].id.replace('target-', '');
          var checky = $("input#" + idToUse); 
          console.log("id being checked ... " + idToUse);
          checky = checky[0]; 
          console.log("checky : " + checky + " checky.checked: " + checky.checked);
          if ( checky.checked == true ){
             console.log("checkedTargets added one" + idToUse);
             checkedTargets.push(targets[i]); 
          }
       }
       console.log("checkedTargets.length " + checkedTargets.length);
       for (var i = 0; i < checkedTargets.length; i++) {
          console.log("adding one plot to the bulk download " + checkedTargets[i]);
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




//gets used, based on the same example cited for bulkPlotDownload()
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
      ctx.drawImage(img, 0, -30);
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
    });
}
//end code for bulk downloads

