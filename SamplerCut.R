piano <- read.csv("/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv")
piano$Index <- 1:579
write.csv(piano, file = "/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv", quote = F)
piano <- piano[,-8]



testAmps <- read.csv("/Users/simonherron/Documents/Sampler/outputMiddle2.csv")
testV <- testAmps$Amp
# plot(testV[18500:20000])
plot(testV)

output <- c()
coolDown <- 0
# prevSection <- testV[1]
for(i in 5:length(testV)) {
  if (coolDown > 0) {
    coolDown <- coolDown - 1
  } else {
    if (testV[i] > 0.0005 && (testV[i] > (testV[i-4] * 4)) && (testV[i + 2] > (testV[i - 4] * 2))) {
      output <- c(output, i)
      coolDown <- 20
    }
  }
  # prevSection <- testV[i]
}

abline(v = output, col = "red", lty = 3)
print(length(output))
