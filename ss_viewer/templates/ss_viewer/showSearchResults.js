/* Functions that handle showing search results
   not included as regular Javascript due to the django template tags.*/
function unpopulatedSearchResultsTable(){
        return(`<table id="search_results" class="table table-condensed fixed-header"> \
  <thead class="fixed-header">                                                         \   
  <tr class="header" id="hide">                                   \ 
    <th class="snpid"><span>SNPid
         <sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:snpTable">?</a></sup>  
                                        </span>  </th>     \ 
    <th class="coordinate"><span>Chromosome:Position<sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:snpTable">?</a></sup>
                                        </span>  </th>     \ 
    <th class="pval_rank" ><span>p-value Rank<sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:pvalueTable">?</a></sup>
                                        </span>  </th>     \
    <th class="pval_ref"><span>p-value Reference<sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:pvalueTable">?</a></sup>
                                        </span>  </th>     \ 
    <th class="pval_snp"><span>p-value SNP<sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:pvalueTable">?</a></sup> 
                                        </span>  </th>     \
    <th class="trans_factor"><span>Transcription Factor<sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-3:motifTable">?</a></sup> 
                                        </span>  </th>      \ 
    <th class="details"><span>Details                   </span>  </th>\
    <th class="cl_plot"><span>Composite Logo Plot
        <sup><a target="_blank" href="{% url 'ss_viewer:help-page'%}#part-4:part-4"> ?</a></sup> 
                                         </span>  </th>    \ 
    <th class="add_to_download"><span>Add to Download            </span>  </th>    \
  </tr>                                                \ 
  </thead>                                             \ 
  <tbody class="scroll-content">
 </tbody>`);
 }

function setupAttribute(nameOfAttr, insideOfQuotes){
   return [nameOfAttr, '="', insideOfQuotes, '"'].join('');
}
function setupLink(url, linktext){
   return ['<a', setupAttribute('href', url), 
           setupAttribute('target', '_blank'),
           '>', linktext, '</a>'].join(' ');
}

function makeAColumn(content, styleclass, link=null, id=null,  hide=false){
  var col = ['<td',setupAttribute('class', styleclass)];
  if (!( id==null )){ 
    var idAsAttr = setupAttribute('id', id); 
    col.push(idAsAttr); 
  }
  if (hide==true){
    var hideAsAttr = setupAttribute('style', 'display:none;');
    col.push(hideAsAttr);
  } 
  col.push('>'); 
  if (!( link==null)){ 
    var lnAsAttr = setupLink(link, content);
    col.push(lnAsAttr);
    //content used as text for the link.
  } else{
    col.push(content);
  }
  col.push('</td>'); 
  return col.join(' ');
}


function seutpOneRowOfSearchResults(api_response){


    var row = "<tr>";
    /*row += "<td class='snpid' >" + 
        '<a href="' + api_response.dbsnp_link + '" target="_blank">' + 
          api_response.snpid + '</a>' + 
        "</td>";   
    */
    row += makeAColumn(api_response.snpid,'snpid', link=api_response.dbsnp_link);
    
    /*row += "<td class='coordinate'>" +
           '<a href="' + api_response.ucsc_link + '" target="_blank">' +
           api_response.chr + ":"  + 
           api_response.pos.toLocaleString() + '</a>' +
           "</td>"; */
    var coordToShow = [api_response.chr, api_response.pos.toLocaleString()].join(':');
    row += makeAColumn(coordToShow, 'coordinate', link=api_response.ucsc_link); 

    //row += "<td class='pval_rank'>" + api_response.pval_rank.toExponential(3) + "</td>";   
    row += makeAColumn(api_response.pval_rank.toExponential(3), 'pval_rank');

    //row += "<td class='pval_ref'>" +  api_response.pval_ref.toExponential(3) + "</td>";   
    row += makeAColumn(api_response.pval_ref.toExponential(3), 'pval_ref');

    //row += "<td class='pval_snp'>" +  api_response.pval_snp.toExponential(3) + "</td>";   
    row += makeAColumn( api_response.pval_snp.toExponential(3), 'pval_snp');

    /*
    row += "<td class='trans_factor'>";
    if ( ! ( api_response.factorbook_link === null ) ){
        row += '<a href="' + 
          api_response.factorbook_link +
          '" target="_blank">';
    }
    row += api_response.trans_factor;
    if (!(api_response.factorbook_link === null)){ row += '</a>'; }
    row += "</td>";   
    //should behave correctly if link is null or not..
    */
    //makeAColumn(content, styleclass, id=null, link=null, hide=false){
    row += makeAColumn( api_response.trans_factor, 'trans_factor', link=api_response.factorbook_link);

    /*row += '<td id="plot_data_'  + api_response.plot_id_str +  '" style="display:none;"';
    row += ' class="plotting_data">' + api_response.json_for_plotting + '</td>';*/
    var idToUse = 'plot_data_'  + api_response.plot_id_str;
    row += makeAColumn(api_response.json_for_plotting, 'plotting_data', link=null, id=idToUse, hide=true);

    var detailLink =  '{% url 'ss_viewer:detail' id_str='x_x_x' %}'.replace('x_x_x', '') + api_response.plot_id_str;
    row += makeAColumn('Details', 'details', link=detailLink); 
    //row += '<td class="details"> <a href='
    //              + '"{% url 'ss_viewer:detail' id_str='x_x_x' %}'.replace('x_x_x', '') 
    //              +  api_response.plot_id_str + '" target="_blank">Details</a></td>';
 
    idToUse = 'stacked-plot-' + api_response.plot_id_str;
    row += makeAColumn('', 'stacked-plot cl_plot', link=null, id=idToUse);
    //row += "<td class=\"stacked-plot cl_plot\" id=\"stacked-plot-" + api_response.plot_id_str +"\"></td>";
    
    var checkbox = ['<input', setupAttribute('type', 'checkbox'), 
                   setupAttribute('id', api_response.plot_id_str), '>'].join(' ');
    row += makeAColumn(checkbox, 'add_to_download');
    //row += '<td class="add_to_download"> <input type="checkbox" id="' + api_response.plot_id_str + '" ></td>';
    row += "</tr>";
    return row;
}


//put search results into the document.
function show_search_results(json) {
    showHidePrevNext(json.search_paging_info);
    //if it's null, no buttons will be shown.
    $("#download_button").attr("style", "display: inline;");
    $("#download_page_of_plots").attr("style", "display: inline;");
    $("#download_plots_for_checked_rows").attr("style", "display: inline;");
    var content = unpopulatedSearchResultsTable();
    $("#drop-in").append(content);
    $('#download-exp').show();
    var rows = "";
    for (var i = 0; i < json.api_response.length; i ++){
        var oneRow = seutpOneRowOfSearchResults(json.api_response[i]);
        rows += oneRow;
    }
    $("#drop-in table tbody").append(rows);
    setupPlotsForSearchResults(); 
}//end of show_search_results function.
