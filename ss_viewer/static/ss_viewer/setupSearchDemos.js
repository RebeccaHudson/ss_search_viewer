function setupSearchDemos(){
    $("#snpid-search-demo").click(function(e){ 
       e.preventDefault();
       var snpids =  ['rs767515427', 'rs12122964', 
       'rs377519826', 'rs16859534', 'rs528712585', 'rs141738071',
       'rs115414042', 'rs560130593', 'rs779870075', 'rs143430025',
       'rs79708193', 'rs6427105', 'rs558661914', 'rs777477534', 
       'rs747251582'];
       $('#id_snpid-raw_requested_snpids').val(snpids.join(', '));
       fill_in_pvalues('snpid');
    });

    $("#gl-search-demo").click(function(e){
       e.preventDefault();
       $('#id_gl_region-gl_start_pos').val(10000); 
       $('#id_gl_region-gl_end_pos').val(143163);
       //As of 5/17/17, significantly larger genomic location queries 
       // crush the Elasticsearch cluster
       $('#id_gl_region-selected_chromosome').val('ch5');
       fill_in_pvalues('gl_region');
    });


    $("#tf-search-demo").click(function(e){
        e.preventDefault();
        $('#id_trans_factor-trans_factor').val('Zfx'); 
        $('#id_trans_factor-encode_trans_factor').attr('disabled', 'disabled');
        $("#id_trans_factor-trans_factor").removeAttr('disabled');
        $('#id_trans_factor-tf_library_0').prop('checked', true);
        $('#id_trans_factor-tf_library_1').removeAttr('checked'); 
        fill_in_pvalues('trans_factor');
   });

    $("#snpid-window-search-demo").click(function(e){
        e.preventDefault();
        $('#id_snpid_window-snpid').val('rs755632525');
        fill_in_pvalues('trans_factor');
    });

    $("#gene-name-search-demo").click(function(e){
        e.preventDefault();
        $('#id_gene_name-gene_name').val('ELOVL1'); 
        fill_in_pvalues('gene_name');
    });
}

function fill_in_pvalues(prefix){
    prefix = '#id_' + prefix + '-';
    var cutoff_for_all = 0.05;
    $(prefix + 'pvalue_rank_cutoff').val(cutoff_for_all);
    $(prefix + 'pvalue_snp_cutoff').val(cutoff_for_all);
    $(prefix + 'pvalue_ref_cutoff').val(cutoff_for_all);
}

/* No defaults are provided for sort order; you get results no matter what you do.*/
