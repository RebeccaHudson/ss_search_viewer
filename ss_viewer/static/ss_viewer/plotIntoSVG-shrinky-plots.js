//unshiftedMotifLength either Ref or SNP
//pwmOffset -> either ref or SNP
//xScale is the same xScale that's being used elsewhere.
function drawMarkerLineCompress(targetForLine, pwmOffset, unshiftedMotifLength, xScale, y, strand){
          var direction; //left to right (5' to 3')    right to left (3' to 5')
          s = pwmOffset + unshiftedMotifLength;
          var xLeft = xScale.rangeBand() * (pwmOffset + 1/2 + (pwmOffset * .1));
          var xRight = xScale.rangeBand() * (s - 1/3 + (s * .1)); 
          var leftLabelText; var rightLabelText;
          if (strand == '+' ) { xBegin = xLeft;  xEnd =  xRight; 
                                leftLabelText = "5'";    
                                rightLabelText = "3'"; }
                      else    { xBegin = xRight; xEnd =  xLeft;  
                                leftLabelText = "3'";  
                                rightLabelText = "5'";    }   
          targetForLine.append("line")
                     .attr("x1", xBegin) 
                     .attr("y1", y)  //y1 == y2,    x1 and x2 are determined by the motif data.
                     .attr("x2", xEnd) 
                     .attr("y2", y)
                     .attr("stroke-width", 2)
                     .attr("stroke", "#08519c")
                     .attr("marker-end", "url(#Triangle)");

         targetForLine.append('text') 
                       .attr("font-size", 12)  
                       .attr('stroke', "#08519c")
                       .text(leftLabelText)
                       .attr('x', xLeft - 15) 
                       .attr('y', y - 5);

         targetForLine.append('text') 
                       .attr("font-size", 12)  
                       .attr('stroke', "#08519c")
                       .text(rightLabelText)
                       .attr('x', xRight + 12) 
                       .attr('y', y - 5) ;
}

function drawFixedWidthCompositePlot(plotToMake, idOfTargetSVG){
        //idOfTargetSVG = idOfTargetSVG.replace(/\:/g, '\\:');
        //start with the reference end of the plot
        //
        
        var refSeq = plotToMake.ref_aug_match_seq.split("");
        var refStrand = plotToMake.ref_strand;//Plus or -
        var refPWMOffset = plotToMake.ref_extra_pwm_off;

        var snpSeq = plotToMake.snp_aug_match_seq.split("");
        var snpStrand = plotToMake.snp_strand;
        var snpPWMOffset = plotToMake.snp_extra_pwm_off;

        var randomMotif = plotToMake.motif_data;
        var maxColumnCount = d3.max([refSeq.length, 
                                     randomMotif.forward.length + refPWMOffset  ]);
        //columnWidth is 35 by default.
        //side margin
        var  sideMargin = 10;
        var  fixedWidth = 300;

        var columnWidthScaled = (fixedWidth - margin.left - margin.right) / maxColumnCount;

        if (columnWidthScaled > 29) { columnWidthScaled = 29; } //is this reasonable?

        //var unscaledLetterHeight = columnWidthScaled * 1.3;
        // SHRINK shrinking the height of the plots...
        var unscaledLetterHeight = columnWidthScaled * 0.9;
        // Expand the SVG to fit the widest row.
        //var svgWidth = maxColumnCount * columnWidthScaled + 
        //               margin.left + margin.right + 50;
        var svgWidth = fixedWidth; 
        var svgHeight = svgWidth / 2.5;
        
        svgHeight = svgHeight * 1.6; //accomodate 2 plots stacked up instead.
        //SHRINK

        //don't extend arbitrarially.
        //if (svgWidth < 460) { svgWidth = 460; }
        //force width to ensure the main plot label fits
        d3.select("svg#"+idOfTargetSVG).attr("width", svgWidth);
        d3.select("svg#"+idOfTargetSVG).attr("height", svgHeight);
        //make a range of integers that will be the values for the ordinal X scale.
        var ordinalXRange = [];  //list of integers 0 thru max columns required. 
        for (i = 0; i < maxColumnCount; i++){ ordinalXRange[i] = i; }


        //TODO: add parentheses to the strand information.
        //draw the 'strand' data next to where the SNP and reference sequences will appear
        //ref strand on line 2, SNP strand on line 3 (this is the + and -s)
        d3.select("svg#" + idOfTargetSVG + " g#line2margin text").text("(" + refStrand + ")");
        d3.select("svg#" + idOfTargetSVG + " g#line3margin text").text("(" + snpStrand + ")");


        //draw the line 1 motif.
        //Reference strand determines the direction the line 1 motif is displayed.
        var targetGroup = d3.select("svg#" + idOfTargetSVG + " g#line1data");
        //var targetForLine;
        //var dataForMotif;
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
        drawMarkerLineCompress(targetForLine, refPWMOffset, unshiftedMotifLength, 
                                                   xScale, 55, refStrand); 
        //draw the reference sequence on line 2.
        var refSeqTargetSelector = d3.select("svg#" + idOfTargetSVG + " g#line2data");
        drawUnscaledSequenceScaled(refSeqTargetSelector, refSeq, xScale, unscaledLetterHeight);

        drawScaledHorizontalAxis(refSeqTargetSelector, xScale, refSeq, maxColumnCount, columnWidthScaled);


        var highlightPosition = findSNPLocation(plotToMake);
        applyScaledHighlight(highlightPosition, idOfTargetSVG, xScale, columnWidthScaled);
        //end of the reference end.


        //start the code for the SNP half of the plot.

        //draw the line 4 motif.
        //SNP strand determines the direction the line 4 motif is displayed

         targetGroup = d3.select("svg#"+ idOfTargetSVG + " g#line4data");

         if ( snpStrand == '+' ) { dataForMotif = [].concat(randomMotif.forward); }
         else{ dataForMotif = [].concat(randomMotif.reverse);}
         
         unshiftedMotifLength = dataForMotif.length;
         //determine how long the line should be

         dataForMotif = applyOffsetToMotifData(dataForMotif, snpPWMOffset);
         setupScalesDomainsForOneMotif(xScale, y, ordinalXRange, snpSeq);
         //can the above call be omitted?
         drawOneMotif(dataForMotif, targetGroup, xScale, y, ordinalXRange);
 
         targetForLine = d3.select("svg#" + idOfTargetSVG + " g#line4data");
         drawMarkerLineCompress(targetForLine, snpPWMOffset, unshiftedMotifLength, 
                                                   xScale, 55, snpStrand); 

        //draw the unscaled SNP sequence and the ref sequence.
        columnCount = snpSeq.length; //TODO: is this needed? are we not using maxColumnCount?
        setupScalesDomainsForOneMotif(xScale, y, ordinalXRange, snpSeq);

        //draw the SNP sequence on line 3
        var snpSeqTargetSelector = d3.select("svg#" + idOfTargetSVG + " g#line3data");
        drawUnscaledSequenceScaled(snpSeqTargetSelector, snpSeq, xScale, unscaledLetterHeight);
        drawScaledHorizontalAxis(snpSeqTargetSelector, xScale, snpSeq, maxColumnCount, columnWidthScaled);

        var highlightPosition = findSNPLocation(plotToMake);
        applyScaledHighlight(highlightPosition, idOfTargetSVG, xScale, columnWidthScaled);
        if (columnWidthScaled < 20){
            targetForLine.attr('transform', function(){ return 'translate(0, 40)'; } );
        }
        //end code for SNP half of plot.
       
        //adjust the label positions..
        var labelXShift = 40;
        var labelYShift = 1.129 * columnWidthScaled - 10.76;
        if (columnWidthScaled == 29){
            labelYShift -=  6;
        }
        d3.select("svg#" + idOfTargetSVG + " g.snp-label")
          .attr('transform', 'translate('+labelXShift+', ' + labelYShift  + ' )');

        //Need to adjust the translation of the bottom half of the plot. 
        var line4 = d3.select("svg#" + idOfTargetSVG + " g#line4data"); 
        var downshift;
        if (columnWidthScaled < 20){ 
          downshift = 125;
        }else{ 
          downshift = 130; }
        line4.attr('transform', function(){ return 'translate(0, ' + downshift  + ')'; } );  
}//end of function to draw fixed-width full composite logo plot

//This appears to work.
function applyScaledHighlight(highlightPosition, idOfTargetSVG, xScale, columnWidthScaled){
    if (highlightPosition >= 0) {
      var highlight = d3.select("svg#" + idOfTargetSVG + " #highlight");
      // var highlightHeight = columnWidthScaled * 5.5;
      // var yShift = (columnWidthScaled - 3)* .8;
      
      //for 1/2 a plot: var highlightHeight = 1.45 * columnWidthScaled + 75; 
      var highlightHeight = 10 * columnWidthScaled; 
      var yNudge = 10;
      if (columnWidthScaled < 20){
           highlightHeight += 100;
           yNudge = 5;
      }

      var yShift = 10 - (columnWidthScaled * 0.2);
      var nudge = 0;
      if (columnWidthScaled < 20){
         nudge = 2;   
      } 
      highlight.attr("x", function(){ 
                               var happyX = xScale(highlightPosition) - 2; 
                               return  happyX + nudge; })
               .attr("y", yShift + yNudge)       
               .attr("height", highlightHeight ) 
               .attr("width", function(){ return columnWidthScaled; } )
               .style("fill", "#d3d3d3");
    }
}

//lots of hardcoded numbers; get away from these if it's possible.
//SHRINK TODO: Rename this function to something more reasonable.
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
    var axisScaleAdjustment = sequence.length / 2;
    var axisTranslateForward = Math.floor(maxColumnCount*.1);

    var axisScale = d3.scale.ordinal()
                      .rangeRoundBands([0, sequence.length*columnWidth], .1);

    axisScale.domain( sequence.map( function(d, i) { return i + 1; } ));  
    var altXAxis = d3.svg.axis().scale(axisScale).orient("bottom");
    var height =  columnWidth * 1.35;
    //SHRINK
    var offset = height + height * 0.2; //This should not change per motif.
    //y = -1.851851852·10-2 x2 + 1.611111111 x + 7  haha http://www.xuru.org/rt/PR.asp#Manually
    var offset = (-1.851851/100)*Math.pow(columnWidth,2) + 1.6211111*columnWidth + 5;

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
                            //can this be shortcircuited somehow?
                            return 0;
                        }
                        return yVal;
                       })
      .style( "font-size", function(e) { return ( y(e.y0) - y(e.y1) ) * capHeightAdjust; } );
}
