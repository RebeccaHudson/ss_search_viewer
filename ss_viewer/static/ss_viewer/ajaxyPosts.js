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

function create_search_post(action_name){
 var formElement = document.querySelector('div.active form');
 form_data = new FormData(formElement); 
 var search_type = pull_search_type(form_data);
 form_data.append('search_type', search_type);
 form_data.append('action',  action_name);
 var url_endpoint = search_type + '/';

 hideControlsWhileLoading();

  $.ajax({
      beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", csrftoken);
           }
           show_or_hide_spinner(true);
      },
      url: url_endpoint, 
      type: "POST", 
      data: form_data,   
      processData: false,
      cache: false,
      contentType: false,
     
      success: function(json) {
          //console.log(json);
          $("div.status_message").text(json.status_message);

          if ( json.api_response != null){
              show_search_results(json);
          }

          //save data about the search onto the page: 
          $("#type_of_shown_results").text(search_type);

          console.log(json.form_data);
          //JSON dict containing search params that correspond to any 
          //search results shown.
          
          var values = {};

          values = json.form_data; //does it work to just store the dict directly and re-copy it?
          if (json.search_paging_info != null){ 
              values.page_of_results_shown =
                      json.search_paging_info.page_of_results_to_display;
              console.log("...setting page number of results shown to:" + values.page_of_results_shown);
          }
          //this should contain a correct version of page_of_results_shown.
          var values_to_save_for_paging = JSON.stringify(values);
          console.log("values to persist after successful search: " + values_to_save_for_paging);
          $("div#current_search_params").text(values_to_save_for_paging);

      },
      error: function(xhr, errmsg, err) {
          /* would put code down here to append error messages onto the search page.*/
          console.log(xhr.status + ": " + xhr.responseText);
          //MOVE THIS TO ITS OWN FUNCTION:
          var errorJSON = jQuery.parseJSON(xhr.responseText);
          var errlist = '<ul>';
          for ( var j = 0; j < errorJSON.form_errors.length; j++){
              errlist += '<li>' + errorJSON.form_errors[j] + '</li>';
          } 
          errlist += '</ul>';
          $("div#form_errors").append(errlist);
          $("div.status_message").text(errorJSON.status_message);
          showHidePrevNext(null); //hides the next and previous buttons.
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
}

function  hideControlsWhileLoading(){
   $("div.status_message").text("Working... ");
   showStatusInCorrectPlace(true);
   $("#download-exp").hide(); //hides child elements.
   showHidePrevNext(null); 
}

//search type should already be present.
//some of this can be factored out...
function create_paging_post(action_name, search_type){
 var val_text = $("div#current_search_params").text();
 var values = jQuery.parseJSON(val_text);
 values['action'] = action_name
 var url_endpoint = search_type + '/';

 hideControlsWhileLoading();

  console.log("about to send ajax to endpoint " +
              url_endpoint +  " with these values:");
  console.log(values);
  $.ajax({
      beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", csrftoken);
           }
           show_or_hide_spinner(true);
      },
      url: url_endpoint, 
      type: "POST", 
      data: values , 
     
      success: function(json) {
          $("div.status_message").text(json.status_message);

          if ( json.api_response != null){
              show_search_results(json);
          }
          if (json.search_paging_info != null){ 
              values.page_of_results_shown =
                      json.search_paging_info.page_of_results_to_display;
              console.log("...setting page number of results shown to:" + values.page_of_results_shown);
          }else{ 
              //not setting the page of search results; but no error means 
               //that there's a non-error, no search results case here.
              showStatusInCorrectPlace(true);
          }
          var values_to_save_for_paging = JSON.stringify(values);
          $("div#current_search_params").text(values_to_save_for_paging);
      },
      error: function(xhr, errmsg, err) {
          console.log(xhr.status + ": " + xhr.responseText);
          //MOVE THIS TO ITS OWN FUNCTION: can be shared 
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
      },
      complete: function(){
          show_or_hide_spinner(false);
      }
  });              
}


//may be factored back into other create_post function; separate for now.
//SOURCE:
//http://stackoverflow.com/questions/28165424/download-file-via-jquery-ajax-post
function create_download_post(search_type) {
  var val_text = $("div#current_search_params").text();
  values = jQuery.parseJSON(val_text);
  values['action'] = 'Download Results';
  var result_text = $("#status_above").text();

  //Don't hide the download explanation box while preparing the download.
  $("div.status_message").text("Working... ");
  showStatusInCorrectPlace(true);//show the upper one, hide the lower
  show_or_hide_spinner(true);

  var url_endpoint = search_type + '/';

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
  xhttp.open("POST", url_endpoint);
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


