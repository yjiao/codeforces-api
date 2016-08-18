library(ggplot2)
library(ggrepel)

# read in dataframes
df_activity <- read.table('user_activity.csv', header=T, stringsAsFactors=F, sep=',', comment.char='', quote='"')
df_activity <- df_activity[df_activity$verdict=='OK',]
df_userRating <- read.table('user_rating.csv', header=T, stringsAsFactors=F, sep=',', comment.char='', quote='"')
df_problemRating <- read.table('problem_ratings.csv', header=T, stringsAsFactors=F, sep=',', comment.char='', quote='"')
df_problemData <- read.table('problem_data.csv', header=T, stringsAsFactors=F, sep=',', comment.char='', quote='"')

# create tags dataframe
trim <- function (x) gsub("^\\s+|\\s+$", "", x)
df_tags <- df_problemData
idx <- sapply(df_problemData$tags, nchar) > 2
df_tags <- df_tags[idx,]

dflist <- lapply(1:nrow(df_tags), function(idx){
    row <- df_tags[idx,]
    x <- row$tags
    x <- gsub('\\[', '', x)
    x <- gsub('\\]', '', x)
    x <- strsplit(x, ',')
    tags <- sapply(x, trim)
    data.frame(contestID=row$contestID, problemID=row$problemID, tags=tags)
})

df_tags <- do.call(rbind, dflist)

# merge problem ratings with user activity
cols <- names(df_activity)
names(df_activity)[cols=='problem_index'] <- 'problemID'
df_activity <- merge(df_activity, df_problemRating)

# reformatting dfs
df_userRating$date <- as.Date(as.POSIXct(df_userRating$ratingUpdateTimeSeconds, origin="1970-01-01"),
                                             origin="1970-01-01")

df_activity$size <- (df_activity$verdict == 'OK') + 1
df_activity$shape <-'SUCCESS' 
df_activity$shape[df_activity$verdict != 'OK'] <-'FAIL' 
df_activity$shape <- factor(df_activity$shape, levels=c('SUCCESS', 'FAIL'))
df_activity$participantType <- factor(df_activity$participantType, 
                                     levels=c('CONTESTANT', 'VIRTUAL', 'PRACTICE', 'GYM', 'OUT_OF_COMPETITION'))
df_activity <- as.data.frame(df_activity)
df_activity$date <- as.POSIXct.numeric(df_activity$startTimeSeconds,origin="1970-01-01")

maxcontest <- tapply(1:nrow(df_activity), df_activity$contestID, function(idx){
    df <- df_activity[idx,c('startTimeSeconds', 'verdict', 'problemRating', 'participantType', 'size', 'shape')]
    df <- df[df$verdict == 'OK' & df$participantType=='CONTESTANT',]
    df[df$problemRating == max(df$problemRating),][1,]
})


maxcontest <- do.call(rbind, maxcontest)
maxpractice <- tapply(1:nrow(df_activity), df_activity$contestID, function(idx){
    df <- df_activity[idx,c('startTimeSeconds', 'verdict', 'problemRating', 'participantType', 'size', 'shape')]
    df <- df[df$verdict == 'OK' & df$participantType!='CONTESTANT',]
    df[df$problemRating == max(df$problemRating),][1,]
})
maxpractice <- do.call(rbind, maxpractice)
maxcontest <- rbind(maxcontest, maxpractice)

color_scale <- c('CONTESTANT' = '#EA2E49',
                 'VIRTUAL' = '#F7BC20',
                 'PRACTICE' = '#0063A1',
                 'GYM' = '#EBC4FF',
                 'OUT_OF_COMPETITION' = '#919191')

# plotting parameters
img_width = 1000
blank_theme <- theme(
        #axis.line.y = element_blank(),
        #axis.line.x = element_blank(),
        #panel.grid.major = element_blank(),
        #panel.grid.minor = element_blank(),
        #panel.border = element_blank(),
        #panel.background = element_blank(),
        #axis.ticks.y = element_blank(),
        title = element_text(size=15),
        axis.text.y = element_text(size = 12),
        axis.text.x = element_text(size = 12),
        #axis.title.y = element_blank(),
        legend.text = element_text(size=14),
        legend.title = element_text(size=14),
        legend.key.size = unit(1, "cm")) 
xaxis_breaks <- seq(min(df_activity$date), max(df_activity$date), length.out = 10)
xaxis_labs <- format(xaxis_breaks, "%Y %b")
bgalpha = .2

## User progress
# split the df into 5000 and those below 5000 to make plots easier
c <- ggplot() + 
    annotate("rect", ymin=1200, ymax=1399, xmin=-Inf, xmax=Inf, color=NA, fill='green', alpha=bgalpha) +
    annotate("rect", ymin=1400, ymax=1599, xmin=-Inf, xmax=Inf, color=NA, fill='#30DBCA', alpha=bgalpha) +
    annotate("rect", ymin=1600, ymax=1899, xmin=-Inf, xmax=Inf, color=NA, fill='#3094DB', alpha=bgalpha) +
    annotate("rect", ymin=1900, ymax=2199, xmin=-Inf, xmax=Inf, color=NA, fill='#B930DB', alpha=bgalpha) +
    annotate("rect", ymin=2200, ymax=2299, xmin=-Inf, xmax=Inf, color=NA, fill='#FFEA4D', alpha=bgalpha) +
    annotate("rect", ymin=2300, ymax=2399, xmin=-Inf, xmax=Inf, color=NA, fill='#FFBF00', alpha=bgalpha) +
    annotate("rect", ymin=2400, ymax=2599, xmin=-Inf, xmax=Inf, color=NA, fill='#FF7E61', alpha=bgalpha) +
    annotate("rect", ymin=2600, ymax=2899, xmin=-Inf, xmax=Inf, color=NA, fill='#FF4117', alpha=bgalpha) +
    annotate("rect", ymin=2900, ymax=Inf, xmin=-Inf, xmax=Inf, color=NA, fill='#CC0000', alpha=bgalpha) +
    geom_point(data = df_activity[df_activity$problemRating<5000,],
               aes(x=startTimeSeconds, y = problemRating, 
               color=participantType, size=size, shape=shape, fill=participantType), alpha=.5) + 
    geom_point(data = df_userRating, aes(x=ratingUpdateTimeSeconds, y = newRating), alpha=1, size = 5) + 
    geom_line(data = df_userRating, aes(x=ratingUpdateTimeSeconds, y = newRating), alpha=1, size = .5) + 
    #scale_y_continuous(limits=c(1000, 5000)) + 
    scale_x_continuous(breaks=as.numeric(xaxis_breaks), labels=xaxis_labs, limits=c(min(xaxis_breaks), max(xaxis_breaks))) + 
    blank_theme +
    theme(legend.position = 'bottom',
	plot.margin = unit(c(0,0,0,0), "cm"),
	panel.margin = unit(c(0,0,0,0), "cm")
    ) +
    guides(size = FALSE) +
    guides(colour = guide_legend(override.aes = list(size=5))) +
    guides(shape = guide_legend(override.aes = list(size=5))) +
    scale_color_manual(values = color_scale) +
    scale_size(range=c(1,4)) +
    scale_alpha(range=c(0,1)) +
    scale_shape_manual(values=c('SUCCESS' = 16, "FAIL" = 2)) + 
    labs(x = '', y='')

d <- ggplot() + 
    annotate("rect", ymin=-Inf, ymax=Inf, xmin=-Inf, xmax=Inf, color=NA, fill='#CC0000', alpha=bgalpha) +
    geom_point(data = df_activity[df_activity$problemRating==5000,],
               aes(x=startTimeSeconds, y = problemRating, 
               color=participantType, size=size, shape=shape, fill=participantType), alpha=.5) + 
    scale_y_continuous(limits=c(4999, 5001), breaks=5000, labels=5000) + 
    scale_x_continuous(breaks=as.numeric(xaxis_breaks), labels=xaxis_labs, limits=c(min(xaxis_breaks), max(xaxis_breaks))) + 
    blank_theme +
    theme(legend.position = 'None',
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        panel.border = element_blank(),
        panel.background = element_blank(),
        axis.ticks = element_blank(),
        axis.text = element_text(color='white'),
	plot.margin = unit(c(0,0,0,0), "cm"),
	panel.margin = unit(c(0,0,0,0), "cm")
    ) +
    guides(size = FALSE) +
    guides(colour = guide_legend(override.aes = list(size=5))) +
    guides(shape = guide_legend(override.aes = list(size=5))) +
    scale_color_manual(values = color_scale) +
    scale_size(range=c(1,4)) +
    scale_alpha(range=c(0,1)) +
    scale_shape_manual(values=c('SUCCESS' = 16, "FAIL" = 2)) + 
    labs(x = '', y='')

# print figures
png(paste('img_userProgress.png', sep=''), width=img_width, height=400)
print(c)
dev.off()

png(paste('img_userProgress_upper.png', sep=''), width=img_width, height=50)
print(d)
dev.off()



## Histogram of problem ratings solved
cutoffs <- c(-Inf, 1200, 1400, 1600, 1900, 2200, 2300, 2400, 2600, 2900, Inf)
df_tags <- merge(df_activity, df_tags, all=TRUE)
df_tags <- df_tags[!is.na(df_tags$author),]
df_tags$color <- cut(df_tags$problemRating, cutoffs)
color_rating <- c(
'gray',
'#7AE856', 
'#30DBCA',
'#3094DB',
'#B930DB',
'#FFEA4D',
'#FFBF00',
'#FF7E61',
'#FF4117',
'#CC0000'
)

e <- ggplot(df_tags) +
    geom_histogram(aes(x=problemRating, fill=color), color=NA, bins=80) +
    facet_wrap(~participantType, ncol=1) +
    scale_fill_manual(values=color_rating) +
    theme(legend.position='bottom')
png('img_histogram.png', width=600, height=600)
print(e)
dev.off()


## problem ratings by tag
df_labels <- aggregate(problemRating ~ tags , df_tags, function(i) round(mean(i)))

f <- ggplot(df_tags, aes(x=tags, y=problemRating)) +
    geom_boxplot(outlier.size = 0) +
    geom_jitter(aes(color=color), size=.2, width=.8) +
    scale_color_manual(values=color_rating) +
    theme(legend.position='none',
	axis.text.x = element_text(angle=45, vjust=1, hjust=1)
    ) +
    geom_text(data = df_labels, aes(x=tags, y=800, label = problemRating), size=3.5)

png('img_tags.png', width=1200, height=600)
print(f)
dev.off()

## Problems solved over time
nweeks <- difftime(max(df_activity$date), min(df_activity$date), units='weeks')

g <- ggplot(df_activity) +
    geom_freqpoly(aes(x=date), bins=nweeks/4) +
    labs(x='Date', y='Problems solved')

png('img_timeTrend.png', width=800, height=400)
print(g)
dev.off()










