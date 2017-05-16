function setupAjaxyFormSubmissions(){
    //Matches all of the search forms.
    $("form").on('submit', function(event){
        event.preventDefault();
        hideControlsDuringSearch();
        create_search_post();
    });
}

function hideControlsDuringSearch(){
     $("div#form_errors").empty();
     $("#search_results").remove();   
     $("#drop-in").empty();
     clearOutPlots();
}

function showHideOneButton(btn_selector, show_that_button){
    if ( show_that_button) { $(btn_selector).show();  
    }else{ $(btn_selector).hide(); }
} 

function showHidePrevNext(search_paging_info){
    var btn_selector = '#ajaxyPagingButtons'; 
    var show_btn = {'prev': false, 'next': false};
    if (search_paging_info != null){ 
       show_btn['prev'] =  search_paging_info.show_prev_btn;
       show_btn['next'] = search_paging_info.show_next_btn; 
    }
    showHideOneButton(btn_selector + ' #next_button', show_btn['next']); 
    showHideOneButton(btn_selector + ' #prev_button', show_btn['prev']);
}


function clearOutPlots(){
   var plotsForPage = ['svg[id^="target"]', 
                      '[id!="target-0"]',
                      '[id!="target-snphalf-0"]',
                      '[id!="target-refhalf-0"]', 
                      '[id!="target-stacked-plot-0"]'];
   var plotSelector = plotsForPage.join(''); //don't remove the skeletons!
   $(plotSelector).remove();
}

function getActiveSearchType(){
    return $("span#type_of_shown_results")[0].innerText.trim();
}

//Handle events for paging buttons.
function pagingAJAX(nextOrPrev){
   hideControlsDuringSearch();
   create_paging_post(nextOrPrev, getActiveSearchType());
}

//add event listener for Download button
function clickDownloadResultsAJAX(){
   create_download_post(getActiveSearchType()); //action name, search type
}
