function setupSearchDemos(){
    $("#shared-controls-search-demo").click(function(e){
        e.preventDefault();
        var id_of_active_form = $("div.tab-pane.panel-body.active").attr('id');
        switch(id_of_active_form){
        case 'snpid_search_form':
            snpid_search_demo();
            break;
        case 'gl_region_search_form':
            gl_region_search_demo();
            break;
        case 'tf_search_form':
            trans_factor_search_demo();
            break;
        case 'snpid_window_form':  
            snpid_window_search_demo();
            break;
        case 'gene_name_form':
            gene_name_search_demo();
            break;
        }
        fill_in_pvalues();
        check_all_degeneracy_levels();
    });
}

function trans_factor_search_demo(){
   $('#id_trans_factor-trans_factor').val('ZNF263'); 
   $('#id_trans_factor-encode_trans_factor').attr('disabled', 'disabled');
   $("#id_trans_factor-trans_factor").removeAttr('disabled');
   $('#id_trans_factor-tf_library_0').prop('checked', true);
   $('#id_trans_factor-tf_library_1').removeAttr('checked'); 
}

function gene_name_search_demo(){
   $('#id_gene_name-gene_name').val('ELOVL1'); 
}

function gl_region_search_demo(){
   $('#id_gl_region-gl_start_pos').val(10000); 
   $('#id_gl_region-gl_end_pos').val(143163);
   $('#id_gl_region-selected_chromosome').val('ch5');
}

function snpid_search_demo(){
   var snpids =  ['rs767515427', 'rs12122964', 
   'rs377519826', 'rs16859534', 'rs528712585', 'rs141738071',
   'rs115414042', 'rs560130593', 'rs779870075', 'rs143430025',
   'rs79708193', 'rs6427105', 'rs558661914', 'rs777477534', 
   'rs747251582'];
   $('#id_snpid-raw_requested_snpids').val(snpids.join(', '));
}

function snpid_window_search_demo(){
  $('#id_snpid_window-snpid').val('rs755632525');
}

function fill_in_pvalues(){
    var prefix = "#id_";
    var cutoff_for_all = 0.05;
    $(prefix + 'pvalue_rank_cutoff').val(cutoff_for_all);
    $(prefix + 'pvalue_snp_cutoff').val(cutoff_for_all);
    $(prefix + 'pvalue_ref_cutoff').val(cutoff_for_all);
}

function check_all_degeneracy_levels(){
   $("#id_ic_filter_0")[0].checked = true;
   $("#id_ic_filter_1")[0].checked = true;
   $("#id_ic_filter_2")[0].checked = true;
   $("#id_ic_filter_3")[0].checked = true;
}

/* No defaults are provided for sort order; you get results no matter what you do.*/
