function setupSearchDemos(){
    $("#shared-controls-search-demo").click(function(e){
        e.preventDefault();
        var id_of_active_form = $("div.tab-pane.panel-body.active").attr('id');
        var pval_rank_for_demo = '0.05';
        switch(id_of_active_form){
        case 'snpid_search_form':
            snpid_search_demo();
            break;
        case 'gl_region_search_form':
            gl_region_search_demo();
            break;
        case 'tf_search_form':
            trans_factor_search_demo();
            pval_rank_for_demo = '0.000005';
            break;
        case 'snpid_window_form':  
            snpid_window_search_demo();
            break;
        case 'gene_name_form':
            gene_name_search_demo();
            break;
        }
        fill_in_pvalues(pval_rank_for_demo, '', '');
        check_all_degeneracy_levels();
    });
  
    /* add an onclick handler */
    setup_gain_and_loss_demos();
}


function set_one_cutoff_operator_button(which_button, operator){
    var target = $("button[name='"+ which_button + "']");
    target.attr('value', operator);
    if (operator == 'lte'){ target.text("\u2264"); }
    else if ( operator == 'gt' ){ target.text("\u003E"); }
}

function setup_loss_or_gain(condition){
      var snp_cutoff = condition['pval_snp']['cutoff'];
      var snp_operator = condition['pval_snp']['operator'];
      var ref_cutoff = condition['pval_ref']['cutoff'];
      var ref_operator = condition['pval_ref']['operator'];
      set_one_cutoff_operator_button('pvalue_snp', snp_operator);
      set_one_cutoff_operator_button('pvalue_ref', ref_operator);
      writeBothCutoffDirections();
      fill_in_pvalues('0.05', snp_cutoff, ref_cutoff);
}

function setup_gain_and_loss_demos(){
    console.log("setting up gain and loss demos");
    gain_and_loss = JSON.parse($("#gain_and_loss").text());
    $("#set_gain").click(function(e){
      e.preventDefault();
      setup_loss_or_gain(gain_and_loss['gain']);
    });
    $("#set_loss").click(function(e){
      e.preventDefault();
      setup_loss_or_gain(gain_and_loss['loss']);
    });
}


function trans_factor_search_demo(){
   $('#id_trans_factor-trans_factor').val('ZNF263'); 
   console.log("do not diable what can just be hidden.");
   //$('#id_trans_factor-encode_trans_factor').attr('disabled', 'disabled');
   //$("#id_trans_factor-trans_factor").removeAttr('disabled');
   $('#id_trans_factor-tf_library_0').prop('checked', true);
   $('#id_trans_factor-tf_library_1').removeAttr('checked'); 
}

function gene_name_search_demo(){
   $('#id_gene_name-gene_name').val('TRDD1'); 
   $("#id_gene_name-window_size").val(100);
}

function gl_region_search_demo(){
   $('#id_gl_region-gl_start_pos').val(10000); 
   $('#id_gl_region-gl_end_pos').val(11000);
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
  $("#id_snpid_window-window_size").val(100);
}

function fill_in_pvalues(pval_rank, pval_snp, pval_ref){
    var prefix = "#id_";
    //var default_cutoff = 0.05;
    console.log("pval_snp");
    console.log(pval_snp);

    console.log("pval_ref");
    console.log(pval_ref);
    $(prefix + 'pvalue_rank').val(pval_rank);
    $(prefix + 'pvalue_snp').val(pval_snp);
    $(prefix + 'pvalue_ref').val(pval_ref);
}

function check_all_degeneracy_levels(){
   $("#id_ic_filter_0")[0].checked = true;
   $("#id_ic_filter_1")[0].checked = true;
   $("#id_ic_filter_2")[0].checked = true;
   $("#id_ic_filter_3")[0].checked = true;
}

/* No defaults are provided for sort order; you get results no matter what you do.*/
