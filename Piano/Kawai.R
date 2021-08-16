library(tidyverse)

dta <- read.csv("/Users/simonherron/Google Drive/In/Kawai/KawaiDur.csv", stringsAsFactors = F, skip = 1, header = T, nrows = 10)

plot(dta$MIDI.Pitch, dta$pp, col = "purple", ylim = c(0, 60))
points(dta$MIDI.Pitch, dta$mf, col = "green", lty = 1)
points(dta$MIDI.Pitch, dta$f, col = "red")

partA <- dta[1:3, ]
partB <- tail(dta, -2)

modA <- lm(pp ~ MIDI.Pitch, data = partA)
modB <- lm(pp ~ MIDI.Pitch, data = partB)
curve(modA$coefficients[2] * x + modA$coefficients[1], add = T, to = 40) 
curve(modB$coefficients[2] * x + modB$coefficients[1], add = T, from = 40) 

modAmf <- lm(mf ~ MIDI.Pitch, data = partA)
modBmf <- lm(mf ~ MIDI.Pitch, data = partB)
curve(modAmf$coefficients[2] * x + modAmf$coefficients[1], add = T, to = 40) 
curve(modBmf$coefficients[2] * x + modBmf$coefficients[1], add = T, from = 40)



testD <- dta %>% select(MIDI.Pitch, pp)
theMod <- glm(MIDI.Pitch ~ pp, data = testD, family = "binomial")




f <- function(x) {
  if (x < 40) {
    return(modA$coefficients[2] * x + modA$coefficients[1])
  } else {
    return(modB$coefficients[2] * x + modB$coefficients[1])
  }
}

rsum <- function(f, a, b, h = 10e-5) {
  if(a > b) {
    h <- -1*h
  }
  s <- seq(a, b, h)
  vals <- unlist(lapply(s, f))
  return(
    sum(vals)*h
  )
}
