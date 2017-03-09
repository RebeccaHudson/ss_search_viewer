//add event listeners for each search form submit button.
function setupAjaxyFormSubmissions(){
   $("#snpid_window_form").on('submit', function(event){
       event.preventDefault();
       hideControlsDuringSearch();
       create_search_post('search', 'snpid-window-search');
   });
   $("#snpid_search_form").on('submit', function(event){
       event.preventDefault();  //works fine here?
       hideControlsDuringSearch();
       create_search_post('search', 'snpid-search');
   });
   $("#gl_region_search_form").on('submit', function(event){
       event.preventDefault();  //works fine here?
       hideControlsDuringSearch();
       create_search_post('search', 'gl-region-search');
   });
   $("#gene_name_form").on('submit', function(event){
       event.preventDefault();
       hideControlsDuringSearch();
       create_search_post('search', 'gene-name-search');
   });
   $("#tf_search_form").on('submit', function(event){
       event.preventDefault();
       hideControlsDuringSearch();
       create_search_post('search', 'trans-factor-search');
   });
}

function hideControlsDuringSearch(){
     $("div#form_errors").empty();
     $("#search_results").remove();   
     $("#drop-in").empty();
     clearOutPlots();
     //$("div#plots").empty(); //does this work? no.
}

function showHidePrevNext(search_paging_info){
    if ( (search_paging_info != null) && (search_paging_info.show_next_btn) ){
      $("#ajaxyPagingButtons #next_button").attr("style", "display:inline;"); 
    }else{
      $("#ajaxyPagingButtons #next_button").attr("style", "display:none;"); 
    }
    if ( (search_paging_info != null) && (search_paging_info.show_prev_btn) ){
      $("#ajaxyPagingButtons #prev_button").attr("style", "display:inline;"); 
    }else{ 
      $("#ajaxyPagingButtons #prev_button").attr("style", "display:none;"); 
    }
}

//add event listener for paging buttons
function pagingAJAX(nextOrPrev){
   var active_search = $("span#type_of_shown_results")[0].innerText.trim();
   $("div#form_errors").empty();
   $("#search_results").remove();   
   $("#drop-in").empty();
   clearOutPlots();
   create_paging_post(nextOrPrev, active_search);
}

function clearOutPlots(){
   var plotsForPage = ['svg[id^="target"]', 
                      '[id!="target-0"]',
                      '[id!="target-snphalf-0"]',
                      '[id!="target-refhalf-0"]'];
   var plotSelector = plotsForPage.join(''); //don't remove the skeletons!
   $(plotSelector).remove();
}


//add event listener for Download button
function clickDownloadResultsAJAX(){
   var active_search = $("span#type_of_shown_results")[0].innerText.trim();
   create_download_post(active_search); //action name, search type
}
