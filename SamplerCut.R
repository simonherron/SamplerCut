piano <- read.csv("/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv")
piano$Index <- 1:579
write.csv(piano, file = "/Users/simonherron/Documents/Sampler/Piano/PianoNoPedal.csv", quote = F)
piano <- piano[,-8]

# veryStart: 0
# start: 4850300
# middle: 179382000
# middle_2: 169459000
# end: 515675250
# endMistake: 513292709
# mistake: (407706000)



testAmps <- read.csv("/Users/simonherron/Documents/Sampler/outputEnd200.csv")
testV <- testAmps$Amp
plot(testV, ylim = c(0, 0.004))

output <- c()
noise <- c()
coolDown <- 0

for(i in 5:length(testV)) {
  if (coolDown > 0) {
    coolDown <- coolDown - 1
  } else {
    if (testV[i] > 0.0005) {
      if (testV[i] > (testV[i-5] * 4)) {
        if (all(testV[i:(i+15)] > (testV[i - 5] * 2))) {
          if (all(testV[i:(i+5)] > min(testV[(i-5):i]) * 4)) {
            output <- c(output, i)
            coolDown <- 20
          }
        } 
      }
    }
  }
}



# else if (all(testV[i] > c(testV[(i-20):(i-1)], testV[(i+1):(i+20)]))) {
#     noise <- c(noise, i)
#     coolDown <- 20 
# }

abline(v = output, col = "red", lty = 3)
# abline(v = noise, col = "blue", lty = 3)
print(length(output))

target <- 12117
adj <- target - 14
end <- target + 20
toTry <- testV[adj:end]
plot(toTry, ylim=c(0, 0.0015))
abline(v = output - adj + 1, col = "red", lty = 3)
abline(v = target - adj + 1 + 15, lty = 3)
abline(v = target - adj + 1 - 5, lty = 3)


theVal <- testV[target - 5] * 2
segments(x0 = target - adj + 1, x1 = 50, y0 = theVal, lty = 3)
  

# legend("topright", legend = "y=0.00060486\nVeryStart, #7038")
legend("topright", legend = "y=0.00060674\nEnd, #18")

