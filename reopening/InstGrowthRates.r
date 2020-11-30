library(mgcv)

DataFile <- function(country){
  if(country=="DK"){filename <- "denmark_data.csv"}
  else if(country=="DKcase"){filename <- "denmark_cases.csv"}
  else if(country=="NO"){filename <- "norway_data.csv"}
  else if(country=="DE"){filename <- "germany_data_hosp.csv"}
  else if(country=="DEstaff"){filename <- "germany_data_raw.csv"}
  else if(country=="DEstudents"){filename <- "germany_data_raw.csv"}
  filename
}

GrowthRate <- function(raw, country, FE='None', meth="ML", splinemeth='bs', plotfig=TRUE, printrates=TRUE){
  startdate <- "2020-04-01"#raw$Dates[1]
  if(country=="DK"){raw <- raw$Hospital}
  else if(country=="DKcase"){raw <- raw$Confirmed}
  else if(country=="NO"){raw <- raw$Confirmed}
  else if(country=="DE"){raw <- raw$Hospital}
  else if(country=="DEstaff"){raw <- raw$Staff}
  else if(country=="DEstudents"){raw <- raw$Students}
  #By default, the fit goes over as many data points as the length of the raw data, but N can bee changed here is desired
  N <- length(raw)
  
  #Prepare data structures
  rates<- data.frame(rate=rep(0,N),rateub=rep(0,N),ratelb=rep(0,N))
  ndays <- seq(1,length(raw),1)
  #Time t
  dt<-seq(1,length(raw), length=N)
  newdays <- data.frame(ndays=dt)
  #Time t + epsilon
  epsilon <- 1e-7
  dteps <- seq(1,length(raw), length=N) + epsilon
  newdayseps <- data.frame(ndays=dteps)
  
  #Define GAM function
  GAMfit <- gam(raw~s(ndays), family=nb())
  #Define GAM function with fixed effect for weekends
  if(FE=='None'){
    GAMfit <- gam(raw~s(ndays, bs=splinemeth), family=nb(), method=meth)
  }else{
    DW <- weekdays(as.Date(ndays, origin = startdate))
    if(FE=='WE'){
      DW <- ifelse(DW=='Sunday','WE',ifelse(DW=='Saturday','WE','WD'))
    }
    GAMfit <- gam(raw~s(ndays, bs=splinemeth) + DW, family=nb(), method=meth)
  }
  #gam.check(GAMfit)
  
  #Define data structure with day-of-week effect
  if(FE=='None'){
    newdays <- data.frame(ndays=dt)
  }else{
    dow <- weekdays(as.Date(dt, origin = startdate))
    if(FE=='WE'){
      dow <- ifelse(dow=='Sunday','WE',ifelse(dow=='Saturday','WE','WD'))
    }
    newdays <- data.frame(ndays=dt, DW=dow)
  }
  #Estimated fits for times t
  Fitt <- predict(GAMfit, newdays, type="lpmatrix")
  
  #Define data structure with day-of-week effect at time t + epsilon
  if(FE=='None'){
    newdayseps <- data.frame(ndays=dteps)
  }else{
    dow <- weekdays(as.Date(dteps, origin = startdate))
    if(FE=='WE'){
      dow <- ifelse(dow=='Sunday','WE',ifelse(dow=='Saturday','WE','WD'))
    }
    newdayseps <- data.frame(ndays=dteps, DW=dow)
  }
  #Estimated fits for times (t, t+epsilon)
  Fitteps <- predict(GAMfit, newdayseps, type="lpmatrix")
  
  #Approximation of the derivative of the fit. This derivative will give us the instantaneous rate.
  Grad <- (Fitteps-Fitt)/epsilon
  #Apply the GAM fit to the raw derivatives to smooth them out
  rateval <- Grad%*%coef(GAMfit)
  #Multiply our rates by the GAM covariance matrix to obtain the variance of the rates
  #Square root to determine the standard deviation
  rateval.stdev <- sqrt(rowSums(Grad%*%GAMfit$Vp*Grad))
  
  #Save the mean and confidence intervals
  rates$rate <- rateval
  rates$rateub <- rateval+2*rateval.stdev
  rates$ratelb <- rateval-2*rateval.stdev
  
  par(mfrow=c(1,2))
  plot(as.Date(ndays, origin = startdate), raw, ylab='Cases', xlab='', ylim=range(c(1.5*max(raw),0)))
  
  p <- predict(GAMfit, type = "link", se.fit = TRUE)
  upr <- p$fit + (2 * p$se.fit)
  lwr <- p$fit - (2 * p$se.fit)
  upr <- GAMfit$family$linkinv(upr)
  lwr <- GAMfit$family$linkinv(lwr)
  lines(as.Date(ndays, origin = startdate), GAMfit$family$linkinv(p$fit), col=1)
  lines(as.Date(ndays, origin = startdate), upr, col=1, lty=2)
  lines(as.Date(ndays, origin = startdate), lwr, col=1, lty=2)
  
  plot(as.Date(dteps, origin = startdate),rateval,type="l",ylim=range(c(rateval+2*rateval.stdev,rateval-2*rateval.stdev)), ylab='Instantaneous growth rate', xlab='')
  lines(as.Date(dteps, origin = startdate),rateval+2*rateval.stdev,lty=2)
  lines(as.Date(dteps, origin = startdate),rateval-2*rateval.stdev,lty=2)
  
  if(printrates==TRUE){
    if(country=="DK"){
      write.csv(rates$rate, 'DK.csv')
      write.csv(rates$rateub, 'DK-ub.csv')
      write.csv(rates$ratelb, 'DK-lb.csv')
    }
    else if(country=="DKcase"){
      write.csv(rates$rate, 'DKcases.csv')
      write.csv(rates$rateub, 'DKcases-ub.csv')
      write.csv(rates$ratelb, 'DKcases-lb.csv')
    }
    else if(country=="NO"){
      write.csv(rates$rate, 'NO.csv')
      write.csv(rates$rateub, 'NO-ub.csv')
      write.csv(rates$ratelb, 'NO-lb.csv')
    }
    else if(country=="DE"){
      write.csv(rates$rate, 'DE.csv')
      write.csv(rates$rateub, 'DE-ub.csv')
      write.csv(rates$ratelb, 'DE-lb.csv')
    }
    else if(country=="DEstaff"){
      write.csv(rates$rate, 'DEstaff.csv')
      write.csv(rates$rateub, 'DEstaff-ub.csv')
      write.csv(rates$ratelb, 'DEstaff-lb.csv')
    }
    else if(country=="DEstudents"){
      write.csv(rates$rate, 'DEstudents.csv')
      write.csv(rates$rateub, 'DEstudents-ub.csv')
      write.csv(rates$ratelb, 'DEstudents-lb.csv')
    }
  }
}

#Choose which country to analyse (DK, DKcase, NO, DE, DEstaff, or DEstudents):
CountryCode <- "DEstudents"
InputData<-data.frame(read.csv(DataFile(CountryCode)))
#Toggle printrates if you want to save the instantaneous growth rates
#Evaluates the instantaneous growth rate
GrowthRate(InputData, CountryCode, printrates=TRUE, FE="WD", splinemeth = 'tp')
#These growth rates are visualised in Python (see other enclosed scripts)


