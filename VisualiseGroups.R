#***********************************************************
# This script is intended for drawing the gruop curves for the 
# curves files created with CreateGlobalGroups.R
#***********************************************************

# Required libraries
library(ggplot2)
library(reshape2)


# Basic settings (MODIFY: patch and variant number)
root.path <- "C://TUULI/Artikkelit/GPAN_Expansion/Zoutput/GroupedResults"
taxoncurves <- list.files(root.path,pattern = "_taxoncurves.txt$")
categorycurves <- list.files(root.path, pattern = "_categorycurves.txt$")
message(paste0("number of variants found", length(taxoncurves)))

i = 1 # number of variant to be analysed (would be good to do all, but loops dont work with PNG)


#for (i in 1:length(taxoncurves)){     #Tried to do loops but did't work!
message(paste0("reading taxons ", taxoncurves[i]))
variant.name <- taxoncurves[i]
taxon.stats <-  read.csv(taxoncurves[i], header = TRUE, sep=",")

# Plot the taxon  stats
m.taxon.stats <- melt(taxon.stats, id.vars=c("pr_lost"))
p <- ggplot(m.taxon.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ labs(title = (variant.name))

#do the same again to store to a png file 

png(paste0(root.path, "/",variant.name, "_taxoncurves.png"))
p <- ggplot(m.taxon.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ labs(title = (variant.name))
graphics.off()


message(paste0("reading categories ", categorycurves[i]))
variant.name <- categorycurves[i]
category.stats <-  read.csv(categorycurves[i], header = TRUE, sep=",")

# Plot the category stats
m.category.stats <- melt(category.stats, id.vars=c("pr_lost"))

p <- ggplot(m.category.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ labs(title = (variant.name))

#do the same again to store to a png file
png(paste0(root.path, "/",variant.name, "_categorycurves.png"))
p <- ggplot(m.category.stats, aes(x=pr_lost, y=value, color=variable))
p + geom_line(size=1) + theme_bw()+ ylim(0, 1)+ labs(title = (variant.name))
dev.off()

  
#}
