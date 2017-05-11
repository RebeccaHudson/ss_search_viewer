function setupSNPidFileControls(){
    //handle SNPid list input controls for entering a file of SNPids or 
    //a typed/pasted list of SNPids: 
    //setup infrastructure for the button to clear the file.
    $("#id_snpid-file_of_snpids").change(function(e){
          var fileval = $("#id_snpid-file_of_snpids").attr('value');
          console.log("file val : = " + fileval);
          $("#clear-snpid-file").attr('style', 'display:inline;');
           /* blank out the snpdis requested if the file upload button is clicked. */
           $("#id_snpid-raw_requested_snpids").val("");
          console.log("did that show the button?");
     });
      
    /*if the change event is used, this will not happen 
      until the control loses focus*/ 
    $("#id_snpid-raw_requested_snpids").click(function(e){
         clearFileInput();
    });
    $("#clear-snpid-file").click(function(e){
          e.preventDefault();
          clearFileInput();
    });
    function clearFileInput(){
          $("#id_snpid-file_of_snpids")[0].value = ''; 
          $("#clear-snpid-file").attr('style', 'display:none;');
    } 
  
    //Show the "clear" button if there's already a file selected.
    if (! ( $("#id_snpid-file_of_snpids")[0].value == '')) {
        $("#clear-snpid-file").attr('style', 'display:inline;');
    } 
}


