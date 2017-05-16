function pull_search_type(form_data){
  for (var key of form_data.keys()) {
      //every search type has a pvalue_rank_cutoff;
      if ( key.search('pvalue_rank_cutoff') > 0 ){
      //if the string is not found, search returns -1
          var prefix = key.split('-')[0]; 
          return prefix.replace('_', '-') + '-search';
      } 
   } 
}

function create_search_post(){
 var formElement = document.querySelector('div.active form');
 form_data = new FormData(formElement); 

 var search_type = pull_search_type(form_data);
 form_data.append('search_type', search_type);
 form_data.append('action',  'search');

 hideControlsWhileLoading();

  $.ajax({
      beforeSend: function(xhr, settings) {
        csrfSafeSend(xhr, settings)
        show_or_hide_spinner(true);
      },
      url: search_type + '/', 
      type: "POST", 
      data: form_data,   
      processData: false,
      cache: false,
      contentType: false,
      success: function(json) {
          handleResults(json.form_data, json);
          //save data about the search onto the page: 
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

//some of this can be factored out...
function create_paging_post(action_name, search_type){
 var val_text = $("div#current_search_params").text();
 var values = jQuery.parseJSON(val_text);
 values['action'] = action_name
 hideControlsWhileLoading();
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
}

//shared between success handler for search and paging posts.
function handleResults(values, json){
    $("div.status_message").text(json.status_message);
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
    var values_to_save_for_paging = JSON.stringify(values);
    $("div#current_search_params").text(values_to_save_for_paging);
    //console.log(json.form_data);
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
  }
  else{ $("div.spinner").remove(); }
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

function  hideControlsWhileLoading(){
   $("div.status_message").text("Working... ");
   showStatusInCorrectPlace(true);
   $("#download-exp").hide(); //hides child elements.
   showHidePrevNext(null); 
}

//shared in beforeSend for paging and search requests.
function csrfSafeSend(xhr, settings){
  if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
  }

}
