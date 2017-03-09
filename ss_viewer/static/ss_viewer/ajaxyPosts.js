//TODO: determine if search type is a needed parameter for these.
function create_search_post(action_name, search_type){
 var formElement = document.querySelector('div.active form');
 form_data = new FormData(formElement); 
 
 form_data.append('search_type', search_type);
 form_data.append('action',  action_name);
 // var url_endpoint = 'ajaxy-' + search_type + '/';
 var url_endpoint = search_type + '/';

 $("div#status_message").text("Working... ");
 $("div#download_button").attr("style", "display:none;");
 $("#download_page_of_plots").hide();   //remove this
 $("#download_plots_for_checked_rows").hide();  //remove this
 $("#download-exp").hide(); 
 //TODO: no need to explicitly show and hide the child dowload buttons.

 showHidePrevNext(null); 
 //hides the search buttons while we are working...

  $.ajax({
      beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", csrftoken);
           }
           var target = $("body");
           var spinner = new Spinner().spin();
           target.append(spinner.el);
           console.log("appended spinner!");
      },
      url: url_endpoint, 
      type: "POST", 
      data: form_data,   
      processData: false,
      cache: false,
      contentType: false,
     
      success: function(json) {
          console.log("AJAX call reported success. Next line w/ response");
          console.log(json);
          $("div#status_message").text(json.status_message);

          if ( json.api_response != null){
              show_search_results(json);
          }

          //save data about the search onto the page: 
          //search type
          $("#type_of_shown_results").text(search_type);

          //what about just grabbing the form data that is sent back?
          console.log(json.form_data); //try to grab the values out of here.

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
          $("div#status_message").text(errorJSON.status_message);
          showHidePrevNext(null); //hides the next and previous buttons.
      },
      complete: function(){
          console.log("complete is acctually happenning; do shared stuff if this triggers for success AND error.");
          $("div.spinner").remove();
      }
  });              
}

//search type should already be present.
//some of this can be factored out...
function create_paging_post(action_name, search_type){
 var val_text = $("div#current_search_params").text();
 var values = jQuery.parseJSON(val_text);
 values['action'] = action_name
 var url_endpoint = 'ajaxy-' + search_type + '/';
 $("div#status_message").text("Working... ");
 $("div#download_button").attr("style", "display:none;");
 $("#download-exp").hide(); //TODO: no need to individually hide child 
                            //elements of the download-exp(lanation) box.
 showHidePrevNext(null); 
 //hides the search buttons while we are working...

  console.log("about to send ajax to endpoint " +
              url_endpoint +  " with these values:");
  console.log(values);
  $.ajax({
      beforeSend: function(xhr, settings) {
           if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
               xhr.setRequestHeader("X-CSRFToken", csrftoken);
           }
           var target = $("body");
           var spinner = new Spinner().spin();
           target.append(spinner.el);
           console.log("appended spinner!");
      },
      url: url_endpoint, //url: "ajaxy-snpid-window-search/",
      type: "POST", 
      data: values , 
     
      success: function(json) {
          console.log("PAGING: AJAX call reported success. Next line w/ response");
          console.log(json);

          //this should contain a correct version of page_of_results_shown.
          $("div#status_message").text(json.status_message);

          if ( json.api_response != null){
              show_search_results(json);
          }
          if (json.search_paging_info != null){ 
              values.page_of_results_shown =
                      json.search_paging_info.page_of_results_to_display;
              console.log("...setting page number of results shown to:" + values.page_of_results_shown);
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
          $("div#status_message").text(errorJSON.status_message);
          showHidePrevNext(null); //hides the next and previous buttons.
      },
      complete: function(){
          console.log("complete is acctually happenning; do shared stuff if this triggers for success AND error.");
          $("div.spinner").remove();
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
  var result_text = $("div#status_message").text();
  $("div#status_message").text("Working... ");

  var url_endpoint = 'ajaxy-' + search_type + '/';

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
          $("div#status_message").text(result_text);
      }
  };
  xhttp.open("POST", url_endpoint);
  xhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhttp.setRequestHeader("X-CSRFToken", csrftoken);
 
  console.log("values for submitting for download; "+ values);

  // You should set responseType as blob for binary responses
  xhttp.responseType = 'blob';
  xhttp.withCredentials = true;
  xhttp.send(JSON.stringify(values));
}
