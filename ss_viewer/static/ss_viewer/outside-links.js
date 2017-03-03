console.log("loaded outside-plots.js");
//this would be factored out into a js file that is shared between the main search page and detail view.
function dbSNPLink(snpid){
    var link = "<a href='https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=" + snpid + "'>";
    link += snpid + '</a>';
    console.log("link " + link);
    return link;
}

//returns a link to factor book for this transcription factor if it's availble, otherwise,
//just returns a text value.
function factorbookLink(t_factor){
  //JASPAR transcription factors available from Factorbook:
  var fbFactors = ["ELK1" ,"RELA" ,"TBP" ,"BRCA1" ,"CTCF" ,"GABPA" ,"REST" ,"ESR1" ,"ARID3A" ,"NFIC" ,"CREB1" ,"CEBPB" ,"E2F4" ,"E2F6" ,"ELF1" ,"FOS" ,"FOSL1" ,"FOSL2" ,"HNF4G" ,"HSF1" ,"JUN" ,"JUND" ,"MAFF" ,"MAFK" ,"MEF2C" ,"NFYB" ,"NR2C2" ,"NRF1" ,"POU2F2" ,"PRDM1" ,"RFX5" ,"SP2" ,"TCF7L2" ,"USF2" ,"ZBTB33" ,"ZNF263" ,"E2F1" ,"EBF1" ,"EGR1" ,"ELK4" ,"FOXA1" ,"GATA2" ,"GATA3" ,"HNF4A" ,"IRF1" ,"MAX" ,"MEF2A" ,"NFYA" ,"PAX5" ,"SP1" ,"SRF" ,"STAT1" ,"STAT3" ,"USF1" ,"YY1" ,"ZEB1" ,"ESRRA" ,"FOXP2" ,"SREBF1" ,"SREBF2" ,"THAP1" ,"NR3C1"];

  if ( fbFactors.indexOf(t_factor) === -1 ){
      return t_factor; //JASPAR TF not represented in FactorBook
                       //return only text for this value.
  }
   var link = '<a href="http://www.factorbook.org/human/chipseq/tf/' + t_factor + '">';
   link += t_factor + '</a>';
   return link;
}
