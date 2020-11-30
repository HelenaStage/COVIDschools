from matplotlib import pyplot as plt
plt.rcParams.update({'font.size': 12})
import pandas
import datetime

norway = pandas.read_csv('norway_data.csv', parse_dates=True, dayfirst=True)
NOr = pandas.read_csv('NO.csv')
NOr_ub = pandas.read_csv('NO-ub.csv')
NOr_lb = pandas.read_csv('NO-lb.csv')
dates = norway['Dates']
NO_sch_dates = [dates[19], dates[26], dates[40]]
NO_other_dates = [dates[0], dates[7], dates[36], dates[41]]

fig = plt.figure(figsize=(15,8))
ax = fig.gca()

# sp1
plt.subplot(121)
plt.plot(norway['Dates'], norway['Confirmed'], "x:", lw=2, label='Observed cases')
plt.text(.25, -4.75, 'NO-B4', rotation=0, color='k', alpha=0.5)
plt.text(7.25, 3.75, 'NO-B5', rotation=0, color='k', alpha=0.5)
plt.text(19.25, 15.75, 'NO-S2', rotation=0, color='k', alpha=0.5)
plt.text(19.25, 9.75, 'NO-G5', rotation=0, color='k', alpha=0.5)
plt.text(26.25, 1.25, 'NO-S3', rotation=0, color='k', alpha=0.5)
plt.text(26.25, -4.75, 'NO-R1', rotation=0, color='k', alpha=0.5)
plt.text(36.25, 1.25, 'NO-P1', rotation=0, color='k', alpha=0.5)
plt.text(36.25, -4.75, 'NO-G6', rotation=0, color='k', alpha=0.5)
plt.text(40.25, 55.75, 'NO-S4', rotation=0, color='k', alpha=0.5)
plt.text(40.25, 49.75, 'NO-P2', rotation=0, color='k', alpha=0.5)
plt.text(41.25, 38.75, 'NO-B6', rotation=0, color='k', alpha=0.5)
for intv in NO_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in NO_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Daily cases')
plt.legend

# sp2
plt.subplot(122)
plt.plot(norway['Dates'], NOr['V1'], "-", lw=3, label='Observed cases')
plt.plot(norway['Dates'], NOr_lb['V1'], "b:", color='dodgerblue', lw=1)
plt.plot(norway['Dates'], NOr_ub['V1'], "b:",color='dodgerblue', lw=1)
plt.text(.25, -.077, 'NO-B4', rotation=0, color='k', alpha=0.5)
plt.text(7.25, -.0735, 'NO-B5', rotation=0, color='k', alpha=0.5)
plt.text(19.25, -.0685, 'NO-S2', rotation=0, color='k', alpha=0.5)
plt.text(19.25, -.071, 'NO-G5', rotation=0, color='k', alpha=0.5)
plt.text(26.25, -.0745, 'NO-S3', rotation=0, color='k', alpha=0.5)
plt.text(26.25, -.077, 'NO-R1', rotation=0, color='k', alpha=0.5)
plt.text(36.25, -.0745, 'NO-P1', rotation=0, color='k', alpha=0.5)
plt.text(36.25, -.077, 'NO-G6', rotation=0, color='k', alpha=0.5)
plt.text(40.25, -.061, 'NO-S4', rotation=0, color='k', alpha=0.5)
plt.text(40.25, -.0635, 'NO-P2', rotation=0, color='k', alpha=0.5)
plt.text(41.25, -.0685, 'NO-B6', rotation=0, color='k', alpha=0.5)
plt.fill_between(norway['Dates'], NOr['V1'], NOr_lb['V1'], facecolor='dodgerblue', alpha=0.25,)
plt.fill_between(norway['Dates'], NOr['V1'], NOr_ub['V1'], facecolor='dodgerblue', alpha=0.25,)
for intv in NO_sch_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2)
for intv in NO_other_dates:
    plt.axvline(x=intv, linewidth=2, color='k', alpha=0.2, linestyle=':')
#plt.ylim(-0.06,-0.035)
plt.ylim(-0.08,-0.01)
plt.xticks(ticks=dates[::7], labels=dates[::7], rotation=45, ha='right')
#plt.xlabel('Date')
plt.ylabel('Instantaneous growth rate')
plt.legend

#plt.show()
plt.tight_layout()
plt.savefig("Norway-notes.pdf")
