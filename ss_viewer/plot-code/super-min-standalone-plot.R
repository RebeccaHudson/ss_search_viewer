library(RSQLite)
library(DBI)
#   library(data.table)


#we have python code that connects to a database and passes
# an rpy2 DataFrame into this code.   
# (in python:  'from rpy2.robjects.vectors import DataFrame')
handle_python_params <- function(tmpfile, motif_lib_ref){
  #md <- motif_match_data_from_python
  #print("this is being called")
  #converted_to_table <- data.table(md)
  #setkey(converted_to_table, snpid)
  #print(class(converted_to_table))
  #print(converted_to_table)
  #ct <- converted_to_table

  #print(paste("dim(ct)", dim(ct)))
  #print(names(ct))
 
  #print(paste("class(ct[[1]])", class(ct[[1]])))
  #print(paste("ct[[1]]", ct[[1]]))
  #print(paste("ct[1]", ct[1]))
 
  print(paste('name of tempfile', tmpfile))
  db_driver <- dbDriver("SQLite")
  open_db <- dbConnect(db_driver, tmpfile) 
  simple_query <- 'select * from dmm_table_motif_unknown;'
  results <- dbSendQuery(open_db, simple_query)
  results <- fetch(results)
  library(data.table)
  to_use <- data.table(results)
  setkey(to_use, snpid)
  print(paste("to use: ", to_use))
  print(to_use$snpid)
 # ml <- motif_lib_ref
 # print("\nmotif library?")
 # print(class(ml))  
 # print(length(motif_lib_ref))
 # #does motif library reference sill come through?
 # #what do I have to do with it now? 
 # print(ml[[1]])
   fname <- makeJustOnePlot(to_use, 6, motif_lib_ref)
 # print(paste("filename: ", fname))
  return('not quite yet')
}



#used to get file names for the plots to output
#motif library label could be parametrized in a more sophisticated way.
#(we should know somewhere higher up the chain what the motif_library is)
getFileNameForPlot <- function(motif_match_dt, motif_library_label){
   snpid <- motif_match_dt$snpid
   motif <- motif_match_dt$motif
   fname <- (paste(snpid, motif, motif_library_label, 'svg', sep="."))
   print(paste("fname : ", fname))
   return(fname)
}


#This has been pulled out for benchmaking purposes. 
#Covers making the plot from creating the svg file to saving it.
makeJustOnePlot <- function(plot_making_params, i  ,motif.lib){ 
  print("makeJustOnePlot...")
  outfile_name <- paste("output_plots", getFileNameForPlot(plot_making_params, 'jaspar'), sep="/")
  print(paste("Creating plot", i, "in file:", outfile_name, sep = " "))
  svg(outfile_name)
  plotMotifMatchQuickly(plot_making_params,  motif.lib)
  dev.off()
  return(outfile_name) 
}
#looking for a file with an 'outlist' of motif match data tables,
#as produced by dtMotifMatch




# Note: previous documentation for this method moved below it for readability.
#'quickly', because instead of creating motif.match.dt in here, we read it out of a file. 
# Intended for separate use from the rest of the atSNP package.
plotMotifMatchQuickly <- function(motif.match.dt, motif.lib ,cex.main = 2, ...) {
# Checks disabled to try to speed this up.
#if (class(snpid) != "character" | length(snpid)!=1) {
#    stop("snpid must be a character")
#  }
#  if (class(motif) != "character" | length(motif)!=1) {
#    stop("motif must be a character")
#  }
#  if(sum(! motif %in% names(motif.lib)) > 0) {
#    stop("Error: The motif is not included in 'motif.lib'.")
#  }

#the first part to be disabled.
#motif.match.dt <- dtMotifMatch(snp.tbl, motif.scores, snpid, motif, ncores = 1, motif.lib = motif.lib)  
  ref_aug_match_seq_forward = motif.match.dt['ref_aug_match_seq_forward']   
  snp_aug_match_seq_reverse = motif.match.dt['snp_aug_match_seq_reverse']   
  #can some of this be prepocessed as well? 
  ##Convert ACGT to 1234
  #try to move this block into preprocessing? 
  codes <- seq(4)
  names(codes) <- c("A", "C", "G", "T")
  print("first code assignment")
  ref_aug_match_seq_forward_code <- codes[strsplit(motif.match.dt[,ref_aug_match_seq_forward], "")[[1]]]
  ref_aug_match_seq_reverse_code <- codes[strsplit(motif.match.dt[,ref_aug_match_seq_reverse], "")[[1]]]
  print("after second code assn")
  snp_aug_match_seq_forward_code <- codes[strsplit(motif.match.dt[,snp_aug_match_seq_forward], "")[[1]]]
  snp_aug_match_seq_reverse_code <- codes[strsplit(motif.match.dt[,snp_aug_match_seq_reverse], "")[[1]]]
  
  ##Convert 1234 to (1000)(0100)(0010)(0001)
  codes.vec <- diag(4)
  rownames(codes.vec) <- c("A", "C", "G", "T")
  ref_aug_match_pwm_forward<- mapply(function(i) codes.vec[,i], as.list(ref_aug_match_seq_forward_code))
  ref_aug_match_pwm_reverse<- mapply(function(i) codes.vec[,i], as.list(ref_aug_match_seq_reverse_code))
  snp_aug_match_pwm_forward<- mapply(function(i) codes.vec[,i], as.list(snp_aug_match_seq_forward_code))
  snp_aug_match_pwm_reverse<- mapply(function(i) codes.vec[,i], as.list(snp_aug_match_seq_reverse_code))
  
  ##(3,2) to Augmented PWM: ___PWM__
  ref_aug_pwm <- cbind(matrix(0, 4, motif.match.dt[, ref_extra_pwm_left]), t(get(motif.match.dt[, motif], motif.lib)), matrix(0, 4, motif.match.dt[, ref_extra_pwm_right]))
  rownames(ref_aug_pwm) <- c("A", "C", "G", "T")
  snp_aug_pwm <- cbind(matrix(0, 4, motif.match.dt[, snp_extra_pwm_left]), t(get(motif.match.dt[, motif], motif.lib)), matrix(0, 4, motif.match.dt[, snp_extra_pwm_right]))
  rownames(snp_aug_pwm) <- c("A", "C", "G", "T")

  snp_loc <- motif.match.dt$ref_location
  revert.columns <- function(mat) {
    mat[, rev(seq(ncol(mat)))]
  }

  ref_aug_match_pwm<-ref_aug_match_pwm_forward
  snp_aug_match_pwm<-snp_aug_match_pwm_forward

  if(motif.match.dt$ref_strand == "-") {
    ref_aug_pwm <- revert.columns(ref_aug_pwm)
    snp_loc <- ncol(ref_aug_match_pwm_forward) - 1 - snp_loc
    ref_aug_match_pwm<-ref_aug_match_pwm_reverse
  }
  if(motif.match.dt$snp_strand == "-") {
    snp_aug_pwm <- revert.columns(snp_aug_pwm)
    snp_aug_match_pwm<-snp_aug_match_pwm_reverse
  }

 #actual graphics commands appear to begin here.
  par(mfrow=c(4,1), oma=c(1,1,4,1))
  par(mar=c(1.5, 3, 4, 2))
  plotMotifLogo(pcm2pfm(ref_aug_pwm), "Best match to the reference genome", yaxis=FALSE, xaxis=FALSE, xlab="", ylab="PWM", ...)
if(motif.match.dt$ref_strand=='+') {
arrows((min(which(colSums(ref_aug_pwm)!=0))-1)/ncol(ref_aug_pwm), -0.17, max(which(colSums(ref_aug_pwm)!=0))/ncol(ref_aug_pwm), -0.17, length = 0.1, angle = 15, code = 2, col = "blue", lwd = 1.5, xpd=NA)
  mtext("5'", 1, adj=(min(which(colSums(ref_aug_pwm)!=0))-1)/ncol(ref_aug_pwm), padj=1, col="blue", cex=1) 
  mtext("3'", 1, adj=max(which(colSums(ref_aug_pwm)!=0))/ncol(ref_aug_pwm), padj=1, col="blue", cex=1)
} else {
arrows(max(which(colSums(ref_aug_pwm)!=0))/ncol(ref_aug_pwm), -0.17, (min(which(colSums(ref_aug_pwm)!=0))-1)/ncol(ref_aug_pwm), -0.17, length = 0.1, angle = 15, code = 2, col = "blue", lwd = 1.5, xpd=NA)
  mtext("5'", 1, adj=max(which(colSums(ref_aug_pwm)!=0))/ncol(ref_aug_pwm), padj=1, col="blue", cex=1) 
  mtext("3'", 1, adj=(min(which(colSums(ref_aug_pwm)!=0))-1)/ncol(ref_aug_pwm), padj=1, col="blue", cex=1) 
}
  par(mar = c(4, 3, 1.5, 2))
plotMotifLogo(pcm2pfm(ref_aug_match_pwm), font="mono,Courier", yaxis=FALSE, xlab="", ylab=paste("(", motif.match.dt$ref_strand, ")", sep=""), ...)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 0, motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 1, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments((motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 0, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 0, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 0, col="blue", lty=3, lwd=2)
  if(motif.match.dt$ref_strand=="+")   {
  mtext("5'", 1,  adj=0, padj=1, col="blue", cex=1) 
  mtext("3'", 1,  adj=1, padj=1, col="blue", cex=1)
} else {
  mtext("3'", 1, adj=0, padj=1, col="blue", cex=1) 
  mtext("5'", 1, adj=1, padj=1, col="blue", cex=1) 
  }
par(mar=c(1.5, 3, 4, 2))      
plotMotifLogo(pcm2pfm(snp_aug_match_pwm), "Best match to the SNP genome", font="mono,Courier", yaxis=FALSE, xlab="", ylab=paste("(", motif.match.dt$snp_strand, ")", sep=""), ...)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 0, motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 1, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments((motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 0, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 1, col="blue", lty=3, lwd=2)
segments(motif.match.dt[,snp_loc]/motif.match.dt[,snp_ref_length], 0, (motif.match.dt[,snp_loc]+1)/motif.match.dt[,snp_ref_length], 0, col="blue", lty=3, lwd=2)
  if(motif.match.dt$snp_strand=="+")   {
  mtext("5'", 1,  adj=0, padj=1, col="blue", cex=1) 
  mtext("3'", 1,  adj=1, padj=1, col="blue", cex=1)
} else {
  mtext("3'", 1, adj=0, padj=1, col="blue", cex=1) 
  mtext("5'", 1, adj=1, padj=1, col="blue", cex=1) 
  }
par(mar=c(4, 3, 1.5, 2))
plotMotifLogo(pcm2pfm(snp_aug_pwm), yaxis=FALSE, xaxis=FALSE, xlab="", ylab="PWM", ...)
if(motif.match.dt$snp_strand=='+') {
arrows((min(which(colSums(snp_aug_pwm)!=0))-1)/ncol(snp_aug_pwm), -0.17, max(which(colSums(snp_aug_pwm)!=0))/ncol(snp_aug_pwm), -0.17, length = 0.1, angle = 15, code = 2, col = "blue", lwd = 1.5, xpd=NA)
  mtext("5'", 1, adj=(min(which(colSums(snp_aug_pwm)!=0))-1)/ncol(snp_aug_pwm), padj=1, col="blue", cex=1) 
  mtext("3'", 1, adj=max(which(colSums(snp_aug_pwm)!=0))/ncol(snp_aug_pwm), padj=1, col="blue", cex=1)
} else {
arrows(max(which(colSums(snp_aug_pwm)!=0))/ncol(snp_aug_pwm), -0.17, (min(which(colSums(snp_aug_pwm)!=0))-1)/ncol(snp_aug_pwm), -0.17, length = 0.1, angle = 15, code = 2, col = "blue", lwd = 1.5, xpd=NA)
  mtext("5'", 1, adj=max(which(colSums(snp_aug_pwm)!=0))/ncol(snp_aug_pwm), padj=1, col="blue", cex=1) 
  mtext("3'", 1, adj=(min(which(colSums(snp_aug_pwm)!=0))-1)/ncol(snp_aug_pwm), padj=1, col="blue", cex=1)
}
title(main=paste(motif.match.dt[,motif], " Motif Scan for ", motif.match.dt[,snpid], sep=""), outer=TRUE, cex.main=cex.main)
#title(main=paste(motif.match.dt[,motif], " Motif Scan for ", motif.match.dt[,snpid], sep=""), outer=TRUE, cex.main=2)
}

.find_reverse <- function(sequence) {
  if(length(sequence) > 0) {
    codes <- seq(4)
    names(codes) <- c("A", "C", "G", "T")
    return(paste(names(codes)[5 - codes[strsplit(sequence, split = "")[[1]]]], collapse = ""))
  }
}



#' @name plotMotifMatch
#' @title Plot sequence logos of the position weight matrix of the motif and sequences of its corresponding best matching augmented subsequence on the reference and SNP allele.
#' @description Plot the best matching augmented subsequences on the reference and SNP alleles. Plot sequence logos of the position weight matrix of the motif to the corresponding positions of the best matching subsequences on the references and SNP alleles.
#' @param snp.tbl A data.table with the following information:
#' \tabular{cc}{
#' snpid \tab SNP id.\cr
#' ref_seq \tab Reference allele nucleobase sequence.\cr
#' snp_seq \tab SNP allele nucleobase sequence.\cr
#' ref_seq_rev \tab Reference allele nucleobase sequence on the reverse strand.\cr
#' snp_seq_rev \tab SNP allele nucleobase sequence on the reverse strand.\cr}
#' @param motif.scores A data.table with the following information:
#' \tabular{cc}{
#' motif \tab Name of the motif.\cr
#' motif_len \tab Length of the motif.\cr
#' ref_start, ref_end, ref_strand \tab Location of the best matching subsequence on the reference allele.\cr
#' snp_start, snp_end, snp_strand \tab Location of the best matching subsequence on the SNP allele.\cr
#' log_lik_ref \tab Log-likelihood score for the reference allele.\cr
#' log_lik_snp \tab Log-likelihood score for the SNP allele.\cr
#' log_lik_ratio \tab The log-likelihood ratio.\cr
#' log_enhance_odds \tab Difference in log-likelihood ratio between SNP allele and reference allele based on the best matching subsequence on the reference allele.\cr
#' log_reduce_odds \tab Difference in log-likelihood ratio between reference allele and SNP allele based on the best matching subsequence on the SNP allele.\cr
#' }
#' @param snpid A snpid to plot the sequences on the reference and SNP alleles
#' @param motif A motif to match the sequences with its position weight matrix
#' @param motif.lib A list of position weight matrices
#' @param cex.main The size of the main title.
#' @param ... Other parameters passed to plotMotifLogo.
#' @return Sequence logo stacks: Reference subsequences, sequence logo of reference allele matching potision weight matrix, SNP subsequences, sequence logo of SNP allele matching potision weight matrix
#' @author Sunyoung Shin\email{shin@@stat.wisc.edu}
#' @examples
#' data(example)
#' plotMotifMatch(motif_scores$snp.tbl, motif_scores$motif.scores, motif_scores$snp.tbl$snpid[1], motif_scores$motif.scores$motif[1], motif.lib = motif_library)
#' @import data.table motifStack
#' @export
