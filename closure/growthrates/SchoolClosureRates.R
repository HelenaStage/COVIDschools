library(ggplot2)
library(MASS)
library(dplyr)

DataFile <- function(country){
  if(country=="BY"){filename <- "BY.csv"}
  else if(country=="BW"){filename <- "BW.csv"}
  else if(country=="BE"){filename <- "BE.csv"}
  else if(country=="HE"){filename <- "HE.csv"}
  else if(country=="NI"){filename <- "NI.csv"}
  else if(country=="NW"){filename <- "NW.csv"}
  else if(country=="RP"){filename <- "RP.csv"}
  filename
}

FitWindows <- function(country){
  #Selected windows over which fitting happens
  #Lag: lag time, startwindow: day of school closure, peak: peak daily incidence
  windows<- data.frame(lag=0, startwindow=0, peak=0)
  if(country=="BY"){
    windows$lag <- 8
    windows$startwindow <- 11
    windows$peak <- 30
  }
  else if(country=="BW"){
    windows$lag <- 8
    windows$startwindow <- 14
    windows$peak <- 24
  }
  else if(country=="BE"){
    windows$lag <- 10
    windows$startwindow <- 14
    windows$peak <- 23
  }
  else if(country=="HE"){
    windows$lag <- 7
    windows$startwindow <- 11
    windows$peak <- 29
  }
  else if(country=="NI"){
    windows$lag <- 7
    windows$startwindow <- 11
    windows$peak <- 23
  }
  else if(country=="NW"){
    windows$lag <- 6
    windows$startwindow <- 11
    windows$peak <- 30
  }
  else if(country=="RP"){
    windows$lag <- 7
    windows$startwindow <- 11
    windows$peak <- 24
  }
  windows
}

DoWRate <- function(raw, country, FE='None', meth="ML", splinemeth='bs', lagscale=0.25, plt=TRUE){
  #By default, the fit goes over as many data points as the length of the raw data, but N can be changed here as desired
  tmp <- raw$Confirmed
  tmp1 <- raw$Projection[c(1:(FitWindows(country)$peak+10))]
  startdate <- "2020-03-03"
  inverse.timescale <- 10
  N <- inverse.timescale*length(tmp)
  N1 <- inverse.timescale*length(tmp1)
  #Prepare data structures
  rates<- data.frame(rate=rep(0,N),rateub=rep(0,N),ratelb=rep(0,N))
  rates1<- data.frame(rate=rep(0,N1),rateub=rep(0,N1),ratelb=rep(0,N1))
  ndays <- seq(1,length(tmp),1)
  ndays1 <- seq(1,length(tmp1),1)
  #Time t
  dt<-seq(min(ndays),max(ndays), length=N)
  dt1<-seq(min(ndays1),max(ndays1), length=N1)
  #Time t + epsilon
  epsilon <- 1e-7
  dteps <- seq(min(ndays),max(ndays), length=N) + epsilon
  dteps1 <- seq(min(ndays1),max(ndays1), length=N1) + epsilon
  newdayseps <- data.frame(ndays=dteps)
  newdayseps1 <- data.frame(ndays1=dteps1)
  
  GAMfit <- gam(tmp~s(ndays), family=nb())
  GAMfit1 <- gam(tmp1~s(ndays1), family=nb())
  #Define GAM function with fixed effect for weekends
  if(FE=='None'){
    GAMfit <- gam(tmp~s(ndays, bs=splinemeth), family=nb(), method=meth)
    GAMfit1 <- gam(tmp1~s(ndays1, bs=splinemeth), family=nb(), method=meth)
  }else{
    DW <- weekdays(as.Date(ndays, origin = startdate))
    DW1 <- weekdays(as.Date(ndays1, origin = startdate))
    if(FE=='WE'){
      DW <- ifelse(DW=='Sunday','WE',ifelse(DW=='Saturday','WE','WD'))
      DW1 <- ifelse(DW1=='Sunday','WE',ifelse(DW1=='Saturday','WE','WD'))
    }
    GAMfit <- gam(tmp~s(ndays, bs=splinemeth) + DW, family=nb(), method=meth)
    GAMfit1 <- gam(tmp1~s(ndays1, bs=splinemeth) + DW1, family=nb(), method=meth)
  }
  #gam.check(GAMfit)
  
  #Define data structure with day-of-week effect
  if(FE=='None'){
    newdays <- data.frame(ndays=dt)
    newdays1 <- data.frame(ndays1=dt1)
  }else{
    dow <- weekdays(as.Date(dt, origin = startdate))
    dow1 <- weekdays(as.Date(dt1, origin = startdate))
    if(FE=='WE'){
      dow <- ifelse(dow=='Sunday','WE',ifelse(dow=='Saturday','WE','WD'))
      dow1 <- ifelse(dow1=='Sunday','WE',ifelse(dow1=='Saturday','WE','WD'))
    }
    newdays <- data.frame(ndays=dt, DW=dow)
    newdays1 <- data.frame(ndays1=dt1, DW1=dow1)
  }
  #Estimated fits for times t
  Fitt <- predict(GAMfit, newdays, type="lpmatrix")
  Fitt1 <- predict(GAMfit1, newdays1, type="lpmatrix")
  
  #Define data structure with day-of-week effect at time t + epsilon
  if(FE=='None'){
    newdayseps <- data.frame(ndays=dteps)
    newdayseps1 <- data.frame(ndays1=dteps1)
  }else{
    dow <- weekdays(as.Date(dteps, origin = startdate))
    dow1 <- weekdays(as.Date(dteps1, origin = startdate))
    if(FE=='WE'){
      dow <- ifelse(dow=='Sunday','WE',ifelse(dow=='Saturday','WE','WD'))
      dow1 <- ifelse(dow1=='Sunday','WE',ifelse(dow1=='Saturday','WE','WD'))
    }
    newdayseps <- data.frame(ndays=dteps, DW=dow)
    newdayseps1 <- data.frame(ndays1=dteps1, DW1=dow1)
  }
  #Estimated fits for times t + epsilon
  Fitteps <- predict(GAMfit, newdayseps, type="lpmatrix")
  Fitteps1 <- predict(GAMfit1, newdayseps1, type="lpmatrix")
  
  #Approximation of the derivative of the fit. This derivative will give us the instantaneous rate.
  Grad <- (Fitteps-Fitt)/epsilon
  Grad1 <- (Fitteps1-Fitt1)/epsilon
  #Apply the GAM fit to the raw derivatives to smooth them out
  rateval <- Grad%*%coef(GAMfit)
  rateval1 <- Grad1%*%coef(GAMfit1)
  #Multiply our rates by the GAM covariance matrix to obtain the variance of the rates
  #Square root to determine the standard deviation
  rateval.stdev <- sqrt(rowSums(Grad%*%GAMfit$Vp*Grad))
  rateval1.stdev <- sqrt(rowSums(Grad1%*%GAMfit1$Vp*Grad1))
  
  #Save the rate and confidence intervals
  rates$rate <- rateval
  rates$rateub <- rateval+2*rateval.stdev
  rates$ratelb <- rateval-2*rateval.stdev
  rates1$rate <- rateval1
  rates1$rateub <- rateval1+2*rateval1.stdev
  rates1$ratelb <- rateval1-2*rateval1.stdev
  
  #Calculate the fit windows for the GAM rates
  datawindows <- FitWindows(country)
  #Find the time steps these correspond to for the smoothed timesteps
  times <- data.frame(closetime=0, postresptime=0)
  instrates <- data.frame(pre=0, prelb=0, preub=0, post=0, postlb=0, postub=0, modpost=0, modpostlb=0, modpostub=0)
  instdouble <- data.frame(pre=0, prelb=0, preub=0, post=0, postlb=0, postub=0, modpost=0, modpostlb=0, modpostub=0)
  timevals <- data.frame(t_c=0, t_post=0)
  times$closetime <- min(which(dteps >= datawindows$startwindow))
  timevals$t_c <- dteps[times$closetime]
  times$postresptime <- min(which(dteps >= datawindows$startwindow + datawindows$lag))
  timevals$t_post <- dteps[times$postresptime]
  print(datawindows)
  print(timevals)
  #Determine the instantaneous rates at the time of school closure and response time
  instrates$pre <- rates$rate[times$closetime]
  instrates$prelb <- rates$ratelb[times$closetime]
  instrates$preub <- rates$rateub[times$closetime]
  instrates$post <- rates$rate[times$postresptime]
  instrates$postlb <- rates$ratelb[times$postresptime]
  instrates$postub <- rates$rateub[times$postresptime]
  instrates$modpost <- rates1$rate[times$postresptime]
  instrates$modpostlb <- rates1$ratelb[times$postresptime]
  instrates$modpostub <- rates1$rateub[times$postresptime]
  instdouble$pre <- log(2)/instrates$pre
  instdouble$prelb <- log(2)/instrates$preub
  instdouble$preub <- log(2)/instrates$prelb
  instdouble$post <- log(2)/instrates$post
  instdouble$postlb <- log(2)/instrates$postub
  instdouble$postub <- log(2)/instrates$postlb
  instdouble$modpost <- log(2)/instrates$modpost
  instdouble$modpostlb <- log(2)/instrates$modpostub
  instdouble$modpostub <- log(2)/instrates$modpostlb
  print("Instantaneous rates")
  print(instrates)
  print("Improvement to growth rate")
  print(1-rates$rate[times$postresptime]/rates1$rate[times$postresptime])
  print(1-rates$ratelb[times$postresptime]/rates1$rateub[times$postresptime])
  print(1-rates$rateub[times$postresptime]/rates1$ratelb[times$postresptime])
  print("Doubling times")
  print(instdouble)
  
  if(plt==TRUE){
    
    par(mfrow=c(1,2))
    plot(as.Date(ndays, origin = startdate), tmp, ylab='Cases', xlab='', ylim=range(c(1.5*max(tmp),0)))
    points(as.Date(ndays1, origin = startdate), tmp1, col="red")
    
    p <- predict(GAMfit, type = "link", se.fit = TRUE)
    upr <- p$fit + (2 * p$se.fit)
    lwr <- p$fit - (2 * p$se.fit)
    upr <- GAMfit$family$linkinv(upr)
    lwr <- GAMfit$family$linkinv(lwr)
    p1 <- predict(GAMfit1, type = "link", se.fit = TRUE)
    upr1 <- p1$fit + (2 * p1$se.fit)
    lwr1 <- p1$fit - (2 * p1$se.fit)
    upr1 <- GAMfit1$family$linkinv(upr1)
    lwr1 <- GAMfit1$family$linkinv(lwr1)
    lines(as.Date(ndays, origin = startdate), GAMfit$family$linkinv(p$fit), col=1)
    lines(as.Date(ndays, origin = startdate), upr, col=1, lty=2)
    lines(as.Date(ndays, origin = startdate), lwr, col=1, lty=2)
    lines(as.Date(ndays1, origin = startdate), GAMfit1$family$linkinv(p1$fit), col="red")
    lines(as.Date(ndays1, origin = startdate), upr1, col="red", lty=2)
    lines(as.Date(ndays1, origin = startdate), lwr1, col="red", lty=2)
    
    plot(as.Date(dteps, origin = startdate),rateval,type="l",ylim=range(c(rateval+2*rateval.stdev,rateval-2*rateval.stdev)), ylab='Instantaneous growth rate', xlab='')
    lines(as.Date(dteps, origin = startdate),rateval+2*rateval.stdev,lty=2)
    lines(as.Date(dteps, origin = startdate),rateval-2*rateval.stdev,lty=2)
    lines(as.Date(dteps1, origin = startdate),rateval1,type="l",col="red")
    lines(as.Date(dteps1, origin = startdate),rateval1+2*rateval1.stdev,lty=2,col="red")
    lines(as.Date(dteps1, origin = startdate),rateval1-2*rateval1.stdev,lty=2,col="red")
  }
  
}


#Choose which German state to analyse: Baden-Wurttemberg (BW), Bavaria (BY), Berlin (BE)
#     Hesse (HE), Lower Saxony (NI), North Rhine-Westphalia (NW), Rhineland-Palatinate (RP)
CountryCode <- "BW"
InputData<-data.frame(read.csv(DataFile(CountryCode)))
#Call functions which determines the growth rates...toggle if want to print doubling times instead
DoWRate(InputData,CountryCode,FE="WE",splinemeth = 'tp')
