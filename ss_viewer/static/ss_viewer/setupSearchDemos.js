function setupSearchDemos(){
    /* clickable examples for demo searches */
    $("#snpid-search-demo").click(function(e){ 
                                   $('#id_raw_requested_snpids').val(
                                         'rs539483321, rs576894892, rs553761389, rs757299236, rs770590115');
                                    } );
    $("#gl-search-demo").click(function(e){
                                   $('#id_gl_start_pos').val(10000);
                                   $('#id_gl_end_pos').val(143511163);
                                   $('#id_selected_chromosome').val('ch5'); });
    $("#tf-search-demo").click(function(e){
                                  $('#id_trans_factor').val('NFYB'); 
                                    $('#id_encode_trans_factor').attr('disabled', 'disabled');
                                    $("#id_trans_factor").removeAttr('disabled');
                                    $('#id_tf_library_0').prop('checked', true);
                                    $('#id_tf_library_1').removeAttr('checked'); 
                                    });

    $("#snpid-window-search-demo").click(function(e){
                                  $('#id_snpid').val('rs755632525'); });
    $("#gene-name-search-demo").click(function(e){
                                  $('#id_gene_name').val('ELOVL1'); });

}

