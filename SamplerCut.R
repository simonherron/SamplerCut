piano <- read.csv("/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv")
piano$Index <- 1:579
write.csv(piano, file = "/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv", quote = F)
piano <- piano[,-8]


# start: 4850300
# middle: 179382000
# middle_2: 169459000
# end: 515675250
# mistake: (407706000)



testAmps <- read.csv("/Users/simonherron/Documents/Sampler/output200.csv")
testV <- testAmps$Amp
plot(testV)

output <- c()
coolDown <- 0
# prevSection <- testV[1]
for(i in 5:length(testV)) {
  if (coolDown > 0) {
    coolDown <- coolDown - 1
  } else {
    if (testV[i] > 0.0005 
        && (testV[i] > (testV[i-5] * 4)) 
        && all(testV[i:(i+15)] > (testV[i - 5] * 2))) {
          output <- c(output, i)
          coolDown <- 20
    }
  }
  # prevSection <- testV[i]
}

abline(v = output, col = "red", lty = 3)
print(length(output))


plot(testV[0:1000])
abline(v = output, col = "red", lty = 3)
