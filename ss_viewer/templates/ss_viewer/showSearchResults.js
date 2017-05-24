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

    row += makeAColumn(api_response.snpid,'snpid', link=api_response.dbsnp_link);

    var coordToShow = [api_response.chr, api_response.pos.toLocaleString()].join(':');
    row += makeAColumn(coordToShow, 'coordinate', link=api_response.ucsc_link); 

    row += makeAColumn(api_response.pval_rank.toExponential(3), 'pval_rank');
    row += makeAColumn(api_response.pval_ref.toExponential(3), 'pval_ref');
    row += makeAColumn( api_response.pval_snp.toExponential(3), 'pval_snp');
    row += makeAColumn( api_response.trans_factor, 'trans_factor', link=api_response.factorbook_link);

    var idToUse = 'plot_data_'  + api_response.plot_id_str;
    row += makeAColumn(api_response.json_for_plotting, 'plotting_data', link=null, id=idToUse, hide=true);

    var detailLink =  '{% url 'ss_viewer:detail' id_str='x_x_x' %}'.replace('x_x_x', '') + api_response.plot_id_str;
    row += makeAColumn('Details', 'details', link=detailLink); 
 
    idToUse = 'stacked-plot-' + api_response.plot_id_str;
    row += makeAColumn('', 'stacked-plot cl_plot', link=null, id=idToUse);
    
    var checkbox = ['<input', setupAttribute('type', 'checkbox'), 
                   setupAttribute('id', api_response.plot_id_str), '>'].join(' ');
    row += makeAColumn(checkbox, 'add_to_download');

    row += "</tr>";
    return row;
}


//put search results into the document.
function show_search_results(json) {
    if ( json.api_response == null ) { return; }
    showHidePrevNext(json.search_paging_info);
    //if it's null, no buttons will be shown.
    var content = unpopulatedSearchResultsTable();
    $("#drop-in").append(content);
    $('#download-exp').show();
    var rows = "";
    for (var i = 0; i < json.api_response.length; i ++){
        var oneRow = seutpOneRowOfSearchResults(json.api_response[i]);
        rows += oneRow;
    }
    $("#drop-in table tbody").append(rows);
    //
    showStatusInCorrectPlace(false); //hide the top one.
    setupPlotsForSearchResults(); 
    setMaxValueOnJumpControl(json.search_paging_info);
}//end of show_search_results function.
