//write another version of show_search_results that will take a rendered string and drop it in.
function show_search_results(page_of_results){
    var content = page_of_results;
    $("#drop-in").append(content);
    var search_paging_info = jQuery.parseJSON($("#search_paging_info").text());
    showHidePrevNext(search_paging_info);

    showStatusInCorrectPlace(false); //hide the top one.
    if (search_paging_info != null){
       setMaxValueOnJumpControl(search_paging_info);
       $("#download_button").show(); 
       setupPlotsForSearchResults(); 
       $(".download_detail_plot").click(function(e) {
           downloadSinglePlot(e);
       });

    }
}
