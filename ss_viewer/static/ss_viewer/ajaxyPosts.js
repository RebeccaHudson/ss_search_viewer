function pull_search_type(form_data){
  var onekey = form_data.keys()[0];
  for (var key of form_data.keys()) {
      if ( key.search('-') > 0 ){
           //if the string is not found, search returns -1
          var prefix = key.split('-')[0]; 
          return prefix.replace('_', '-') + '-search';
      } 
   } 
}

function setup_shared_search_controls_dict(){
 var shared_search_controls_form_data  = 
            new FormData(document.querySelector('#shared_controls'));

  shared_search_controls_dict = {};
  motif_ic = [];
  /*  add each of the shared_form_controls to the formdata.*/
  for (var pair of shared_search_controls_form_data.entries()) {
     if (pair[0] == 'ic_filter' ){ motif_ic.push(pair[1]);  }else{
        shared_search_controls_dict[pair[0]] = pair[1];
     } 
     //console.log("shared data key: " +  pair[0] +  " shared data value: " +  pair[1]);
  }

  shared_search_controls_dict['ic_filter']  = motif_ic;

  //Sort order is stored as a string representation of a dictionary.
  shared_search_controls_dict['sort_order'] = 
             JSON.parse(shared_search_controls_dict['sort_order']);

  return shared_search_controls_dict;
}



function create_search_post(){
 var formElement = document.querySelector('div.active form');
 form_data = new FormData(formElement); 

 var search_type = pull_search_type(form_data);
 form_data.append('search_type', search_type);
 form_data.append('action',  'search');

 form_data.append('shared_controls', 
                  JSON.stringify(setup_shared_search_controls_dict()));

 hideControlsWhileLoading();

  $.ajax({
      beforeSend: function(xhr, settings) {
        csrfSafeSend(xhr, settings)
        show_or_hide_spinner(true);
        /*show the LOADING  div */
      },
      url: search_type + '/', 
      type: "POST", 
      data: form_data,   
      processData: false,
      cache: false,
      contentType: false,
      success: function(json) {
          handleResults(json.form_data, json);
          $("#type_of_shown_results").text(search_type);
      },
      error: function(xhr, errmsg, err) {
          showFormErrors(xhr);
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
}

function create_paging_post(action_name, search_type){
 var val_text = $("div#current_search_params").text();
 var values = jQuery.parseJSON(val_text);
 values['action'] = action_name
 hideControlsWhileLoading();
 
 if ( ! ( typeof(values['sort_order']) == "string") ) {
   values['sort_order'] =  JSON.stringify(values['sort_order']);
 }

 if ( ! ( typeof(values['ic_filter']) == "string") ) {
   values['ic_filter'] =  JSON.stringify(values['ic_filter']);
 }


 $.ajax({
      beforeSend: function(xhr, settings) {
           csrfSafeSend(xhr, settings);
           show_or_hide_spinner(true);
      },
      url: search_type + '/', 
      type: "POST", 
      data: values , 
      success: function(json) {
          handleResults(values, json);
      },
      error: function(xhr, errmsg, err) {
          showFormErrors(xhr);
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
} //also handles 'jump' action to jump to any valid page.


//shared between success handler for search and paging posts.
function handleResults(values, json){
    $("div.status_message").text(json.status_message);
    $("span.status_message").text(json.status_message);
    show_search_results(json);
    if (json.search_paging_info != null){ 
        values.page_of_results_shown =
            json.search_paging_info.page_of_results_to_display;
         //Sets the page number of displayed results.
    }else{ 
        //not setting the page of search results; but no error means 
        //that this is a non-error, but empty search results case.
        showStatusInCorrectPlace(true);
    }
  
    //stringify the ic filter information ONCE. 
    /*if (typeof values['ic_filter'] == 'object'){ 
        console.log("strinifying ic filter values.");
        values['ic_filter'] = JSON.stringify(values['ic_filter']);
        //must be un-stringified on the back end.
    }*/

    var values_to_save_for_paging = JSON.stringify(values);
    console.log("saving these values for paging:  ");
    console.log(values);
    $("div#current_search_params").text(values_to_save_for_paging);
}


function showFormErrors(xhr){
    //console.log(xhr.status + ": " + xhr.responseText);
    var errorJSON = jQuery.parseJSON(xhr.responseText);
    var errlist = '<ul>';
    for ( var j = 0; j < errorJSON.form_errors.length; j++){
        errlist += '<li>' + errorJSON.form_errors[j] + '</li>';
    } 
    errlist += '</ul>';
    $("div#form_errors").append(errlist);
    $("div.status_message").text(errorJSON.status_message);
    showHidePrevNext(null); //hides the next and previous buttons.
    showStatusInCorrectPlace(true);
}


//may be factored back into other create_post function; separate for now.
//SOURCE:
//http://stackoverflow.com/questions/28165424/download-file-via-jquery-ajax-post
function create_download_post(search_type) {
  var val_text = $("div#current_search_params").text();
  values = jQuery.parseJSON(val_text);
  values['action'] = 'Download Results';

 //this code is copied out of paging handler
 //TODO: factor it out into a sepearate function so it's not repeated.
 if ( ! ( typeof(values['sort_order']) == "string") ) {
   values['sort_order'] =  JSON.stringify(values['sort_order']);
 }

 if ( ! ( typeof(values['ic_filter']) == "string") ) {
   values['ic_filter'] =  JSON.stringify(values['ic_filter']);
 }

  var result_text = $("#status_above").text(); //Saved to be replaced after download.

  //Don't hide the download explanation box while preparing the download.
  $("div.status_message").text("Working... ");
  showStatusInCorrectPlace(true);//show the upper one, hide the lower
  show_or_hide_spinner(true);

  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
      var a;
      if (xhttp.readyState === 4 && xhttp.status === 200) {
          a = document.createElement('a');
          a.href = window.URL.createObjectURL(xhttp.response);
          a.download = "search-results-download.csv";
          a.style.display = 'none';
          document.body.appendChild(a);
          a.click();
          $("div.status_message").text(result_text);
      }
      if (xhttp.readyState == XMLHttpRequest.DONE) {
            show_or_hide_spinner(false);
      }
  };
  xhttp.open("POST",search_type + '/');
  xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhttp.setRequestHeader("X-CSRFToken", csrftoken);

  // You should set responseType as blob for binary responses
  xhttp.responseType = 'blob';
  xhttp.withCredentials = true;
  xhttp.send(JSON.stringify(values));
}

//try to use everywhere the spinner appears. 
//true for show, false for hide.
function show_or_hide_spinner(showOrHide){
  if (showOrHide === true){
    var target = $("body");
    var spinner = new Spinner().spin();
    target.append(spinner.el);
    console.log(spinner.el);
    $("#loading").show(); 
  }
  else{ 
        $("div.spinner").remove();
        $("#loading").hide(); 
  }
}

//true for upper, false for lower.
function showStatusInCorrectPlace(isUpper){
    if (isUpper === true){
        $("#status_above").show();
        $("#status_below").hide();
    }else{
        $("#status_above").hide();
        $("#status_below").show();
    }    
}

/*Don't let users jump past the end of the search results.
  use total_page_count or max_page_availabe, whichever one is greater. 
  Don't allow paging past max_result_window / page_size (666 for now) */
function setMaxValueOnJumpControl(search_paging_info){
   var maxPg;
   if (search_paging_info.max_page_available <  
         search_paging_info.total_page_count){
        maxPg = search_paging_info.max_page_available;
      }else{
        maxPg = search_paging_info.total_page_count;
      }
      $("#user-page-number").attr('max',maxPg );
      $("#max_pg_available").text(maxPg);
}

function  hideControlsWhileLoading(){
   $("div.status_message").text("Working... ");
   showStatusInCorrectPlace(true);
   showHidePrevNext(null); 
}

//shared in beforeSend for paging and search requests.
function csrfSafeSend(xhr, settings){
  if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
  }

}
