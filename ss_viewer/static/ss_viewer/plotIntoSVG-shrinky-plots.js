

////setup shared between all plots:
//    var margin = {top: 20, right: 20, bottom: 30, left: 40},
//        width = 500 - margin.left - margin.right,
//        height = 100  - margin.top - margin.bottom;
//
//    // There will probably be other vertical scales added later.
//    var y = d3.scale.linear()
//        .range([height, 0]);
//
//    var capHeightAdjust  = 0.99, // approximation to bring cap-height to full font size
//        logoYAdjust = 0.0053;
//
//    var columnWidth = 35;
//
//    //This actually puts the first svg object onto the page body.
//    var svg = d3.select("body")
//                .append("svg")
//                .attr("height", 0);//so sequencelogoFont() works..
//
//    //don't call this unless there's already an SVG on the page!
//    sequencelogoFont();
//




    //CURRENTLY UNDERGOING THIS:modify this so it produces a plot with a fixed width.
    //                          draw a half of a plot.
    //         For 'ref' plots.
    function makeAScaledDownHalfPlot(plotToMake, idOfTargetSVG){

        console.log("getting a half plot");
        var refSeq = plotToMake.ref_aug_match_seq.split("");
        var refStrand = plotToMake.ref_strand;//Plus or -
        var refPWMOffset = plotToMake.ref_extra_pwm_off;

        var randomMotif = plotToMake.motif_data;
        var maxColumnCount = d3.max([refSeq.length, 
                                     randomMotif.forward.length + refPWMOffset  ]);

        //columnWidth is 35 by default.
        //side margin
        var  sideMargin = 10;
        var  fixedWidth = 300;

        columnWidthScaled = (fixedWidth - margin.left - margin.right) / maxColumnCount;
        unscaledLetterHeight =  columnWidthScaled * 1.3 ; 

        // Expand the SVG to fit the widest row.
        //var svgWidth = maxColumnCount * columnWidthScaled + 
        //               margin.left + margin.right + 50;
        var svgWidth = fixedWidth; 
        var svgHeight = svgWidth / 2.5; 

        //don't extend arbitrarially.
        //if (svgWidth < 460) { svgWidth = 460; }
        //force width to ensure the main plot label fits
        d3.select("svg#"+idOfTargetSVG).attr("width", svgWidth);
        d3.select("svg#"+idOfTargetSVG).attr("height", svgHeight);
        //make a range of integers that will be the values for the ordinal X scale.
        var ordinalXRange = [];  //list of integers 0 thru max columns required. 
        for (i = 0; i < maxColumnCount; i++){ ordinalXRange[i] = i; }

        //draw the 'strand' data next to where the SNP and reference sequences will appear
        //ref strand on line 2, SNP strand on line 3 (this is the + and -s)
        d3.select("svg#" + idOfTargetSVG + " g#line2margin text").text(refStrand);

        //draw the line 1 motif.
        //Reference strand determines the direction the line 1 motif is displayed.
        var targetGroup = d3.select("svg#" + idOfTargetSVG + " g#line1data");
        var targetForLine;
        var dataForMotif;
        var unshiftedMotifLength;
        var xScale = d3.scale
                       .ordinal()
                       .rangeRoundBands([0, maxColumnCount*columnWidthScaled], .1);

        if ( refStrand == '+' ){ dataForMotif = [].concat(randomMotif.forward); }
        else { dataForMotif = [].concat(randomMotif.reverse); }
 
        unshiftedMotifLength = dataForMotif.length; 
        //determine how long the line should be
        
        dataForMotif = applyOffsetToMotifData(dataForMotif, refPWMOffset);
        setupScalesDomainsForOneMotif(xScale, y, ordinalXRange, dataForMotif);
        drawOneMotif(dataForMotif, targetGroup, xScale, y, ordinalXRange);
 
        targetForLine = d3.select("svg#" + idOfTargetSVG + " g#line1data");
        drawMarkerLine(targetForLine, refPWMOffset, unshiftedMotifLength, 
                                                   xScale, 55, refStrand); 
        //draw the reference sequence on line 2.
        var refSeqTargetSelector = d3.select("svg#" + idOfTargetSVG + " g#line2data");
        drawUnscaledSequenceScaled(refSeqTargetSelector, refSeq, xScale, unscaledLetterHeight);

        drawScaledHorizontalAxis(refSeqTargetSelector, xScale, refSeq, maxColumnCount, columnWidthScaled);

        var highlightPosition = findSNPLocationForHalfPlot(plotToMake);
        applyScaledHighlight(highlightPosition, idOfTargetSVG, xScale, columnWidthScaled);

}//end function to plot one SVG composite logo plot in an already-existing SVG.



//This appears to work.
function applyScaledHighlight(highlightPosition, idOfTargetSVG, xScale, columnWidthScaled){
    if (highlightPosition >= 0) {
      var highlight = d3.select("svg#" + idOfTargetSVG + " #highlight");
      // var highlightHeight = columnWidthScaled * 5.5;
      // var yShift = (columnWidthScaled - 3)* .8;
      var highlightHeight = 1.45 * columnWidthScaled + 75; 
      var yShift = 10 - (columnWidthScaled * 0.2);
      var nudge = 0;
      if (columnWidthScaled < 20){
         nudge = 2;   
      } 
      highlight.attr("x", function(){ 
                               var happyX = xScale(highlightPosition) - 2; 
                               return  happyX + nudge; })
               .attr("y", yShift)               //.attr("y", "10")
               .attr("height", highlightHeight ) //"105")
               .attr("width", function(){ return columnWidthScaled; } )
               .style("fill", "#d3d3d3");
    }
}



                         
//lots of hardcoded numbers; get away from these if it's possible.
function drawUnscaledSequenceScaled(sequenceTargetSelector, sequenceData, xScale, letterHeight){
    var seqColumn = sequenceTargetSelector.selectAll(".sequence-column")
           .data(sequenceData)   //one column per datum
           .enter()
           .append("g")
           .attr("transform", function(d, i) {
                           return "translate(" + (xScale(i) + (xScale.rangeBand() / 2 )) + ",0)"; })
           .attr("class", "sequence-column");

    seqColumn.selectAll("text")
              .data(function(d){ 
                         return d;  //snpSeq should be bound already.
                         //make this letter appear as text in this element..
                    })
              .enter()
              .append("text")
              .text(function(d) { return d; } )
              .attr("class", function(d) { //can also just explictly define the font-family attr.
                                 return "letter-"+ d;  })
              .style("text-anchor", "middle")
              .style("font-family", "console")
              .style("font-weight", "normal")
              .attr("textLength", xScale.rangeBand() ) 
              .attr("lengthAdjust", "spacingAndGlyphs")
              .attr("font-size", letterHeight)  //make this more dynamic
              .attr("y", function() { return letterHeight + 10;  } );
}
          


//trying to draw under 'sequence'; have to re-define a scale for use with 
//the axis that matches the ones on the plots.
function drawScaledHorizontalAxis(svgSelector, xScale, sequence, maxColumnCount, columnWidth){
    //make a new axis generator when a new x scale is needed is appropriate.
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient("bottom");   
    //this is experimental
    
    var axisScaleAdjustment = sequence.length / 2;
    var axisTranslateForward = Math.floor(maxColumnCount*.1);
    //console.log("axisTranslateForward " + axisTranslateForward);
    //try to eliminate the padding
    var axisScale = d3.scale.ordinal()
                      .rangeRoundBands([0, sequence.length*columnWidth], .1);
                      //.rangeRoundBands([0, sequence.length*columnWidth-axisScaleAdjustment], .1);

    axisScale.domain( sequence.map( function(d, i) { return i + 1; } ));  

    var altXAxis = d3.svg.axis().scale(axisScale).orient("bottom");

    //height is defined way up...
    console.log("columnWidth " +   columnWidth);
    
    var height =  columnWidth * 1.35;
    //try defining height like it's defined in the calling method. 
    var offset = height + 11 ; //This should not change per motif.

    var label_font_size = 12;
    if ( columnWidth < 20 ){  label_font_size = 10; }
    if ( columnWidth < 10 ){  label_font_size = 8; }
    svgSelector.append("g")
       .attr("class", "x axis")
       .attr("transform", "translate(" + axisTranslateForward + "," + offset + ")") 
       .style('font-size', label_font_size)
       .call(altXAxis);
}



//TODO:
//could be changed to add some scaling into this.
function drawLettersIntoColumns(columnsSelector, x, y){
  columnsSelector
    .selectAll("text")
    .data( function(d) { return d.bits; })
    .enter()
    .append("text")
      .text( function(e) { return e.letter; } )
      .attr("class", function(e) { return "letter-" + e.letter; } )
      .style( "text-anchor", "middle" )
      .style( "font-family", "Helvetica")  //was 'sequencelogo'
      .attr( "textLength", x.rangeBand() )
      .attr( "lengthAdjust", "spacingAndGlyphs" )
      .attr( "font-size", function(e) { return ( y(e.y0) - y(e.y1) ) * capHeightAdjust; } )
      .attr("y", function(e, i) { 
                        var yVal =  (y(e.y0) - (y(e.y0) - y(e.y1))*logoYAdjust); 
                        if (isNaN(yVal)) {
                            console.log("avoiding NaN..");
                            return 0;
                        }
                        return yVal;
                       })
      .style( "font-size", function(e) { return ( y(e.y0) - y(e.y1) ) * capHeightAdjust; } );
}

