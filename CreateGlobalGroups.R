library(zonator)

#***********************************************************
# This script is intended for groupwise examination of the global analysis 
# results. The group IDs have been creates as a combination of a two things: Taxon (1:9)
# and IUCN Category (1:9). The script creates 
# - a taxon based result table based on the first number in the group code
# - a IUCN category based result table based on the latter number in the group code
# - a combination of these. 


# MODIFY THESE; 
# Set according to your local system and the variant you want to examine
root.path <- "C://TUULI/Artikkelit/GPAN_Expansion/ZOutput" # Replace with the correct root path 
zvariant.nro <- 2 # Replace with the correct variant number. 

# NOTE: You can list the variants and numbers with this: 
#zonation.project <- create_zproject(root.path)
#names(zonation.project)
  

zonation.project <- create_zproject(root.path)
zvariant <- get_variant(zonation.project, zvariant.nro)
zresults <- results(zvariant)
variantnames  <- names(zonation.project)
outputname  <- variantnames[zvariant.nro]



zcurves <- curves(zresults)
all.spp.data <- sppdata(zvariant)

#******************************************************
# BUILD GROUP WISE CURVES FILES FROM SPP

#Collect only spp name and group name to a df
spp_groups = all.spp.data[, 7:8]


#Function to identify groups to be examined

calc.col.stats <- function(taxon=NULL, category=NULL){
  
  if (is.null(taxon) && is.null(category)) {
    stop("Must provide either!")
  }
  if (!is.null(taxon)  && is.null(category)) {
    grp.name <- paste0("taxon", taxon)
    query <- paste0("^", taxon)
  }
  if (is.null(taxon)  && !is.null(category)) {
    grp.name <- paste0("category", category)
    query <- paste0(category, "$")
  }
  if (!is.null(taxon) && !is.null(category)) {
    grp.name <- paste0("group", taxon, category)
    query  <- paste0(taxon, category)
  }
  
  inds <- grepl(query, spp_groups$group)
  sub_spp_groups <- spp_groups[inds,]
  
  sub_curves = curves(zresults, cols = sub_spp_groups$name)
  sub_stat <- data.frame(stat=rowMeans(sub_curves[,-1]))
  names(sub_stat) <- grp.name

  return(sub_stat)
} 

#identify unique group codes

all.grp.codes <- unique(spp_groups$group)
taxon.codes <- sort(unique(as.numeric(substring(all.grp.codes, 1, 1))))
category.codes <- sort(unique(as.numeric(substring(all.grp.codes, 2, 2))))


#create base for output data frames and rescale pr_lost

taxon.stats <- data.frame(pr_lost=seq(1, 0, -(1 / (nrow(zcurves) - 1) )))
category.stats <- data.frame(pr_lost=seq(1, 0, -(1 / (nrow(zcurves) - 1) )))
all.grp.stats <- data.frame(pr_lost=seq(1, 0, -(1 / (nrow(zcurves) - 1) )))

#loop trough all taxon groups and add a column for each 

for (code in taxon.codes) {
  message("Processing taxon ", code)
  taxon.stats <- cbind(taxon.stats, calc.col.stats(taxon=code))
}


#loop trough all IUCN category groups and add a column for each 

for (code in category.codes) {
  message("Processing category ", code)
  category.stats <- cbind(category.stats, calc.col.stats(category=code))
}


#loop trough all different groups and add a column for each 

for (code in all.grp.codes) {
  message("Processing category ", code)
  message("taxon ", substring(code, 1, 1))
  message("category ", substring(code, 2, 2))
  all.grp.stats <- cbind(all.grp.stats, calc.col.stats(taxon=substring(code, 1, 1), category=substring(code, 2, 2)))
}

all.grp.stats[1,]

#Write the results to csv files with taxon data and IUCN category data

write.csv(category.stats, paste0(root.path, "/",outputname, "_categorycurves.txt"), row.names=FALSE)
message(paste0(root.path, "/",outputname, "_categorycurves.txt WRITTEN!"))
write.csv(taxon.stats, paste0(root.path,"/", outputname, "_taxoncurves.txt"), row.names=FALSE)
message(paste0(root.path, "/",outputname, "_taxoncurves.txt WRITTEN!"))

write.csv(all.grp.stats, paste0(root.path,"/", outputname, "_allgroupcurves.txt"), row.names=FALSE)
message(paste0(root.path, "/",outputname, "_allgroupcurves.txt WRITTEN!"))

#********************************************************************************
#VISUALISE SOME OF THE RESULTS


library(ggplot2)
library(reshape2)

# Plot the category stats
m.category.stats <- melt(category.stats, id.vars=c("pr_lost"))

p <- ggplot(m.category.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ opts(title = (outputname))

#do the same again to store to a png file
png(paste0(root.path, "/",outputname, "_categorycurves.png"))
p <- ggplot(m.category.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ opts(title = (outputname))
dev.off()

# Plot the taxon  stats
m.taxon.stats <- melt(taxon.stats, id.vars=c("pr_lost"))

p <- ggplot(m.taxon.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ opts(title = (outputname))

#do the same again to store to a png file 
png(paste0(root.path, "/",outputname, "_taxoncurves.png"))
p <- ggplot(m.taxon.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ opts(title = (outputname))
dev.off()

